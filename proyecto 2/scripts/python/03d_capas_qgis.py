#!/usr/bin/env python3
"""
Ítem 3 — Capas adicionales para QGIS
Exporta:
  - isotermas_temperatura.geojson   (isolíneas de t2m)
  - ciudades.geojson                (puntos de ciudades principales)

Salidas en results/qgis/
"""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Niveles de isolíneas de temperatura
ISOTERMA_LEVELS = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

CIUDADES = {
    "Pereira":   {"lat": 4.8143, "lon": -75.6946, "elevacion_m": 1411},
    "Armenia":   {"lat": 4.5339, "lon": -75.6811, "elevacion_m": 1483},
    "Manizales": {"lat": 5.0703, "lon": -75.5138, "elevacion_m": 2153},
    "Ibagué":    {"lat": 4.4389, "lon": -75.2322, "elevacion_m": 1285},
}


def open_dataset(nc_path: Path) -> xr.Dataset:
    return xr.open_dataset(nc_path)


def time_dim(ds: xr.Dataset) -> str:
    return "valid_time" if "valid_time" in ds.dims else "time"


def export_isotermas(ds: xr.Dataset, out_path: Path) -> None:
    tdim = time_dim(ds)
    t2m = (ds["t2m"] - 273.15).mean(tdim, skipna=True)
    lon = ds["longitude"].values
    lat = ds["latitude"].values

    t_min, t_max = float(t2m.min()), float(t2m.max())
    levels = [lv for lv in ISOTERMA_LEVELS if t_min <= lv <= t_max]

    fig, ax = plt.subplots()
    cs = ax.contour(lon, lat, t2m.values, levels=levels)

    features = []
    for i, level in enumerate(cs.levels):
        for seg in cs.allsegs[i]:
            if len(seg) < 2:
                continue
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[float(c[0]), float(c[1])] for c in seg],
                },
                "properties": {
                    "temperatura_C": round(float(level), 1),
                    "label": f"{level:.0f} °C",
                },
            })
    plt.close(fig)

    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }
    out_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    print(f"[OK] Isotermas: {out_path.name}  "
          f"({len(features)} segmentos, niveles: {levels})")


def export_ciudades(out_path: Path) -> None:
    features = []
    for nombre, info in CIUDADES.items():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [info["lon"], info["lat"]],
            },
            "properties": {
                "nombre":       nombre,
                "elevacion_m":  info["elevacion_m"],
                "label":        f"{nombre} ({info['elevacion_m']} m)",
            },
        })

    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }
    out_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    print(f"[OK] Ciudades: {out_path.name}  ({len(features)} puntos)")


def main() -> None:
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    in_nc   = project_root / "data" / "raw" / "era5_surface_monthly_1996_2025.nc"
    out_dir = project_root / "results" / "qgis"
    out_dir.mkdir(parents=True, exist_ok=True)

    ds = open_dataset(in_nc)

    export_isotermas(ds, out_dir / "isotermas_temperatura.geojson")
    export_ciudades(out_dir / "ciudades.geojson")

    print(f"\n[OK] Archivos listos en: {out_dir}")
    print("     Cargar en QGIS: Capa > Agregar capa > Capa vectorial")


if __name__ == "__main__":
    main()