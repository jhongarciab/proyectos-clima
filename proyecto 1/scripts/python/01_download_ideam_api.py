#!/usr/bin/env python3
"""
Download IDEAM datasets from Socrata API already aggregated to DAILY scale.

This version is optimized for long periods (e.g., 10 years) by querying daily
aggregates directly in API (SoQL), instead of downloading raw 5-min observations.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://www.datos.gov.co/resource"
DATASETS = {
    "temperature": "sbwg-7ju4",
    "precipitation": "s54a-sgyg",
    "humidity": "uext-mhny",
}


def build_where(department: str, municipality: str | None, start_date: str, end_date: str) -> str:
    clauses = [f"upper(departamento)='{department.upper()}'"]
    if municipality:
        clauses.append(f"upper(municipio)='{municipality.upper()}'")
    clauses.append(f"fechaobservacion >= '{start_date}T00:00:00'")
    clauses.append(f"fechaobservacion <= '{end_date}T23:59:59'")
    return " AND ".join(clauses)


def make_session(app_token: str | None) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    if app_token:
        session.headers.update({"X-App-Token": app_token})
    return session


def build_select_and_group(var_name: str) -> tuple[str, str]:
    agg = "sum(valorobservado)" if var_name == "precipitation" else "avg(valorobservado)"
    select = (
        "codigoestacion,nombreestacion,departamento,municipio,"
        "date_trunc_ymd(fechaobservacion) as fecha,"
        f"{agg} as valor_diario,"
        "unidadmedida"
    )
    group = "codigoestacion,nombreestacion,departamento,municipio,fecha,unidadmedida"
    return select, group


def fetch_daily_dataset(
    dataset_id: str,
    var_name: str,
    where_clause: str,
    limit: int = 1000,
    sleep_s: float = 2.0,
    max_attempts_per_page: int = 6,
    request_timeout_s: int = 20,
    app_token: str | None = None,
) -> pd.DataFrame:
    rows: List[Dict] = []
    offset = 0
    session = make_session(app_token)
    select, group = build_select_and_group(var_name)

    while True:
        params = {
            "$select": select,
            "$where": where_clause,
            "$group": group,
            "$order": "fecha ASC",
            "$limit": limit,
            "$offset": offset,
        }

        url = f"{BASE_URL}/{dataset_id}.json"
        batch = None
        last_err = None

        for attempt in range(1, max_attempts_per_page + 1):
            try:
                resp = session.get(url, params=params, timeout=request_timeout_s)
                resp.raise_for_status()
                batch = resp.json()
                break
            except Exception as err:
                last_err = err
                wait_s = min(2**attempt, 20)
                print(f"  request failed (attempt {attempt}/{max_attempts_per_page}) offset={offset}: {err}")
                time.sleep(wait_s)

        if batch is None:
            raise RuntimeError(f"Failed to fetch dataset={dataset_id}, offset={offset}") from last_err

        if not batch:
            break

        rows.extend(batch)
        print(f"  fetched {len(batch)} daily rows (offset={offset}) | total so far: {len(rows)}")

        if len(batch) < limit:
            break

        offset += limit
        time.sleep(sleep_s)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["valor_diario"] = pd.to_numeric(df["valor_diario"], errors="coerce")

    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Download IDEAM daily-aggregated datasets via API")
    parser.add_argument("--department", default="RISARALDA")
    parser.add_argument("--municipality", default="PEREIRA", help="Use empty string to skip municipality filter")
    parser.add_argument("--start-date", default="2015-01-01")
    parser.add_argument("--end-date", default="2024-12-31")
    parser.add_argument("--out-dir", default="data/raw")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--max-attempts", type=int, default=6)
    parser.add_argument("--app-token", default="")

    args = parser.parse_args()

    municipality = args.municipality.strip() or None
    where_clause = build_where(args.department, municipality, args.start_date, args.end_date)

    project_root = Path(__file__).resolve().parents[1]
    out_dir_arg = Path(args.out_dir)
    out_dir = out_dir_arg if out_dir_arg.is_absolute() else (project_root / out_dir_arg)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading IDEAM DAILY datasets...")
    print(f"Where: {where_clause}")

    summary = []
    for var_name, dataset_id in DATASETS.items():
        print(f"\n[{var_name}] dataset_id={dataset_id}")
        active_where = where_clause

        df = fetch_daily_dataset(
            dataset_id=dataset_id,
            var_name=var_name,
            where_clause=active_where,
            limit=args.limit,
            request_timeout_s=args.timeout,
            sleep_s=args.sleep,
            max_attempts_per_page=args.max_attempts,
            app_token=(args.app_token.strip() or None),
        )

        # Fallback: precipitation can be sparse/missing at municipality level.
        # If empty and municipality filter was used, retry with department-only.
        if var_name == "precipitation" and municipality and df.empty:
            print("  precipitation returned 0 rows with municipality filter; retrying with department-only filter...")
            active_where = build_where(args.department, None, args.start_date, args.end_date)
            df = fetch_daily_dataset(
                dataset_id=dataset_id,
                var_name=var_name,
                where_clause=active_where,
                limit=args.limit,
                request_timeout_s=args.timeout,
                sleep_s=args.sleep,
                max_attempts_per_page=args.max_attempts,
                app_token=(args.app_token.strip() or None),
            )

        var_dir = out_dir / var_name
        var_dir.mkdir(parents=True, exist_ok=True)

        out_file = var_dir / f"ideam_{var_name}_{args.department.lower()}"
        use_municipality_in_name = municipality and not (var_name == "precipitation" and "upper(municipio)" not in active_where)
        if use_municipality_in_name:
            out_file = Path(str(out_file) + f"_{municipality.lower()}")
        else:
            out_file = Path(str(out_file) + "_all_municipalities")
        out_file = Path(str(out_file) + f"_{args.start_date}_{args.end_date}_daily.csv")

        df.to_csv(out_file, index=False)
        print(f"  saved: {out_file} ({len(df)} rows)")

        summary.append({"variable": var_name, "dataset_id": dataset_id, "rows": len(df), "file": str(out_file)})

    summary_df = pd.DataFrame(summary)
    summary_file = out_dir / f"download_summary_ideam_{args.start_date}_{args.end_date}_daily.csv"
    summary_df.to_csv(summary_file, index=False)

    print("\nDone.")
    print(summary_df)
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()
