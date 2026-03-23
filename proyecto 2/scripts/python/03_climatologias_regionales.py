#!/usr/bin/env python3
"""
Ítem 3 — Exportación a GeoTIFF para QGIS
Genera un GeoTIFF por variable climatológica (promedio 1996-2025):
  - t2m  : Temperatura 2 m [°C]
  - sp   : Presión superficial [hPa]
  - u10  : Viento zonal 10 m [m/s]
  - v10  : Viento meridional 10 m [m/s]
  - ws10 : Rapidez del viento [m/s]
  - isolineas_presion : GeoJSON con isobaras (para capa vectorial en QGIS)

Salidas (en results/qgis/):
  - t2m_climatologia.tif
  - sp_climatologia.tif
  - u10_climatologia.tif
  - v10_climatologia.tif
  - ws10_climatologia.tif
  - isobaras_presion.geojson

Requisitos: pip install xarray netCDF4 rasterio numpy
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import xarray as xr

try:
    import rasterio
    from rasterio.crs import CRS
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Falta 'rasterio'. Instálalo con: python3 -m pip install rasterio"
    ) from exc


# ─────────────────────────────────────────
# Configuración de variables a exportar
# ─────────────────────────────────────────
EXPORT_VARS = {
    "t2m":  {"src": "t2m",  "convert": lambda x: x - 273.15, "desc": "Temperatura 2m [C]"},
    "sp":   {"src": "sp",   "convert": lambda x: x / 100.0,  "desc": "Presion superficial [hPa]"},
    "u10":  {"src": "u10",  "convert": lambda x: x,           "desc": "Viento zonal 10m [m/s]"},
    "v10":  {"src": "v10",  "convert": lambda x: x,           "desc": "Viento meridional 10m [m/s]"},
}

# Niveles de isobaras a exportar como vectores
ISOBAR_LEVELS = [760, 780, 800, 820, 840, 860, 880, 900]


def open_dataset(nc_path: Path) -> xr.Dataset:
    return xr.open_dataset(nc_path)


def time_dim(ds: xr.Dataset) -> str:
    return "valid_time" if "valid_time" in ds.dims else "time"


def compute_mean_fields(ds: xr.Dataset) -> dict[str, np.ndarray]:
    """Calcula el promedio climatológico multianual de cada variable."""
    tdim = time_dim(ds)
    fields = {}
    for name, meta in EXPORT_VARS.items():
        da = ds[meta["src"]].mean(tdim, skipna=True)
        fields[name] = meta["convert"](da.values)

    # Rapidez del viento derivada
    fields["ws10"] = np.sqrt(fields["u10"] ** 2 + fields["v10"] ** 2)
    return fields


def get_grid(ds: xr.Dataset):
    """Devuelve latitudes (N→S), longitudes (W→E) y el transform rasterio."""
    lat = ds["latitude"].values   # ya viene N→S: [5.5, 5.25, ..., 4.0]
    lon = ds["longitude"].values  # W→E: [-76.5, ..., -75.0]

    # rasterio from_bounds espera (west, south, east, north)
    west, east = float(lon.min()), float(lon.max())
    south, north = float(lat.min()), float(lat.max())
    nrows, ncols = len(lat), len(lon)

    # pixel_size
    res_lon = (east  - west)  / (ncols - 1)
    res_lat = (north - south) / (nrows - 1)

    # El transform: origen en la esquina superior-izquierda del primer píxel
    # (west - res/2, north + res/2) con píxel de tamaño res_lon x -res_lat
    transform = rasterio.transform.from_origin(
        west  - res_lon / 2,
        north + res_lat / 2,
        res_lon,
        res_lat,
    )
    return lat, lon, nrows, ncols, transform


def export_geotiffs(fields: dict[str, np.ndarray],
                    nrows: int, ncols: int,
                    transform, out_dir: Path) -> None:
    """Exporta cada campo como GeoTIFF Float32 en WGS84."""
    crs = CRS.from_epsg(4326)
    var_names = list(EXPORT_VARS.keys()) + ["ws10"]

    for name in var_names:
        data = fields[name].astype(np.float32)

        # ERA5: latitudes N→S → el array[0,:] es la fila norte → correcto para rasterio
        out_path = out_dir / f"{name}_climatologia.tif"
        with rasterio.open(
            out_path,
            "w",
            driver="GTiff",
            height=nrows,
            width=ncols,
            count=1,
            dtype="float32",
            crs=crs,
            transform=transform,
            nodata=np.nan,
        ) as dst:
            dst.write(data, 1)
            dst.update_tags(description=EXPORT_VARS.get(name, {}).get("desc", name))

        print(f"[OK] GeoTIFF: {out_path.name}  "
              f"(min={data.min():.3f}, max={data.max():.3f})")


def export_isobars_geojson(fields: dict[str, np.ndarray],
                           lat: np.ndarray, lon: np.ndarray,
                           out_path: Path) -> None:
    """
    Calcula isolíneas de presión con matplotlib y las exporta como GeoJSON
    para cargar en QGIS como capa vectorial de líneas.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sp = fields["sp"]

    # Filtrar niveles que realmente existen en los datos
    sp_min, sp_max = float(sp.min()), float(sp.max())
    levels = [lv for lv in ISOBAR_LEVELS if sp_min <= lv <= sp_max]

    if not levels:
        print("[WARN] Ningún nivel de isobara dentro del rango de datos. "
              f"Rango sp: {sp_min:.1f}–{sp_max:.1f} hPa")
        return

    fig, ax = plt.subplots()
    cs = ax.contour(lon, lat, sp, levels=levels)

    features = []
    for i, level in enumerate(cs.levels):
        for seg in cs.allsegs[i]:
            coords = seg.tolist()
            if len(coords) < 2:
                continue
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[c[0], c[1]] for c in coords],
                },
                "properties": {
                    "presion_hPa": round(float(level), 1),
                    "label": f"{level:.0f} hPa",
                },
            })

    plt.close(fig)

    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }

    out_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    print(f"[OK] GeoJSON isobaras: {out_path.name}  "
          f"({len(features)} segmentos, niveles: {levels})")


def main() -> None:
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    in_nc   = project_root / "data" / "raw" / "era5_surface_monthly_1996_2025.nc"
    out_dir = project_root / "results" / "qgis"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Leyendo NetCDF...")
    ds = open_dataset(in_nc)

    print("[INFO] Calculando campos climatológicos medios...")
    fields = compute_mean_fields(ds)

    lat, lon, nrows, ncols, transform = get_grid(ds)

    print(f"[INFO] Grilla: {nrows}x{ncols} | "
          f"lat [{lat[-1]:.2f}–{lat[0]:.2f}] | "
          f"lon [{lon[0]:.2f}–{lon[-1]:.2f}]")

    print("\n[INFO] Exportando GeoTIFFs...")
    export_geotiffs(fields, nrows, ncols, transform, out_dir)

    print("\n[INFO] Exportando isobaras como GeoJSON...")
    export_isobars_geojson(fields, lat, lon,
                           out_dir / "isobaras_presion.geojson")

    print(f"\n[OK] Todos los archivos en: {out_dir}")
    print("     Carga en QGIS: Capa > Agregar capa > Capa ráster (.tif) / Capa vectorial (.geojson)")


if __name__ == "__main__":
    main()