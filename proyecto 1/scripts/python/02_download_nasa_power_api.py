#!/usr/bin/env python3
"""
Download daily NASA POWER data for Pereira using the POWER API.

Variables selected for cross-source comparison with IDEAM:
- T2M          : Air temperature at 2 meters (°C)
- PRECTOTCORR  : Precipitation corrected (mm/day)
- RH2M         : Relative humidity at 2 meters (%)

Usage:
  python3 scripts/03_download_nasa_power_api.py \
    --start 20150101 --end 20251231
"""

from __future__ import annotations

import argparse
from pathlib import Path
import requests

API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def build_url(lat: float, lon: float, start: str, end: str) -> str:
    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "CSV",
        "header": "true",
        "time-standard": "UTC",
    }
    req = requests.Request("GET", API_URL, params=params).prepare()
    return req.url


def main() -> None:
    parser = argparse.ArgumentParser(description="Download NASA POWER daily point data")
    parser.add_argument("--lat", type=float, default=4.8143, help="Latitude for Pereira")
    parser.add_argument("--lon", type=float, default=-75.6946, help="Longitude for Pereira")
    parser.add_argument("--start", default="20150101", help="Start date YYYYMMDD")
    parser.add_argument("--end", default="20251231", help="End date YYYYMMDD")
    parser.add_argument("--out-dir", default="data/raw/nasa_power", help="Output directory")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    out_dir = (project_root / args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    url = build_url(args.lat, args.lon, args.start, args.end)
    out_file = out_dir / f"nasa_power_pereira_{args.start}_{args.end}_daily.csv"

    print("Requesting NASA POWER...")
    print(url)

    r = requests.get(url, timeout=120)
    r.raise_for_status()

    out_file.write_bytes(r.content)
    print(f"Saved: {out_file}")


if __name__ == "__main__":
    main()
