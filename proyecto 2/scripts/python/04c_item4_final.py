#!/usr/bin/env python3
"""MP2 - Ítem 4 (versión final): geostrofía en niveles de presión + métricas y mapa de error."""

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

OMEGA = 7.2921159e-5
R_E = 6371000.0


def gradients_spherical(field: np.ndarray, lat_deg: np.ndarray, lon_deg: np.ndarray):
    lat_rad = np.deg2rad(lat_deg)
    lon_rad = np.deg2rad(lon_deg)
    dlat = np.gradient(lat_rad)
    dlon = np.gradient(lon_rad)
    dy = R_E * dlat[:, None]
    dx = (R_E * np.cos(lat_rad)[:, None]) * dlon[None, :]
    dfdx = np.gradient(field, axis=1) / dx
    dfdy = np.gradient(field, axis=0) / dy
    return dfdx, dfdy


def metricas(u_ref, v_ref, u_geo, v_geo):
    m = np.isfinite(u_ref) & np.isfinite(v_ref) & np.isfinite(u_geo) & np.isfinite(v_geo)
    ur, vr, ug, vg = u_ref[m], v_ref[m], u_geo[m], v_geo[m]

    du = ug - ur
    dv = vg - vr
    s_ref = np.sqrt(ur**2 + vr**2)
    s_geo = np.sqrt(ug**2 + vg**2)

    rmse_u = float(np.sqrt(np.mean(du**2)))
    rmse_v = float(np.sqrt(np.mean(dv**2)))
    rmse_vec = float(np.sqrt(np.mean(du**2 + dv**2)))

    mae_speed = float(np.mean(np.abs(s_geo - s_ref)))
    rel_speed = float(mae_speed / max(np.mean(s_ref), 1e-8))

    return {
        "rmse_u_m_s": rmse_u,
        "rmse_v_m_s": rmse_v,
        "rmse_vector_m_s": rmse_vec,
        "bias_u_m_s": float(np.mean(du)),
        "bias_v_m_s": float(np.mean(dv)),
        "corr_u": float(np.corrcoef(ur, ug)[0, 1]),
        "corr_v": float(np.corrcoef(vr, vg)[0, 1]),
        "mae_speed_m_s": mae_speed,
        "relative_speed_error": rel_speed,
        "n_valid_cells": int(m.sum()),
    }


def main():
    root = Path(__file__).resolve().parents[2]
    ds = xr.open_dataset(root / "data/raw/era5_pressure_monthly_1996_2025.nc")
    tdim = "time" if "time" in ds.dims else "valid_time"
    ldim = "level" if "level" in ds.dims else "pressure_level"

    lat = ds["latitude"].values
    lon = ds["longitude"].values

    resumen = []
    campos = {}

    for lev in [850, 700, 600]:
        z = ds["z"].sel({ldim: lev}).mean(tdim, skipna=True).values  # geopotential m2/s2
        u = ds["u"].sel({ldim: lev}).mean(tdim, skipna=True).values
        v = ds["v"].sel({ldim: lev}).mean(tdim, skipna=True).values

        dzdx, dzdy = gradients_spherical(z, lat, lon)
        lat2d = np.repeat(lat[:, None], len(lon), axis=1)
        f = 2 * OMEGA * np.sin(np.deg2rad(lat2d))
        f = np.where(np.abs(f) < 1e-6, np.nan, f)

        ug = -(1.0 / f) * dzdy
        vg = (1.0 / f) * dzdx

        met = metricas(u, v, ug, vg)
        met["pressure_level_hpa"] = lev
        resumen.append(met)
        campos[lev] = (u, v, ug, vg)

    df_res = pd.DataFrame(resumen).sort_values("rmse_vector_m_s")
    best_lev = int(df_res.iloc[0]["pressure_level_hpa"])
    u, v, ug, vg = campos[best_lev]

    out_tables = root / "results/tables"
    out_plots = root / "results/plots"
    out_report = root / "docs/report"
    out_tables.mkdir(parents=True, exist_ok=True)
    out_plots.mkdir(parents=True, exist_ok=True)
    out_report.mkdir(parents=True, exist_ok=True)

    f_levels = out_tables / "04_item4_metricas_por_nivel.csv"
    f_final = out_tables / "04_item4_metricas_final.csv"
    f_plot_cmp = out_plots / "04_item4_comparacion_viento_final.png"
    f_plot_err = out_plots / "04_item4_mapa_error_velocidad_final.png"
    f_md = out_report / "04_item4_geostrofia.md"

    df_res.to_csv(f_levels, index=False)
    df_res.head(1).to_csv(f_final, index=False)

    LON, LAT = np.meshgrid(lon, lat)
    # Comparación vientos
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)
    q1 = axs[0].quiver(LON, LAT, u, v, color="tab:blue")
    axs[0].quiverkey(q1, 0.9, -0.10, 1.0, "1 m s$^{-1}$", labelpos="E")
    axs[0].set_title(f"ERA5 climatológico ({best_lev} hPa)")
    q2 = axs[1].quiver(LON, LAT, ug, vg, color="tab:red")
    axs[1].quiverkey(q2, 0.9, -0.10, 1.0, "1 m s$^{-1}$", labelpos="E")
    axs[1].set_title(f"Geostrófico estimado ({best_lev} hPa)")
    for ax in axs:
        ax.set_xlabel("Longitud [°]")
        ax.grid(alpha=0.25)
    axs[0].set_ylabel("Latitud [°]")
    fig.suptitle("Comparación final del campo de velocidad (ítem 4)")
    fig.tight_layout()
    fig.savefig(f_plot_cmp, dpi=240)
    plt.close(fig)

    # Mapa de error de magnitud
    err = np.sqrt((ug - u) ** 2 + (vg - v) ** 2)
    fig, ax = plt.subplots(figsize=(7, 6))
    cf = ax.contourf(lon, lat, err, levels=12, cmap="magma")
    cbar = fig.colorbar(cf, ax=ax, shrink=0.92)
    cbar.set_label("Error vectorial |Vg - V| [m s$^{-1}$]")
    ax.set_title(f"Mapa de error vectorial geostrofía vs ERA5 ({best_lev} hPa)")
    ax.set_xlabel("Longitud [°]")
    ax.set_ylabel("Latitud [°]")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(f_plot_err, dpi=240)
    plt.close(fig)

    best = df_res.iloc[0].to_dict()
    lines = [
        "# MP2 — Ítem 4 (aproximación geostrófica)",
        "",
        "## Resultados finales",
        f"- Nivel seleccionado (menor RMSE vectorial): **{best_lev} hPa**.",
        f"- RMSE vectorial: **{best['rmse_vector_m_s']:.3f} m/s**.",
        f"- Error relativo de rapidez: **{best['relative_speed_error']:.3f}**.",
        "",
        "## Archivos",
        "- Tabla por nivel: `results/tables/04_item4_metricas_por_nivel.csv`",
        "- Tabla final: `results/tables/04_item4_metricas_final.csv`",
        "- Figura comparación: `results/plots/04_item4_comparacion_viento_final.png`",
        "- Figura mapa de error: `results/plots/04_item4_mapa_error_velocidad_final.png`",
    ]
    f_md.write_text("\n".join(lines), encoding="utf-8")

    print("[OK]", f_levels)
    print("[OK]", f_final)
    print("[OK]", f_plot_cmp)
    print("[OK]", f_plot_err)
    print("[OK]", f_md)


if __name__ == "__main__":
    main()
