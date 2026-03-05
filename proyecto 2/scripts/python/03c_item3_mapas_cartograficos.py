#!/usr/bin/env python3
"""MP2 Ítem 3: mapas climatológicos finales sobre fondo cartográfico.

Genera:
- 03_item3_presion_isobaras_viento_cartografico.png
- 03_item3_temperatura_cartografico.png
"""

from pathlib import Path
from urllib.request import urlopen
import ssl
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

LON_MIN, LON_MAX = -76.5, -75.0
LAT_MIN, LAT_MAX = 4.0, 5.5

def download_basemap(out_path: Path) -> None:
    url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/export"
        f"?bbox={LON_MIN},{LAT_MIN},{LON_MAX},{LAT_MAX}"
        "&bboxSR=4326&imageSR=4326&size=2200,1600&format=png&f=image"
    )
    ctx = ssl._create_unverified_context()
    with urlopen(url, context=ctx, timeout=30) as r:
        out_path.write_bytes(r.read())


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    ds = xr.open_dataset(root / "data/raw/era5_surface_monthly_1996_2025.nc")
    tdim = "time" if "time" in ds.dims else "valid_time"

    sp = (ds["sp"] / 100.0).mean(tdim, skipna=True)  # hPa
    t2m = (ds["t2m"] - 273.15).mean(tdim, skipna=True)  # C
    u10 = ds["u10"].mean(tdim, skipna=True)
    v10 = ds["v10"].mean(tdim, skipna=True)

    lon = sp["longitude"].values
    lat = sp["latitude"].values

    plots = root / "results/plots"
    plots.mkdir(parents=True, exist_ok=True)

    basemap = plots / "03_item3_basemap_cartografico.png"
    out_p = plots / "03_item3_presion_isobaras_viento_cartografico.png"
    out_t = plots / "03_item3_temperatura_cartografico.png"

    download_basemap(basemap)
    img = plt.imread(basemap)

    # Mapa presión + isobaras + viento
    fig, ax = plt.subplots(figsize=(9.2, 7.2))
    ax.imshow(img, extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], origin="upper", zorder=0)

    cf = ax.contourf(lon, lat, sp.values, levels=14, cmap="viridis", alpha=0.42, zorder=2)
    cbar = fig.colorbar(cf, ax=ax, shrink=0.92)
    cbar.set_label("Presión superficial climatológica [hPa]")

    cs = ax.contour(lon, lat, sp.values, levels=9, colors="white", linewidths=1.3, zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%.1f")

    q = ax.quiver(
        lon,
        lat,
        u10.values,
        v10.values,
        color="black",
        scale=8,
        width=0.003,
        zorder=6,
    )
    ax.quiverkey(q, 0.88, -0.07, 1.0, "1 m s$^{-1}$", labelpos="E")

    ax.set_title("Climatología de presión superficial con isobaras y viento a 10 m (1996–2025)")
    ax.set_xlabel("Longitud [°]")
    ax.set_ylabel("Latitud [°]")
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(out_p, dpi=250)
    plt.close(fig)

    # Mapa temperatura por aparte
    fig, ax = plt.subplots(figsize=(9.2, 7.2))
    ax.imshow(img, extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], origin="upper", zorder=0)

    cf = ax.contourf(lon, lat, t2m.values, levels=14, cmap="turbo", alpha=0.43, zorder=2)
    cbar = fig.colorbar(cf, ax=ax, shrink=0.92)
    cbar.set_label("Temperatura 2 m climatológica [°C]")

    cs = ax.contour(lon, lat, t2m.values, levels=8, colors="k", linewidths=0.9, alpha=0.7, zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%.2f")

    ax.set_title("Climatología de temperatura del aire a 2 m (1996–2025)")
    ax.set_xlabel("Longitud [°]")
    ax.set_ylabel("Latitud [°]")
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(out_t, dpi=250)
    plt.close(fig)

    print(f"[OK] {out_p}")
    print(f"[OK] {out_t}")


if __name__ == "__main__":
    main()
