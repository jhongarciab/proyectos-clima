#!/usr/bin/env python3
"""Genera mapa base cartográfico del bbox MP2 con etiquetas grandes de ciudades."""

from pathlib import Path
from urllib.request import urlopen
import ssl
import matplotlib.pyplot as plt

LON_MIN, LON_MAX = -76.5, -75.0
LAT_MIN, LAT_MAX = 4.0, 5.5

CITIES = {
    "Pereira": (4.8143, -75.6946),
    "Armenia": (4.5339, -75.6811),
    "Manizales": (5.0703, -75.5138),
    "Ibagué": (4.4389, -75.2322),
    "Dosquebradas": (4.8392, -75.6673),
    "Santa Rosa de Cabal": (4.8681, -75.6214),
    "Chinchiná": (4.9833, -75.6036),
    "Cartago": (4.7464, -75.9117),
}


def download_basemap(out_path: Path) -> None:
    url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/export"
        f"?bbox={LON_MIN},{LAT_MIN},{LON_MAX},{LAT_MAX}"
        "&bboxSR=4326&imageSR=4326&size=2000,1500&format=png&f=image"
    )
    ctx = ssl._create_unverified_context()
    with urlopen(url, context=ctx, timeout=30) as r:
        out_path.write_bytes(r.read())


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    plots = root / "results" / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    basemap = plots / "03_basemap_arcgis_bbox.png"
    out_map = plots / "03_mapa_base_municipios.png"

    download_basemap(basemap)

    img = plt.imread(basemap)
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.imshow(img, extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], origin="upper")

    for name, (lat, lon) in CITIES.items():
        if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX:
            ax.scatter(lon, lat, s=75, c="yellow", edgecolors="black", linewidths=1.0, zorder=3)
            ax.text(
                lon + 0.02,
                lat + 0.015,
                name,
                fontsize=12,
                fontweight="bold",
                color="black",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="black", alpha=0.88),
                zorder=4,
            )

    ax.set_title("Mapa base cartográfico de la región de estudio (MP2)")
    ax.set_xlabel("Longitud [°]")
    ax.set_ylabel("Latitud [°]")
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(out_map, dpi=240)
    plt.close(fig)

    print(f"[OK] {out_map}")


if __name__ == "__main__":
    main()
