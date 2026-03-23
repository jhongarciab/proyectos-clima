#!/usr/bin/env python3
"""
Ítem 3 — Exportación de vectores de viento para QGIS
Interpola la grilla ERA5 (7x7) a resolución más fina antes de exportar.

Salida: results/qgis/viento_vectores.geojson
"""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import xarray as xr
from scipy.interpolate import RegularGridInterpolator


# Factor de refinamiento: 3 → pasa de 7x7 a 19x19 puntos
REFINE = 3


def time_dim(ds: xr.Dataset) -> str:
    return "valid_time" if "valid_time" in ds.dims else "time"


def interpolate_field(data: np.ndarray,
                      lat: np.ndarray, lon: np.ndarray,
                      lat_fine: np.ndarray, lon_fine: np.ndarray) -> np.ndarray:
    """Interpolación bilineal de data(lat, lon) a grilla más fina."""
    # RegularGridInterpolator espera lat ascendente
    if lat[0] > lat[-1]:
        interp = RegularGridInterpolator(
            (lat[::-1], lon), data[::-1, :], method="linear"
        )
    else:
        interp = RegularGridInterpolator((lat, lon), data, method="linear")

    lon_g, lat_g = np.meshgrid(lon_fine, lat_fine)
    pts = np.column_stack([lat_g.ravel(), lon_g.ravel()])
    return interp(pts).reshape(len(lat_fine), len(lon_fine))


def main() -> None:
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    in_nc   = project_root / "data" / "raw" / "era5_surface_monthly_1996_2025.nc"
    out_dir = project_root / "results" / "qgis"
    out_dir.mkdir(parents=True, exist_ok=True)

    ds   = xr.open_dataset(in_nc)
    tdim = time_dim(ds)

    u_raw = ds["u10"].mean(tdim, skipna=True).values   # (7,7)
    v_raw = ds["v10"].mean(tdim, skipna=True).values
    lat   = ds["latitude"].values    # N→S: [5.5, ..., 4.0]
    lon   = ds["longitude"].values   # W→E: [-76.5, ..., -75.0]

    # Grilla fina interpolada
    n_lat = (len(lat) - 1) * REFINE + 1
    n_lon = (len(lon) - 1) * REFINE + 1
    lat_fine = np.linspace(lat[-1], lat[0], n_lat)   # ascendente S→N
    lon_fine = np.linspace(lon[0], lon[-1], n_lon)

    u_fine = interpolate_field(u_raw, lat, lon, lat_fine, lon_fine)
    v_fine = interpolate_field(v_raw, lat, lon, lat_fine, lon_fine)

    rapidez   = np.sqrt(u_fine**2 + v_fine**2)
    direccion = (np.degrees(np.arctan2(-u_fine, -v_fine))) % 360

    features = []
    for i, la in enumerate(lat_fine):
        for j, lo in enumerate(lon_fine):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lo), float(la)],
                },
                "properties": {
                    "u_ms":             round(float(u_fine[i, j]), 4),
                    "v_ms":             round(float(v_fine[i, j]), 4),
                    "rapidez_ms":       round(float(rapidez[i, j]), 4),
                    "direccion_grados": round(float(direccion[i, j]), 2),
                    "label":            f"{rapidez[i,j]:.2f} m/s",
                },
            })

    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }

    out_path = out_dir / "viento_vectores.geojson"
    out_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")

    print(f"[OK] Vectores de viento interpolados: {out_path.name}")
    print(f"     Grilla original: {len(lat)}x{len(lon)} → interpolada: {n_lat}x{n_lon}")
    print(f"     {len(features)} puntos | "
          f"rapidez min={rapidez.min():.3f} max={rapidez.max():.3f} m/s")


if __name__ == "__main__":
    main()