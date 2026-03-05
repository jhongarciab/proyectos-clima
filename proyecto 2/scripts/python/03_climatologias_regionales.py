#!/usr/bin/env python3
"""
Ítem 3 — Mini Proyecto 2
Climatologías regionales mensuales (1996–2025) para variables de superficie ERA5:
- t2m, sp, u10, v10, ws10 (derivada) 

Salidas:
- results/tables/03_climatologia_mensual.csv
- results/plots/03_climatologia_mensual_superficie.png
- docs/report/03_item3_climatologias.md
"""

from __future__ import annotations

from pathlib import Path
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


def _open_dataset(nc_path: Path) -> xr.Dataset:
    # engine automático (xarray decide backend disponible)
    return xr.open_dataset(nc_path)


def compute_climatology(ds: xr.Dataset) -> pd.DataFrame:
    rows = []

    time_dim = "time" if "time" in ds.dims else "valid_time"

    # Ponderación areal simple por cos(lat) para media regional
    lat_weights = np.cos(np.deg2rad(ds["latitude"]))
    lat_weights = lat_weights / lat_weights.mean()

    # Derivada útil: rapidez del viento a 10 m
    ws10 = np.sqrt(ds["u10"] ** 2 + ds["v10"] ** 2)

    for var, meta in VAR_META.items():
        if var == "ws10":
            da = ws10
        else:
            if var not in ds:
                raise KeyError(f"Variable requerida no encontrada en NetCDF: {var}")
            da = ds[var]

        # Serie regional mensual: media espacial ponderada (lat-lon) para cada mes del periodo completo
        ts_region = da.weighted(lat_weights).mean(dim=("latitude", "longitude"), skipna=True)
        ts_region = meta["convert"](ts_region)

        # Climatología mensual + variabilidad interanual (sobre 30 eneros, 30 febreros, etc.)
        clim_mean = ts_region.groupby(f"{time_dim}.month").mean(time_dim, skipna=True)
        clim_std = ts_region.groupby(f"{time_dim}.month").std(time_dim, skipna=True)

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


def plot_climatology(df: pd.DataFrame, out_png: Path) -> None:
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
        ax.set_xticklabels(MONTH_LABELS, rotation=0)
        ax.grid(alpha=0.3)

    # Ocultar ejes sobrantes
    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle("MP2 — Ítem 3: climatología mensual regional (1996–2025)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)


def write_report(df: pd.DataFrame, out_md: Path) -> None:
    lines = []
    lines.append("# MP2 — Ítem 3 (climatologías regionales)\n")
    lines.append("## Estado")
    lines.append("Completado (cálculo de climatología mensual regional + figura + tabla).\n")

    lines.append("## Metodología")
    lines.append("- Fuente: `data/raw/era5_surface_monthly_1996_2025.nc`.")
    lines.append("- Variables: t2m, sp, u10, v10 y derivada ws10=√(u10²+v10²).")
    lines.append("- Periodo: 1996–2025 (360 meses).")
    lines.append("- Dominio: caja regional definida en el proyecto.")
    lines.append("- Procedimiento: media espacial mensual ponderada por área (peso cos(lat)) y luego climatología por mes calendario (enero–diciembre), reportando media y desviación estándar interanual.\n")

    lines.append("## Salidas")
    lines.append("- Tabla: `results/tables/03_climatologia_mensual.csv`")
    lines.append("- Figura: `results/plots/03_climatologia_mensual_superficie.png`\n")

    lines.append("## Resumen numérico (promedio anual de la climatología mensual)")
    for var, meta in VAR_META.items():
        d = df[df["variable"] == var]
        annual_mean = d["clim_mean"].mean()
        annual_std_mean = d["clim_std"].mean()
        lines.append(f"- {meta['label']}: media anual climatológica = {annual_mean:.3f} {meta['unit_out']}; variabilidad interanual media mensual = {annual_std_mean:.3f} {meta['unit_out']}")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    in_nc = project_root / "data" / "raw" / "era5_surface_monthly_1996_2025.nc"
    out_csv = project_root / "results" / "tables" / "03_climatologia_mensual.csv"
    out_png = project_root / "results" / "plots" / "03_climatologia_mensual_superficie.png"
    out_md = project_root / "docs" / "report" / "03_item3_climatologias.md"

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_png.parent.mkdir(parents=True, exist_ok=True)

    ds = _open_dataset(in_nc)
    df = compute_climatology(ds)
    df.to_csv(out_csv, index=False)
    plot_climatology(df, out_png)
    write_report(df, out_md)

    print("[OK] Tabla:", out_csv)
    print("[OK] Figura:", out_png)
    print("[OK] Reporte:", out_md)


if __name__ == "__main__":
    main()
