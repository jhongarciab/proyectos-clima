#!/usr/bin/env python3
"""
Ítem 2 — Descarga ERA5 de superficie (promedios mensuales)
Región: 4.0–5.5 N, -76.5 a -75.0
Periodo: 1996–2025

Salida:
- data/raw/era5_surface_monthly_1996_2025.nc
- data/raw/era5_surface_request.json

Requisitos:
- pip install cdsapi
- archivo ~/.cdsapirc configurado con URL + key de CDS
"""

from __future__ import annotations

import json
from pathlib import Path

from cdsapi import Client
import importlib.util


def load_config(script_dir: Path):
    cfg_path = script_dir / "00_config_mp2.py"
    spec = importlib.util.spec_from_file_location("config_mp2", cfg_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No fue posible cargar configuración: {cfg_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_cds_credentials() -> None:
    cdsrc = Path.home() / ".cdsapirc"
    if not cdsrc.exists():
        raise FileNotFoundError(
            "No se encontró ~/.cdsapirc. Configura credenciales de Copernicus CDS antes de descargar."
        )


def build_request(cfg) -> dict:
    return {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": cfg.ERA5_SURFACE_VARIABLES,
        "year": cfg.YEARS,
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": cfg.AREA,
    }


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    out_nc = project_root / "data" / "raw" / "era5_surface_monthly_1996_2025.nc"
    out_req = project_root / "data" / "raw" / "era5_surface_request.json"

    assert_cds_credentials()

    cfg = load_config(script_dir)
    req = build_request(cfg)
    out_req.write_text(json.dumps(req, indent=2), encoding="utf-8")

    client = Client()
    dataset = "reanalysis-era5-single-levels-monthly-means"

    print("[INFO] Descargando ERA5 superficie mensual...")
    print(f"[INFO] Dataset: {dataset}")
    print(f"[INFO] Archivo salida: {out_nc}")

    client.retrieve(dataset, req, str(out_nc))

    if not out_nc.exists() or out_nc.stat().st_size == 0:
        raise RuntimeError("La descarga no produjo un NetCDF válido.")

    size_mb = out_nc.stat().st_size / (1024 * 1024)
    print(f"[OK] Descarga completada. Tamaño: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
