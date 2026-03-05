#!/usr/bin/env python3
"""
Ítem 3 — Mini Proyecto 2
Climatologías regionales de superficie ERA5 (1996–2025).

Salidas:
- results/tables/03_climatologia_mensual.csv
- results/plots/03_climatologia_mensual_superficie.png
- results/plots/03_mapa_presion_isobaras_viento.png
- results/plots/03_mapa_temperatura.png
- docs/report/03_item3_climatologias.md
"""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen
import ssl
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

MONTHS = np.arange(1, 13)
MONTH_LABELS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

VAR_META = {
    "t2m": {"label": "Temperatura 2 m", "unit_out": "°C", "convert": lambda x: x - 273.15},
    "sp": {"label": "Presión superficial", "unit_out": "hPa", "convert": lambda x: x / 100.0},
    "u10": {"label": "Viento zonal 10 m (u)", "unit_out": "m s$^{-1}$", "convert": lambda x: x},
    "v10": {"label": "Viento meridional 10 m (v)", "unit_out": "m s$^{-1}$", "convert": lambda x: x},
    "ws10": {"label": "Rapidez del viento 10 m", "unit_out": "m s$^{-1}$", "convert": lambda x: x},
}

CITIES = {
    "Pereira": (4.8143, -75.6946),
    "Armenia": (4.5339, -75.6811),
    "Manizales": (5.0703, -75.5138),
    "Ibagué": (4.4389, -75.2322),
}


def _download_basemap(lon_min: float, lat_min: float, lon_max: float, lat_max: float, out_png: Path) -> Path | None:
    """Descarga fondo de mapa (ArcGIS World Topo) para el bbox en EPSG:4326."""
    url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/export"
        f"?bbox={lon_min},{lat_min},{lon_max},{lat_max}"
        "&bboxSR=4326&imageSR=4326&size=1200,900&format=png&f=image"
    )
    try:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        ctx = ssl._create_unverified_context()
        with urlopen(url, context=ctx, timeout=30) as resp:
            data = resp.read()
        out_png.write_bytes(data)
        return out_png if out_png.exists() and out_png.stat().st_size > 0 else None
    except Exception:
        return None


def _annotate_cities(ax, lon_min: float, lat_min: float, lon_max: float, lat_max: float) -> None:
    for name, (lat, lon) in CITIES.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            ax.scatter(lon, lat, s=65, c="yellow", edgecolors="black", linewidths=0.9, zorder=6)
            ax.text(
                lon + 0.03,
                lat + 0.02,
                name,
                fontsize=11,
                fontweight="bold",
                color="black",
                zorder=7,
                bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="black", alpha=0.85),
            )


def _open_dataset(nc_path: Path) -> xr.Dataset:
    return xr.open_dataset(nc_path)


def _time_dim(ds: xr.Dataset) -> str:
    return "time" if "time" in ds.dims else "valid_time"


def compute_climatology_monthly_regional(ds: xr.Dataset) -> pd.DataFrame:
    rows = []
    tdim = _time_dim(ds)

    lat_weights = np.cos(np.deg2rad(ds["latitude"]))
    lat_weights = lat_weights / lat_weights.mean()

    ws10 = np.sqrt(ds["u10"] ** 2 + ds["v10"] ** 2)

    for var, meta in VAR_META.items():
        da = ws10 if var == "ws10" else ds[var]

        ts_region = da.weighted(lat_weights).mean(dim=("latitude", "longitude"), skipna=True)
        ts_region = meta["convert"](ts_region)

        clim_mean = ts_region.groupby(f"{tdim}.month").mean(tdim, skipna=True)
        clim_std = ts_region.groupby(f"{tdim}.month").std(tdim, skipna=True)

        for m in MONTHS:
            rows.append(
                {
                    "variable": var,
                    "descripcion": meta["label"],
                    "unidad": meta["unit_out"],
                    "month": int(m),
                    "month_name": MONTH_LABELS[m - 1],
                    "clim_mean": float(clim_mean.sel(month=m).item()),
                    "clim_std": float(clim_std.sel(month=m).item()),
                }
            )

    return pd.DataFrame(rows)


def compute_annual_mean_fields(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    """Campo climatológico medio multianual (promedio de todos los meses 1996–2025)."""
    tdim = _time_dim(ds)

    t2m_c = VAR_META["t2m"]["convert"](ds["t2m"])
    sp_hpa = VAR_META["sp"]["convert"](ds["sp"])
    u10 = ds["u10"]
    v10 = ds["v10"]

    return {
        "t2m": t2m_c.mean(tdim, skipna=True),
        "sp": sp_hpa.mean(tdim, skipna=True),
        "u10": u10.mean(tdim, skipna=True),
        "v10": v10.mean(tdim, skipna=True),
    }


def plot_climatology_monthly(df: pd.DataFrame, out_png: Path) -> None:
    vars_to_plot = list(VAR_META.keys())
    n = len(vars_to_plot)
    ncols = 2
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 3.6 * nrows), sharex=True)
    axes = np.array(axes).reshape(-1)

    for ax, var in zip(axes, vars_to_plot):
        d = df[df["variable"] == var].sort_values("month")
        x = d["month"].to_numpy()
        y = d["clim_mean"].to_numpy()
        s = d["clim_std"].to_numpy()

        ax.plot(x, y, lw=2)
        ax.fill_between(x, y - s, y + s, alpha=0.2)
        ax.set_title(f"{VAR_META[var]['label']} [{VAR_META[var]['unit_out']}]")
        ax.set_xticks(MONTHS)
        ax.set_xticklabels(MONTH_LABELS)
        ax.grid(alpha=0.3)

    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle("MP2 — Ítem 3: climatología mensual regional (1996–2025)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)


def plot_map_pressure_wind(fields: dict[str, xr.DataArray], out_png: Path, basemap_path: Path | None = None) -> None:
    lon = fields["sp"]["longitude"].values
    lat = fields["sp"]["latitude"].values
    sp = fields["sp"].values
    u = fields["u10"].values
    v = fields["v10"].values

    lon_min, lon_max = float(np.min(lon)), float(np.max(lon))
    lat_min, lat_max = float(np.min(lat)), float(np.max(lat))

    fig, ax = plt.subplots(figsize=(8, 6))

    if basemap_path and basemap_path.exists():
        img = plt.imread(basemap_path)
        ax.imshow(img, extent=[lon_min, lon_max, lat_min, lat_max], origin="upper", alpha=0.85, zorder=0)

    cf = ax.contourf(lon, lat, sp, levels=12, cmap="viridis", alpha=0.52, zorder=2)
    cbar = fig.colorbar(cf, ax=ax, shrink=0.95)
    cbar.set_label("Presión superficial climatológica [hPa]")

    # Isobaras
    cs = ax.contour(lon, lat, sp, levels=8, colors="white", linewidths=1.2, zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%.1f")

    # Viento (submuestreo para legibilidad)
    step = 1 if len(lat) <= 10 else 2
    q = ax.quiver(
        lon[::step],
        lat[::step],
        u[::step, ::step],
        v[::step, ::step],
        color="black",
        scale=8,
        width=0.003,
        zorder=5,
    )
    ax.quiverkey(q, 0.90, -0.08, 1.0, "1 m s$^{-1}$", labelpos="E")

    _annotate_cities(ax, lon_min, lat_min, lon_max, lat_max)

    ax.set_title("MP2 Ítem 3 — Mapa climatológico: presión + isobaras + viento 10 m")
    ax.set_xlabel("Longitud [°]")
    ax.set_ylabel("Latitud [°]")
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_map_temperature(fields: dict[str, xr.DataArray], out_png: Path, basemap_path: Path | None = None) -> None:
    lon = fields["t2m"]["longitude"].values
    lat = fields["t2m"]["latitude"].values
    t2m = fields["t2m"].values

    lon_min, lon_max = float(np.min(lon)), float(np.max(lon))
    lat_min, lat_max = float(np.min(lat)), float(np.max(lat))

    fig, ax = plt.subplots(figsize=(8, 6))

    if basemap_path and basemap_path.exists():
        img = plt.imread(basemap_path)
        ax.imshow(img, extent=[lon_min, lon_max, lat_min, lat_max], origin="upper", alpha=0.85, zorder=0)

    cf = ax.contourf(lon, lat, t2m, levels=12, cmap="plasma", alpha=0.52, zorder=2)
    cbar = fig.colorbar(cf, ax=ax, shrink=0.95)
    cbar.set_label("Temperatura 2 m climatológica [°C]")

    cs = ax.contour(lon, lat, t2m, levels=8, colors="k", linewidths=0.8, alpha=0.7, zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%.2f")

    _annotate_cities(ax, lon_min, lat_min, lon_max, lat_max)

    ax.set_title("MP2 Ítem 3 — Mapa climatológico: temperatura 2 m")
    ax.set_xlabel("Longitud [°]")
    ax.set_ylabel("Latitud [°]")
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_report(df: pd.DataFrame, out_md: Path) -> None:
    lines = []
    lines.append("# MP2 — Ítem 3 (climatologías regionales)\n")
    lines.append("## Estado")
    lines.append("Completado (series climatológicas regionales + mapas climatológicos solicitados).\n")

    lines.append("## Metodología")
    lines.append("- Fuente: `data/raw/era5_surface_monthly_1996_2025.nc`.")
    lines.append("- Variables base: t2m, sp, u10, v10; derivada: ws10=√(u10²+v10²).")
    lines.append("- Periodo: 1996–2025 (360 meses).")
    lines.append("- Dominio: caja regional definida en el proyecto.")
    lines.append("- Media regional mensual: ponderación areal cos(lat).")
    lines.append("- Mapas: climatología media multianual de cada campo (promedio temporal 1996–2025).\n")

    lines.append("## Salidas")
    lines.append("- Tabla: `results/tables/03_climatologia_mensual.csv`")
    lines.append("- Figura (series): `results/plots/03_climatologia_mensual_superficie.png`")
    lines.append("- Figura (mapa presión+isobaras+viento): `results/plots/03_mapa_presion_isobaras_viento.png`")
    lines.append("- Figura (mapa temperatura): `results/plots/03_mapa_temperatura.png`\n")

    lines.append("## Resumen numérico (promedio anual de la climatología mensual)")
    for var, meta in VAR_META.items():
        d = df[df["variable"] == var]
        annual_mean = d["clim_mean"].mean()
        annual_std_mean = d["clim_std"].mean()
        lines.append(
            f"- {meta['label']}: media anual climatológica = {annual_mean:.3f} {meta['unit_out']}; "
            f"variabilidad interanual media mensual = {annual_std_mean:.3f} {meta['unit_out']}"
        )

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    in_nc = project_root / "data" / "raw" / "era5_surface_monthly_1996_2025.nc"

    out_csv = project_root / "results" / "tables" / "03_climatologia_mensual.csv"
    out_series_png = project_root / "results" / "plots" / "03_climatologia_mensual_superficie.png"
    out_map_sp_uv_png = project_root / "results" / "plots" / "03_mapa_presion_isobaras_viento.png"
    out_map_t_png = project_root / "results" / "plots" / "03_mapa_temperatura.png"
    out_md = project_root / "docs" / "report" / "03_item3_climatologias.md"

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_series_png.parent.mkdir(parents=True, exist_ok=True)

    ds = _open_dataset(in_nc)

    df = compute_climatology_monthly_regional(ds)
    df.to_csv(out_csv, index=False)

    fields = compute_annual_mean_fields(ds)

    lon = fields["sp"]["longitude"].values
    lat = fields["sp"]["latitude"].values
    lon_min, lon_max = float(np.min(lon)), float(np.max(lon))
    lat_min, lat_max = float(np.min(lat)), float(np.max(lat))
    basemap_path = project_root / "results" / "plots" / "03_basemap_arcgis.png"
    basemap_path = _download_basemap(lon_min, lat_min, lon_max, lat_max, basemap_path)

    plot_climatology_monthly(df, out_series_png)
    plot_map_pressure_wind(fields, out_map_sp_uv_png, basemap_path=basemap_path)
    plot_map_temperature(fields, out_map_t_png, basemap_path=basemap_path)

    write_report(df, out_md)

    print("[OK] Tabla:", out_csv)
    print("[OK] Figura series:", out_series_png)
    print("[OK] Mapa presión+viento:", out_map_sp_uv_png)
    print("[OK] Mapa temperatura:", out_map_t_png)
    print("[OK] Reporte:", out_md)


if __name__ == "__main__":
    main()
