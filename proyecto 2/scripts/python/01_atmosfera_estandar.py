#!/usr/bin/env python3
"""
Ítem 1 — Mini Proyecto 2
Perfiles verticales de T(z), p(z) y rho(z) usando la Atmósfera Estándar ISA (1976)
en la troposfera y estratósfera baja (0–20 km).

Salidas:
- results/tables/01_atmosfera_estandar.csv
- results/tables/01_atmosfera_estandar_validacion.csv
- results/plots/01_atmosfera_estandar.png
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Constantes físicas
# -------------------------
G0 = 9.80665         # gravedad estándar [m s^-2]
R_D = 287.05         # constante específica del aire seco [J kg^-1 K^-1]
P0 = 101325.0        # presión estándar a nivel del mar [Pa]
T0 = 288.15          # temperatura estándar a nivel del mar [K]
RHO0 = P0 / (R_D * T0)

# Capas ISA usadas aquí:
# 0-11 km: gradiente lineal L=-6.5 K/km
# 11-20 km: isotérmica T=216.65 K
Z_TROPOPAUSA = 11000.0   # [m]
LAPSE = -0.0065          # [K m^-1]


def isa_temperature(z_m: np.ndarray) -> np.ndarray:
    """Temperatura ISA [K] para 0–20 km."""
    z_m = np.asarray(z_m)
    T = np.empty_like(z_m, dtype=float)

    mask_tropo = z_m <= Z_TROPOPAUSA
    T[mask_tropo] = T0 + LAPSE * z_m[mask_tropo]

    T_tropopause = T0 + LAPSE * Z_TROPOPAUSA
    T[~mask_tropo] = T_tropopause  # capa isotérmica 11-20 km
    return T


def isa_pressure(z_m: np.ndarray) -> np.ndarray:
    """Presión ISA [Pa] para 0–20 km."""
    z_m = np.asarray(z_m)
    p = np.empty_like(z_m, dtype=float)

    # 0-11 km (lapse rate constante)
    mask_tropo = z_m <= Z_TROPOPAUSA
    T = isa_temperature(z_m)
    p[mask_tropo] = P0 * (T[mask_tropo] / T0) ** (-G0 / (R_D * LAPSE))

    # 11-20 km (isotérmica)
    z11 = Z_TROPOPAUSA
    T11 = T0 + LAPSE * z11
    p11 = P0 * (T11 / T0) ** (-G0 / (R_D * LAPSE))
    p[~mask_tropo] = p11 * np.exp(-G0 * (z_m[~mask_tropo] - z11) / (R_D * T11))
    return p


def build_profiles(z_min_m: float = 0.0, z_max_m: float = 20000.0, dz_m: float = 100.0) -> pd.DataFrame:
    z = np.arange(z_min_m, z_max_m + dz_m, dz_m)
    T = isa_temperature(z)
    p = isa_pressure(z)
    rho = p / (R_D * T)

    df = pd.DataFrame(
        {
            "z_m": z,
            "z_km": z / 1000.0,
            "temperature_K": T,
            "temperature_C": T - 273.15,
            "pressure_Pa": p,
            "pressure_hPa": p / 100.0,
            "density_kg_m3": rho,
        }
    )
    return df


def validate_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Validaciones numéricas básicas: monotonicidad y ecuaciones diagnósticas."""
    z = df["z_m"].to_numpy()
    T = df["temperature_K"].to_numpy()
    p = df["pressure_Pa"].to_numpy()
    rho = df["density_kg_m3"].to_numpy()

    # 1) Monotonicidad esperada
    dp = np.diff(p)
    drho = np.diff(rho)
    monotonic_p = np.all(dp < 0)
    monotonic_rho = np.all(drho < 0)

    # 2) Cierre de ecuación de estado (debe ser exacto por construcción)
    p_ideal = rho * R_D * T
    rel_err_ideal = np.abs((p - p_ideal) / p)

    # 3) Balance hidrostático aproximado (diferencias finitas)
    # dp/dz + rho*g = 0
    dp_dz = np.gradient(p, z)
    hydro_res = dp_dz + rho * G0
    # normalización por escala típica rho*g para obtener error relativo
    hydro_rel = np.abs(hydro_res) / np.maximum(np.abs(rho * G0), 1e-12)

    val = pd.DataFrame(
        {
            "metric": [
                "p_monotonic_decreasing",
                "rho_monotonic_decreasing",
                "max_rel_error_ideal_gas",
                "mean_rel_error_ideal_gas",
                "max_rel_error_hydrostatic",
                "mean_rel_error_hydrostatic",
                "T_surface_K",
                "p_surface_Pa",
                "rho_surface_kg_m3",
                "T_11km_K",
                "p_11km_Pa",
                "T_20km_K",
                "p_20km_Pa",
            ],
            "value": [
                float(monotonic_p),
                float(monotonic_rho),
                float(np.max(rel_err_ideal)),
                float(np.mean(rel_err_ideal)),
                float(np.max(hydro_rel)),
                float(np.mean(hydro_rel)),
                float(T[0]),
                float(p[0]),
                float(rho[0]),
                float(df.loc[df["z_m"] == 11000.0, "temperature_K"].iloc[0]),
                float(df.loc[df["z_m"] == 11000.0, "pressure_Pa"].iloc[0]),
                float(df.loc[df["z_m"] == 20000.0, "temperature_K"].iloc[0]),
                float(df.loc[df["z_m"] == 20000.0, "pressure_Pa"].iloc[0]),
            ],
        }
    )
    return val


def plot_profiles(df: pd.DataFrame, out_png: Path) -> None:
    z_km = df["z_km"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)

    axes[0].plot(df["temperature_K"], z_km, color="#1f77b4", lw=2)
    axes[0].set_xlabel("Temperatura [K]")
    axes[0].set_ylabel("Altura z [km]")
    axes[0].grid(alpha=0.3)

    axes[1].plot(df["pressure_hPa"], z_km, color="#d62728", lw=2)
    axes[1].set_xlabel("Presión [hPa]")
    axes[1].grid(alpha=0.3)

    axes[2].plot(df["density_kg_m3"], z_km, color="#2ca02c", lw=2)
    axes[2].set_xlabel(r"Densidad [$kg\,m^{-3}$]")
    axes[2].grid(alpha=0.3)

    for ax in axes:
        ax.set_ylim(0, 20)

    fig.suptitle("Atmósfera estándar (ISA): perfiles verticales 0–20 km", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    out_table = project_root / "results" / "tables" / "01_atmosfera_estandar.csv"
    out_val = project_root / "results" / "tables" / "01_atmosfera_estandar_validacion.csv"
    out_png = project_root / "results" / "plots" / "01_atmosfera_estandar.png"

    out_table.parent.mkdir(parents=True, exist_ok=True)
    out_png.parent.mkdir(parents=True, exist_ok=True)

    df = build_profiles(z_min_m=0.0, z_max_m=20000.0, dz_m=100.0)
    val = validate_profiles(df)

    df.to_csv(out_table, index=False)
    val.to_csv(out_val, index=False)
    plot_profiles(df, out_png)

    print("[OK] Tabla:", out_table)
    print("[OK] Validación:", out_val)
    print("[OK] Figura:", out_png)


if __name__ == "__main__":
    main()
