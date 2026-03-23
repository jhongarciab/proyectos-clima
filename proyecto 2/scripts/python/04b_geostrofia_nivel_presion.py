#!/usr/bin/env python3
"""
Ítem 4 — Aproximación geostrófica
Calcula el viento geostrófico a partir del geopotencial ERA5 y lo compara
con el viento real del reanálisis en múltiples niveles de presión.

Física:
    u_g = -(1/f) * d(Phi)/dy
    v_g =  (1/f) * d(Phi)/dx
    donde Phi = z [m²/s²] es el geopotencial y f = 2*Omega*sin(lat)

Limitaciones conocidas en esta región:
  - Latitud baja (4–5.5°N): f pequeño → amplificación de errores numéricos
  - Dominio pequeño (1.5°×1.5°, 7 puntos): gradientes con diferencias finitas
    tienen error numérico significativo
  - Topografía compleja: fuerza ageostrófica relevante en superficie

Estrategia:
  - Evaluar todos los niveles disponibles
  - Suavizar el geopotencial con filtro gaussiano antes del gradiente
  - Reportar métricas en todos los niveles y seleccionar el mejor
  - Discutir físicamente por qué la aproximación falla cerca del ecuador

Salidas:
  - results/tables/04_geostrofia_metricas_todos_niveles.csv
  - results/plots/04_geostrofia_mejor_nivel.pdf
  - results/plots/04_geostrofia_rmse_por_nivel.pdf
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
from scipy.ndimage import gaussian_filter

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

OMEGA = 7.2921159e-5   # rad/s
R_E   = 6371000.0      # m
G     = 9.80665        # m/s²
SIGMA = 1.0            # suavizado gaussiano (píxeles)


# ─────────────────────────────────────────
# Gradientes en coordenadas esféricas
# ─────────────────────────────────────────
def spherical_gradients(field: np.ndarray,
                        lat_deg: np.ndarray,
                        lon_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    dfield/dx y dfield/dy en coordenadas esféricas.
    field shape: (nlat, nlon), lat N→S, lon W→E.
    """
    lat_rad = np.deg2rad(lat_deg)
    lon_rad = np.deg2rad(lon_deg)

    # Espaciados uniformes
    dlat = abs(lat_rad[1] - lat_rad[0])
    dlon = abs(lon_rad[1] - lon_rad[0])

    # Métricas métricas (m por radian)
    dy = R_E * dlat                                      # escalar
    dx = R_E * np.cos(lat_rad) * dlon                   # (nlat,)

    dfdx = np.gradient(field, axis=1) / dx[:, None]     # broadcast (nlat,1)
    dfdy = np.gradient(field, axis=0) / dy

    return dfdx, dfdy


def coriolis(lat_deg: np.ndarray, nlon: int) -> np.ndarray:
    """Parámetro de Coriolis f (nlat, nlon). NaN donde |f| < umbral."""
    f1d = 2.0 * OMEGA * np.sin(np.deg2rad(lat_deg))
    f2d = np.repeat(f1d[:, None], nlon, axis=1)
    # En trópicos f es pequeño; ponemos NaN donde |f| < 5e-6 (~2.3°)
    f2d = np.where(np.abs(f2d) < 5e-6, np.nan, f2d)
    return f2d


# ─────────────────────────────────────────
# Métricas de comparación
# ─────────────────────────────────────────
def compute_metrics(u_era: np.ndarray, v_era: np.ndarray,
                    ug: np.ndarray,    vg: np.ndarray,
                    level_hpa: float) -> dict:
    mask = (np.isfinite(u_era) & np.isfinite(v_era) &
            np.isfinite(ug)    & np.isfinite(vg))
    if mask.sum() < 2:
        return {}

    ur, vr = u_era[mask], v_era[mask]
    uc, vc = ug[mask],    vg[mask]

    du, dv     = uc - ur, vc - vr
    ws_era     = np.sqrt(ur**2 + vr**2)
    ws_geo     = np.sqrt(uc**2 + vc**2)

    # Ángulo entre vectores (0° = perfectamente paralelos)
    dot        = ur*uc + vr*vc
    norm       = np.maximum(ws_era * ws_geo, 1e-10)
    angle_diff = np.degrees(np.arccos(np.clip(dot / norm, -1, 1)))

    return {
        "pressure_level_hpa":    level_hpa,
        "rmse_u_ms":             float(np.sqrt(np.mean(du**2))),
        "rmse_v_ms":             float(np.sqrt(np.mean(dv**2))),
        "rmse_vector_ms":        float(np.sqrt(np.mean(du**2 + dv**2))),
        "bias_u_ms":             float(np.mean(du)),
        "bias_v_ms":             float(np.mean(dv)),
        "corr_u":                float(np.corrcoef(ur, uc)[0, 1]),
        "corr_v":                float(np.corrcoef(vr, vc)[0, 1]),
        "mae_speed_ms":          float(np.mean(np.abs(ws_geo - ws_era))),
        "mean_ws_era_ms":        float(np.mean(ws_era)),
        "mean_ws_geo_ms":        float(np.mean(ws_geo)),
        "relative_speed_error":  float(np.mean(np.abs(ws_geo - ws_era)) /
                                       max(np.mean(ws_era), 1e-8)),
        "mean_angle_diff_deg":   float(np.mean(angle_diff)),
        "n_valid":               int(mask.sum()),
    }


# ─────────────────────────────────────────
# Figura 1 — comparación en el mejor nivel
# ─────────────────────────────────────────
def plot_comparison(lon, lat, u_era, v_era, ug, vg,
                    level_hpa, metrics_row, out_pdf: Path) -> None:
    LON, LAT = np.meshgrid(lon, lat)
    ws_era = np.sqrt(u_era**2 + v_era**2)
    ws_geo = np.sqrt(ug**2    + vg**2)

    fig, axs = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    fig.subplots_adjust(wspace=0.32)

    # Escala común para quiver
    scale = max(ws_era.max(), ws_geo.max()) * 6

    # Panel 1 — ERA5
    q1 = axs[0].quiver(LON, LAT, u_era, v_era,
                        ws_era, cmap="viridis",
                        scale=scale, width=0.007)
    axs[0].set_title(f"ERA5 viento real\n{level_hpa:.0f} hPa")
    fig.colorbar(q1, ax=axs[0], shrink=0.8, label="m s$^{-1}$")

    # Panel 2 — Geostrófico
    q2 = axs[1].quiver(LON, LAT, ug, vg,
                        ws_geo, cmap="viridis",
                        scale=scale, width=0.007)
    axs[1].set_title(f"Viento geostrófico\n{level_hpa:.0f} hPa")
    fig.colorbar(q2, ax=axs[1], shrink=0.8, label="m s$^{-1}$")

    # Panel 3 — Diferencia vectorial
    du, dv = ug - u_era, vg - v_era
    dws = np.sqrt(du**2 + dv**2)
    q3 = axs[2].quiver(LON, LAT, du, dv,
                        dws, cmap="Reds",
                        scale=scale, width=0.007)
    axs[2].set_title(f"Diferencia (geo - ERA5)\n{level_hpa:.0f} hPa")
    fig.colorbar(q3, ax=axs[2], shrink=0.8, label="m s$^{-1}$")

    for ax in axs:
        ax.set_xlabel("Longitud [°]")
        ax.grid(alpha=0.25)
    axs[0].set_ylabel("Latitud [°]")

    rmse  = metrics_row["rmse_vector_ms"]
    corrU = metrics_row["corr_u"]
    corrV = metrics_row["corr_v"]
    angle = metrics_row["mean_angle_diff_deg"]
    fig.suptitle(
        f"Geostrofía vs ERA5 — {level_hpa:.0f} hPa  |  "
        f"RMSE = {rmse:.2f} m/s  |  "
        f"r(u) = {corrU:.2f}  r(v) = {corrV:.2f}  |  "
        f"Dif. angular media = {angle:.1f}°",
        fontsize=10
    )

    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Figura comparación: {out_pdf.name}")


# ─────────────────────────────────────────
# Figura 2 — RMSE y correlación por nivel
# ─────────────────────────────────────────
def plot_metrics_by_level(df: pd.DataFrame, out_pdf: Path) -> None:
    df = df.sort_values("pressure_level_hpa", ascending=False)  # superficie→arriba
    levels = df["pressure_level_hpa"].values

    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
    fig.subplots_adjust(wspace=0.3)

    # RMSE vectorial
    axes[0].plot(df["rmse_vector_ms"], levels, "o-", color="#d62728", lw=1.8)
    axes[0].set_xlabel("RMSE vectorial [m s$^{-1}$]")
    axes[0].set_ylabel("Nivel de presión [hPa]")
    axes[0].set_title("RMSE vectorial")
    axes[0].grid(alpha=0.3)

    # Correlación u y v
    axes[1].plot(df["corr_u"], levels, "s-", color="#1f77b4", lw=1.8, label="r(u)")
    axes[1].plot(df["corr_v"], levels, "^-", color="#2ca02c", lw=1.8, label="r(v)")
    axes[1].axvline(0, color="grey", lw=0.8, ls="--")
    axes[1].set_xlabel("Correlación de Pearson")
    axes[1].set_title("Correlación u, v")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    # Ángulo medio de diferencia
    axes[2].plot(df["mean_angle_diff_deg"], levels, "D-", color="#ff7f0e", lw=1.8)
    axes[2].set_xlabel("Diferencia angular media [°]")
    axes[2].set_title("Error direccional")
    axes[2].grid(alpha=0.3)

    for ax in axes:
        ax.set_ylim(levels.min() - 20, levels.max() + 20)
        ax.invert_yaxis()
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.suptitle(
        "Calidad de la aproximación geostrófica por nivel de presión (1996–2025)",
        fontsize=11
    )
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Figura métricas por nivel: {out_pdf.name}")


# ─────────────────────────────────────────
# main
# ─────────────────────────────────────────
def main() -> None:
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    nc  = project_root / "data" / "raw" / "era5_pressure_monthly_1996_2025.nc"
    ds  = xr.open_dataset(nc)
    tdim = "valid_time" if "valid_time" in ds.dims else "time"
    ldim = "pressure_level" if "pressure_level" in ds.dims else "level"

    lat = ds["latitude"].values
    lon = ds["longitude"].values
    f   = coriolis(lat, len(lon))

    levels = ds[ldim].values
    all_metrics = []
    all_fields  = {}

    for lev in levels:
        z_raw = ds["z"].sel({ldim: lev}).mean(tdim, skipna=True).values
        u_era = ds["u"].sel({ldim: lev}).mean(tdim, skipna=True).values
        v_era = ds["v"].sel({ldim: lev}).mean(tdim, skipna=True).values

        # Suavizado gaussiano para reducir ruido numérico en gradientes
        z_smooth = gaussian_filter(z_raw, sigma=SIGMA)

        dphidx, dphidy = spherical_gradients(z_smooth, lat, lon)

        ug = -(1.0 / f) * dphidy
        vg =  (1.0 / f) * dphidx

        m = compute_metrics(u_era, v_era, ug, vg, float(lev))
        if m:
            all_metrics.append(m)
            all_fields[float(lev)] = (u_era, v_era, ug, vg)

    df = pd.DataFrame(all_metrics)

    # Nivel con menor RMSE vectorial
    best_row = df.loc[df["rmse_vector_ms"].idxmin()]
    best_lev = float(best_row["pressure_level_hpa"])
    print(f"\n[INFO] Mejor nivel: {best_lev:.0f} hPa  "
          f"| RMSE = {best_row['rmse_vector_ms']:.3f} m/s  "
          f"| r(u) = {best_row['corr_u']:.3f}  "
          f"| r(v) = {best_row['corr_v']:.3f}")

    # Salidas
    out_tbl  = project_root / "results" / "tables" / "04_geostrofia_metricas_todos_niveles.csv"
    out_cmp  = project_root / "results" / "plots"  / "04_geostrofia_comparacion.pdf"
    out_lvl  = project_root / "results" / "plots"  / "04_geostrofia_rmse_por_nivel.pdf"

    out_tbl.parent.mkdir(parents=True, exist_ok=True)
    out_cmp.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_tbl, index=False, float_format="%.4f")
    print(f"[OK] Tabla: {out_tbl.name}")

    u_era, v_era, ug, vg = all_fields[best_lev]
    plot_comparison(lon, lat, u_era, v_era, ug, vg,
                    best_lev, best_row.to_dict(), out_cmp)
    plot_metrics_by_level(df, out_lvl)

    print("\n── Métricas en el mejor nivel ──")
    for k, v in best_row.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")


if __name__ == "__main__":
    main()