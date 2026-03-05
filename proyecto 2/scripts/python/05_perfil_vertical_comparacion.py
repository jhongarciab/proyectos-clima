#!/usr/bin/env python3
"""MP2 ítem 5: perfil vertical climatológico regional vs atmósfera estándar."""

from __future__ import annotations

import json
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

G = 9.80665


def load_config(script_dir: Path):
    cfg_path = script_dir / "00_config_mp2.py"
    spec = importlib.util.spec_from_file_location("config_mp2", cfg_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No fue posible cargar configuración: {cfg_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ensure_pressure_profile_dataset(project_root: Path, cfg) -> Path:
    out_nc = project_root / "data" / "raw" / "era5_pressure_profile_monthly_1996_2025.nc"
    out_req = project_root / "data" / "raw" / "era5_pressure_profile_request.json"

    if out_nc.exists() and out_nc.stat().st_size > 0:
        return out_nc

    from cdsapi import Client

    req = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["temperature", "geopotential"],
        "pressure_level": cfg.PRESSURE_LEVELS_HPA,
        "year": cfg.YEARS,
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": cfg.AREA,
    }

    out_req.write_text(json.dumps(req, indent=2), encoding="utf-8")
    c = Client()
    c.retrieve("reanalysis-era5-pressure-levels-monthly-means", req, str(out_nc))
    return out_nc


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    cfg = load_config(script_dir)

    nc = ensure_pressure_profile_dataset(project_root, cfg)
    ds = xr.open_dataset(nc)

    tdim = "time" if "time" in ds.dims else "valid_time"
    ldim = "level" if "level" in ds.dims else "pressure_level"

    # Climatología multianual + media espacial regional
    T = ds["t"].mean(tdim, skipna=True).mean(dim=("latitude", "longitude"), skipna=True)  # K
    Z = (ds["z"] / G).mean(tdim, skipna=True).mean(dim=("latitude", "longitude"), skipna=True)  # m

    # ordenar por altura ascendente
    z_vals = Z.values
    t_vals = T.values
    p_vals = ds[ldim].values.astype(float)
    order = np.argsort(z_vals)
    z_vals = z_vals[order]
    t_vals = t_vals[order]
    p_vals = p_vals[order]

    # Perfil ISA de referencia desde resultados del ítem 1
    isa_path = project_root / "results" / "tables" / "01_atmosfera_estandar.csv"
    isa = pd.read_csv(isa_path)

    # Interpolar ISA a las alturas del perfil regional
    t_isa_interp = np.interp(z_vals, isa["z_m"].values, isa["temperature_K"].values)

    # Métricas
    diff = t_vals - t_isa_interp
    rmse = float(np.sqrt(np.mean(diff**2)))
    bias = float(np.mean(diff))
    mae = float(np.mean(np.abs(diff)))

    out_tbl = project_root / "results" / "tables" / "05_perfil_vertical_comparacion.csv"
    out_met = project_root / "results" / "tables" / "05_perfil_vertical_metricas.csv"
    out_plot = project_root / "results" / "plots" / "05_perfil_vertical_temperatura_vs_isa.png"
    out_plot2 = project_root / "results" / "plots" / "05_perfil_vertical_diferencia_temperatura.png"
    out_md = project_root / "docs" / "report" / "05_item5_perfil_vertical.md"

    out_tbl.parent.mkdir(parents=True, exist_ok=True)
    out_plot.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        {
            "pressure_hpa": p_vals,
            "z_m": z_vals,
            "z_km": z_vals / 1000.0,
            "T_regional_K": t_vals,
            "T_regional_C": t_vals - 273.15,
            "T_isa_interp_K": t_isa_interp,
            "T_diff_regional_minus_isa_K": diff,
        }
    )
    df.to_csv(out_tbl, index=False)

    pd.DataFrame([
        {
            "rmse_K": rmse,
            "bias_K": bias,
            "mae_K": mae,
            "n_levels": len(df),
            "z_min_m": float(np.min(z_vals)),
            "z_max_m": float(np.max(z_vals)),
        }
    ]).to_csv(out_met, index=False)

    # Figura 1: perfiles T(z)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(t_vals, z_vals / 1000, "o-", label="Perfil regional climatológico", lw=2)
    ax.plot(t_isa_interp, z_vals / 1000, "s--", label="Atmósfera estándar (interpolada)", lw=1.8)
    ax.set_xlabel("Temperatura [K]")
    ax.set_ylabel("Altura geopotencial [km]")
    ax.set_title("Perfil vertical de temperatura: región vs atmósfera estándar")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_plot, dpi=240)
    plt.close(fig)

    # Figura 2: diferencia térmica
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.axvline(0.0, color="k", lw=1)
    ax.plot(diff, z_vals / 1000, "o-", color="tab:red", lw=2)
    ax.set_xlabel("ΔT = T_regional - T_ISA [K]")
    ax.set_ylabel("Altura geopotencial [km]")
    ax.set_title("Diferencia térmica vertical respecto a atmósfera estándar")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_plot2, dpi=240)
    plt.close(fig)

    out_md.write_text(
        "\n".join(
            [
                "# MP2 — Ítem 5 (perfil vertical regional)",
                "",
                "## Resultados generados",
                f"- Tabla principal: `{out_tbl.relative_to(project_root)}`",
                f"- Métricas: `{out_met.relative_to(project_root)}`",
                f"- Figura perfil: `{out_plot.relative_to(project_root)}`",
                f"- Figura diferencia: `{out_plot2.relative_to(project_root)}`",
                "",
                "## Métricas de comparación región vs ISA",
                f"- RMSE: {rmse:.3f} K",
                f"- Sesgo medio (región - ISA): {bias:.3f} K",
                f"- MAE: {mae:.3f} K",
            ]
        ),
        encoding="utf-8",
    )

    print("[OK]", out_tbl)
    print("[OK]", out_met)
    print("[OK]", out_plot)
    print("[OK]", out_plot2)
    print("[OK]", out_md)


if __name__ == "__main__":
    main()
