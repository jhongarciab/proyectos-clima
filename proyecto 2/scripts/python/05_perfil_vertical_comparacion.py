#!/usr/bin/env python3
"""
Ítem 5 — Perfil vertical de temperatura: región ERA5 vs atmósfera estándar ISA
Calcula el climatológico multianual 1996-2025, promedio espacial regional,
y compara nivel a nivel con el perfil ISA del ítem 1.

Salidas:
- results/tables/05_perfil_vertical.csv
- results/tables/05_perfil_vertical_metricas.csv
- results/plots/05_perfil_vertical_temperatura.pdf
- results/plots/05_perfil_vertical_diferencia.pdf
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

matplotlib.rcParams.update({
    "text.usetex":     False,
    "font.family":     "serif",
    "font.serif":      ["DejaVu Serif", "Georgia", "Times New Roman"],
    "font.size":       11,
    "axes.labelsize":  11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.titlesize":  11,
})

G = 9.80665  # m/s²

# Bandas atmosféricas para sombreado (hasta ~21 km)
LAYER_BANDS = [
    (  0,  11, "#cce5ff", "Troposfera"),
    ( 11,  20, "#d4edda", "Est. baja"),
    ( 20,  21, "#c3e6cb", "Est. media"),
]


def _add_bands(ax, z_min, z_max):
    for z0, z1, color, label in LAYER_BANDS:
        if z1 <= z_min or z0 >= z_max:
            continue
        z0c, z1c = max(z0, z_min), min(z1, z_max)
        ax.axhspan(z0c, z1c, color=color, alpha=0.20, zorder=0)
        mid = (z0c + z1c) / 2
        ax.text(0.985, mid, label, transform=ax.get_yaxis_transform(),
                fontsize=7, va="center", ha="right",
                color="#555555", style="italic")


def main() -> None:
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    nc_pres = project_root / "data" / "raw" / "era5_pressure_monthly_1996_2025.nc"
    isa_csv = project_root / "results" / "tables" / "01_atmosfera_estandar.csv"

    out_tbl  = project_root / "results" / "tables" / "05_perfil_vertical.csv"
    out_met  = project_root / "results" / "tables" / "05_perfil_vertical_metricas.csv"
    out_pdf1 = project_root / "results" / "plots"  / "05_perfil_vertical_temperatura.pdf"
    out_pdf2 = project_root / "results" / "plots"  / "05_perfil_vertical_diferencia.pdf"

    out_tbl.parent.mkdir(parents=True, exist_ok=True)
    out_pdf1.parent.mkdir(parents=True, exist_ok=True)

    # ── Cargar ERA5 ───────────────────────────────────────────────────────────
    ds   = xr.open_dataset(nc_pres)
    tdim = "valid_time" if "valid_time" in ds.dims else "time"
    ldim = "pressure_level" if "pressure_level" in ds.dims else "level"

    # Climatológico multianual + promedio espacial regional ponderado por cos(lat)
    lat_weights = np.cos(np.deg2rad(ds["latitude"].values))
    lat_weights = xr.DataArray(lat_weights, coords=[ds["latitude"]], dims=["latitude"])
    lat_weights = lat_weights / lat_weights.mean()

    T_era = (ds["t"].mean(tdim, skipna=True)
               .weighted(lat_weights)
               .mean(dim=("latitude", "longitude"), skipna=True))
    Z_era = ((ds["z"] / G).mean(tdim, skipna=True)
               .weighted(lat_weights)
               .mean(dim=("latitude", "longitude"), skipna=True))

    p_vals = ds[ldim].values.astype(float)
    z_vals = Z_era.values
    t_vals = T_era.values

    # Ordenar por altura ascendente
    order  = np.argsort(z_vals)
    p_vals, z_vals, t_vals = p_vals[order], z_vals[order], t_vals[order]

    # ── ISA de referencia (ítem 1) ────────────────────────────────────────────
    isa       = pd.read_csv(isa_csv)
    t_isa_K   = np.interp(z_vals, isa["z_m"].values, isa["temperature_K"].values)
    t_isa_C   = t_isa_K - 273.15
    t_era_C   = t_vals  - 273.15
    diff_K    = t_vals  - t_isa_K   # ERA5 - ISA

    # ── Tabla de resultados ───────────────────────────────────────────────────
    df = pd.DataFrame({
        "pressure_hpa":           p_vals,
        "z_m":                    z_vals,
        "z_km":                   z_vals / 1000.0,
        "T_era5_K":               t_vals,
        "T_era5_C":               t_era_C,
        "T_isa_K":                t_isa_K,
        "T_isa_C":                t_isa_C,
        "dT_era5_minus_isa_K":    diff_K,
    })
    df.to_csv(out_tbl, index=False, float_format="%.4f")
    print(f"[OK] Tabla: {out_tbl.name}")

    # ── Métricas ──────────────────────────────────────────────────────────────
    rmse = float(np.sqrt(np.mean(diff_K**2)))
    bias = float(np.mean(diff_K))
    mae  = float(np.mean(np.abs(diff_K)))

    met = pd.DataFrame([{
        "rmse_K": rmse, "bias_K": bias, "mae_K": mae,
        "n_levels": len(df),
        "z_min_m": float(z_vals.min()), "z_max_m": float(z_vals.max()),
        "max_warm_bias_K": float(diff_K.max()),
        "max_cold_bias_K": float(diff_K.min()),
        "z_at_max_warm_m": float(z_vals[diff_K.argmax()]),
        "z_at_max_cold_m": float(z_vals[diff_K.argmin()]),
    }])
    met.to_csv(out_met, index=False, float_format="%.4f")
    print(f"[OK] Métricas: {out_met.name}")

    z_km   = z_vals / 1000.0
    z_max  = z_km.max() + 0.5

    # ── Figura 1 — Perfiles T(z) ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.subplots_adjust(left=0.15, right=0.88, top=0.93, bottom=0.09)

    _add_bands(ax, 0, z_max)

    ax.plot(t_era_C, z_km, "o-", color="#1f77b4", lw=2.0, ms=5,
            label="ERA5 climatológico (1996–2025)")
    ax.plot(t_isa_C, z_km, "s--", color="#d62728", lw=1.8, ms=5,
            label="Atmósfera estándar ISA")

    # Etiquetas de presión en el eje Y derecho
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(z_km)
    ax2.set_yticklabels([f"{p:.0f}" for p in p_vals], fontsize=7)
    ax2.set_ylabel("Nivel de presión [hPa]", fontsize=9)

    ax.set_xlabel("Temperatura [°C]")
    ax.set_ylabel("Altura geopotencial [km]")
    ax.set_ylim(0, z_max)
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax.grid(axis="y", alpha=0.25, lw=0.6)
    ax.grid(axis="x", alpha=0.15, lw=0.6)
    ax.legend(loc="upper right", framealpha=0.88)
    ax.set_title(
        f"Perfil vertical de temperatura\n"
        f"Región 4–5.5°N, 76.5–75°W  |  RMSE = {rmse:.1f} K  |  Sesgo = {bias:+.1f} K",
        fontsize=10
    )

    fig.savefig(out_pdf1, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Figura perfil: {out_pdf1.name}")

    # ── Figura 2 — Diferencia ERA5 - ISA ─────────────────────────────────────
    fig, ax = plt.subplots(figsize=(5, 8))
    fig.subplots_adjust(left=0.18, right=0.88, top=0.93, bottom=0.09)

    _add_bands(ax, 0, z_max)

    ax.axvline(0, color="black", lw=0.9, ls="--", alpha=0.6)
    ax.fill_betweenx(z_km, 0, diff_K,
                     where=(diff_K > 0), color="#d62728", alpha=0.25, label="ERA5 más cálido")
    ax.fill_betweenx(z_km, 0, diff_K,
                     where=(diff_K < 0), color="#1f77b4", alpha=0.25, label="ERA5 más frío")
    ax.plot(diff_K, z_km, "o-", color="#2ca02c", lw=2.0, ms=5)

    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(z_km)
    ax2.set_yticklabels([f"{p:.0f}" for p in p_vals], fontsize=7)
    ax2.set_ylabel("Nivel de presión [hPa]", fontsize=9)

    ax.set_xlabel(r"$\Delta T$ = ERA5 $-$ ISA [K]")
    ax.set_ylabel("Altura geopotencial [km]")
    ax.set_ylim(0, z_max)
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax.grid(axis="y", alpha=0.25, lw=0.6)
    ax.grid(axis="x", alpha=0.15, lw=0.6)
    ax.legend(loc="lower right", framealpha=0.88)
    ax.set_title(
        "Diferencia térmica vertical\nERA5 climatológico $-$ ISA",
        fontsize=10
    )

    fig.savefig(out_pdf2, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Figura diferencia: {out_pdf2.name}")

    # Resumen en consola
    print(f"\n── Métricas ERA5 vs ISA ──")
    print(f"  RMSE  = {rmse:.2f} K")
    print(f"  Sesgo = {bias:+.2f} K  (ERA5 más cálido en promedio)")
    print(f"  MAE   = {mae:.2f} K")
    print(f"  Mayor calentamiento: {diff_K.max():+.1f} K a {z_vals[diff_K.argmax()]/1000:.1f} km ({p_vals[diff_K.argmax()]:.0f} hPa)")
    print(f"  Mayor enfriamiento:  {diff_K.min():+.1f} K a {z_vals[diff_K.argmin()]/1000:.1f} km ({p_vals[diff_K.argmin()]:.0f} hPa)")


if __name__ == "__main__":
    main()