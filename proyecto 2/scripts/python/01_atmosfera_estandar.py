#!/usr/bin/env python3
"""
Ítem 1 — Mini Proyecto 2
Perfiles verticales de T(z), p(z) y rho(z) usando la Atmósfera Estándar ISA (1976)
hasta 86 km (troposfera, estratosfera y mesosfera completa).

Capas ISA oficiales (ICAO/ISO 2533:1975):
  0   –  11 km : L = -6.5  K/km  (troposfera)
  11  –  20 km : L =  0.0  K/km  (estratosfera baja, isotérmica)
  20  –  32 km : L = +1.0  K/km  (estratosfera media)
  32  –  47 km : L = +2.8  K/km  (estratosfera alta)
  47  –  51 km : L =  0.0  K/km  (estratopausa, isotérmica)
  51  –  71 km : L = -2.8  K/km  (mesosfera baja)
  71  –  86 km : L = -2.0  K/km  (mesosfera alta)

Salidas:
- results/tables/01_atmosfera_estandar.csv
- results/tables/01_atmosfera_estandar_validacion.csv
- results/plots/01_atmosfera_estandar_full.pdf   (0-86 km)
- results/plots/01_atmosfera_estandar_zoom.pdf   (0-20 km)
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Tipografía estilo LaTeX sin depender de una instalación TeX externa.
# Si en tu equipo tienes LaTeX instalado, reemplaza las dos primeras líneas por:
#   matplotlib.rcParams["text.usetex"] = True
#   matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams.update({
    "text.usetex":        False,
    "font.family":        "serif",
    "font.serif":         ["DejaVu Serif", "Georgia", "Times New Roman", "serif"],
    "font.size":          12,
    "axes.labelsize":     12,
    "xtick.labelsize":    10,
    "ytick.labelsize":    10,
    "legend.fontsize":    10,
    "axes.titlesize":     12,
})

# ─────────────────────────────────────────
# Constantes físicas
# ─────────────────────────────────────────
G0  = 9.80665    # gravedad estándar   [m s^-2]
R_D = 287.05     # constante aire seco [J kg^-1 K^-1]
P0  = 101325.0   # presión en z=0      [Pa]
T0  = 288.15     # temperatura en z=0  [K]

# Exponente adimensional troposférico: alpha = g0 / (Rd * |L|) ≈ 5.2559
ALPHA_TROPO = G0 / (R_D * 0.0065)

# ─────────────────────────────────────────
# Capas ISA
# ─────────────────────────────────────────
ISA_LAYERS = [
    (     0.0, 288.15, -0.0065, "Troposfera"),
    ( 11_000.0, 216.65,  0.0000, "Estratosfera baja"),
    ( 20_000.0, 216.65, +0.0010, "Estratosfera media"),
    ( 32_000.0, 228.65, +0.0028, "Estratosfera alta"),
    ( 47_000.0, 270.65,  0.0000, "Estratopausa"),
    ( 51_000.0, 270.65, -0.0028, "Mesosfera baja"),
    ( 71_000.0, 214.65, -0.0020, "Mesosfera alta"),
]
Z_MAX = 86_000.0  # [m]


def _p_top(z_base, z_top, T_base, L, p_base):
    if abs(L) < 1e-12:
        return p_base * np.exp(-G0 * (z_top - z_base) / (R_D * T_base))
    T_top = T_base + L * (z_top - z_base)
    return p_base * (T_top / T_base) ** (-G0 / (R_D * L))


def build_profiles(dz_m: float = 100.0) -> pd.DataFrame:
    z = np.arange(0.0, Z_MAX + dz_m, dz_m)
    T = np.empty_like(z)
    p = np.empty_like(z)

    layer_bases = []
    T_b, p_b = T0, P0
    for i, (z_base, _, L, _) in enumerate(ISA_LAYERS):
        z_top = ISA_LAYERS[i + 1][0] if i + 1 < len(ISA_LAYERS) else Z_MAX
        layer_bases.append((z_base, T_b, p_b, L))
        p_b = _p_top(z_base, z_top, T_b, L, p_b)
        T_b = T_b if abs(L) < 1e-12 else T_b + L * (z_top - z_base)

    for k, (z_base, T_base, p_base, L) in enumerate(layer_bases):
        z_top_layer = layer_bases[k + 1][0] if k + 1 < len(layer_bases) else Z_MAX
        mask = (z >= z_base) & (z <= z_top_layer)
        dz = z[mask] - z_base
        if abs(L) < 1e-12:
            T[mask] = T_base
            p[mask] = p_base * np.exp(-G0 * dz / (R_D * T_base))
        else:
            T[mask] = T_base + L * dz
            p[mask] = p_base * (T[mask] / T_base) ** (-G0 / (R_D * L))

    rho = p / (R_D * T)

    return pd.DataFrame({
        "z_m":           z,
        "z_km":          z / 1000.0,
        "temperature_K": T,
        "temperature_C": T - 273.15,
        "pressure_Pa":   p,
        "pressure_hPa":  p / 100.0,
        "density_kg_m3": rho,
    })


# ─────────────────────────────────────────
# Validación
# ─────────────────────────────────────────
ISA_REFERENCE = {
     0.0: (288.15, 101325.0,   1.2250),
    11.0: (216.65,  22632.1,   0.3639),
    20.0: (216.65,   5474.9,   0.0880),
    32.0: (228.65,    868.02,  0.01323),
    47.0: (270.65,    110.91,  0.001427),
    51.0: (270.65,     66.94,  0.0008616),
    71.0: (214.65,      3.956, 0.00006420),
    86.0: (186.87,      0.3734, 0.000006958),
}


def validate_profiles(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    p   = df["pressure_Pa"].to_numpy()
    rho = df["density_kg_m3"].to_numpy()
    T   = df["temperature_K"].to_numpy()
    z   = df["z_m"].to_numpy()

    rows.append(("p_monotonic_decreasing",   float(np.all(np.diff(p)   < 0))))
    rows.append(("rho_monotonic_decreasing", float(np.all(np.diff(rho) < 0))))

    rel_ideal = np.abs(p - rho * R_D * T) / p
    rows.append(("max_rel_error_ideal_gas_%",  float(np.max(rel_ideal)  * 100)))
    rows.append(("mean_rel_error_ideal_gas_%", float(np.mean(rel_ideal) * 100)))

    dp_dz = np.gradient(p, z)
    hydro = np.abs(dp_dz + rho * G0) / np.maximum(np.abs(rho * G0), 1e-12)
    rows.append(("max_rel_error_hydrostatic_%",  float(np.max(hydro)  * 100)))
    rows.append(("mean_rel_error_hydrostatic_%", float(np.mean(hydro) * 100)))

    for z_km, (T_ref, p_ref, rho_ref) in ISA_REFERENCE.items():
        row = df[np.isclose(df["z_km"], z_km, atol=0.05)].iloc[0]
        rows.append((f"T_err_%_at_{z_km:.0f}km",
                     abs(row["temperature_K"] - T_ref)   / T_ref   * 100))
        rows.append((f"p_err_%_at_{z_km:.0f}km",
                     abs(row["pressure_Pa"]   - p_ref)   / p_ref   * 100))
        rows.append((f"rho_err_%_at_{z_km:.0f}km",
                     abs(row["density_kg_m3"] - rho_ref) / rho_ref * 100))

    return pd.DataFrame(rows, columns=["metric", "value"])


# ─────────────────────────────────────────
# Visualización
# ─────────────────────────────────────────
COLORS = {"T": "#1f77b4", "p": "#d62728", "rho": "#2ca02c"}

LAYER_BANDS = [
    (  0,  11, "#cce5ff", "Troposfera"),
    ( 11,  20, "#d4edda", "Est. baja"),
    ( 20,  32, "#c3e6cb", "Est. media"),
    ( 32,  47, "#b1dfbb", "Est. alta"),
    ( 47,  51, "#ffeeba", "Estratopausa"),
    ( 51,  71, "#f5c6cb", "Mesos. baja"),
    ( 71,  86, "#f1b0b7", "Mesos. alta"),
]


def _add_layer_bands(ax, z_min: float, z_max: float) -> None:
    """Bandas de color + etiquetas en el margen derecho."""
    for z0, z1, color, label in LAYER_BANDS:
        if z1 <= z_min or z0 >= z_max:
            continue
        z0c, z1c = max(z0, z_min), min(z1, z_max)
        ax.axhspan(z0c, z1c, color=color, alpha=0.22, zorder=0)
        mid = (z0c + z1c) / 2
        ax.text(0.988, mid, label,
                transform=ax.get_yaxis_transform(),
                fontsize=7, va="center", ha="right",
                color="#444444", style="italic")


def plot_spine_sharing(df: pd.DataFrame, out_pdf: Path,
                       z_min_km: float, z_max_km: float,
                       title_suffix: str) -> None:
    """
    Spine sharing: 1 eje Y compartido, 3 ejes X lineales independientes.
    Cada eje secundario tiene su spine visible como línea de referencia.
    Etiquetas de capa en el lado derecho. Exporta PDF.
    """
    mask = (df["z_km"] >= z_min_km) & (df["z_km"] <= z_max_km)
    sub  = df[mask].copy()

    fig, ax_T = plt.subplots(figsize=(7, 9))
    fig.subplots_adjust(bottom=0.24)

    # ── Temperatura ─────────────────────────────────────────────────────────
    ax_T.plot(sub["temperature_K"], sub["z_km"], color=COLORS["T"], lw=1.8)
    ax_T.set_xlabel("Temperatura [K]", color=COLORS["T"], labelpad=6)
    ax_T.tick_params(axis="x", colors=COLORS["T"])
    ax_T.spines["bottom"].set_color(COLORS["T"])
    ax_T.spines["bottom"].set_linewidth(1.2)
    ax_T.spines["bottom"].set_position(("outward", 0))
    ax_T.set_ylabel(r"Altitud $z$ [km]")
    ax_T.set_ylim(z_min_km, z_max_km)
    ax_T.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax_T.grid(axis="y", alpha=0.25, lw=0.6)
    for side in ("top", "right"):
        ax_T.spines[side].set_visible(False)
    _add_layer_bands(ax_T, z_min_km, z_max_km)

    # ── Presión — spine en outward=62 ────────────────────────────────────────
    ax_p = ax_T.twiny()
    ax_p.set_frame_on(False)
    ax_p.xaxis.set_ticks_position("bottom")
    ax_p.xaxis.set_label_position("bottom")
    ax_p.spines["bottom"].set_visible(True)
    ax_p.spines["bottom"].set_position(("outward", 62))
    ax_p.spines["bottom"].set_color(COLORS["p"])
    ax_p.spines["bottom"].set_linewidth(1.2)
    ax_p.plot(sub["pressure_hPa"], sub["z_km"],
              color=COLORS["p"], lw=1.8, ls="--")
    ax_p.set_xlabel("Presión [hPa]", color=COLORS["p"], labelpad=6)
    ax_p.tick_params(axis="x", colors=COLORS["p"])
    ptp_p = sub["pressure_hPa"].max() - sub["pressure_hPa"].min()
    ax_p.set_xlim(sub["pressure_hPa"].min() - 0.04 * ptp_p,
                  sub["pressure_hPa"].max() + 0.04 * ptp_p)
    ax_p.set_ylim(z_min_km, z_max_km)

    # ── Densidad — spine en outward=124 ──────────────────────────────────────
    ax_rho = ax_T.twiny()
    ax_rho.set_frame_on(False)
    ax_rho.xaxis.set_ticks_position("bottom")
    ax_rho.xaxis.set_label_position("bottom")
    ax_rho.spines["bottom"].set_visible(True)
    ax_rho.spines["bottom"].set_position(("outward", 124))
    ax_rho.spines["bottom"].set_color(COLORS["rho"])
    ax_rho.spines["bottom"].set_linewidth(1.2)
    ax_rho.plot(sub["density_kg_m3"], sub["z_km"],
                color=COLORS["rho"], lw=1.8, ls=":")
    ax_rho.set_xlabel(r"Densidad [kg m$^{-3}$]", color=COLORS["rho"], labelpad=6)
    ax_rho.tick_params(axis="x", colors=COLORS["rho"])
    ptp_rho = sub["density_kg_m3"].max() - sub["density_kg_m3"].min()
    ax_rho.set_xlim(sub["density_kg_m3"].min() - 0.04 * ptp_rho,
                    sub["density_kg_m3"].max() + 0.04 * ptp_rho)
    ax_rho.set_ylim(z_min_km, z_max_km)

    ax_T.set_title(
        "Atmósfera estándar ISA — Perfiles Verticales",
        pad=10,
    )

    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Figura: {out_pdf}")


# ─────────────────────────────────────────
# main
# ─────────────────────────────────────────
def main() -> None:
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    out_table = project_root / "results" / "tables" / "01_atmosfera_estandar.csv"
    out_val   = project_root / "results" / "tables" / "01_atmosfera_estandar_validacion.csv"
    out_full  = project_root / "results" / "plots"  / "01_atmosfera_estandar_full.pdf"
    out_zoom  = project_root / "results" / "plots"  / "01_atmosfera_estandar_zoom.pdf"

    out_table.parent.mkdir(parents=True, exist_ok=True)
    out_full.parent.mkdir(parents=True, exist_ok=True)

    df  = build_profiles(dz_m=100.0)
    val = validate_profiles(df)

    df.to_csv(out_table, index=False)
    val.to_csv(out_val,  index=False)
    print(f"[OK] Tabla:      {out_table}")
    print(f"[OK] Validacion: {out_val}")

    plot_spine_sharing(df, out_full, z_min_km=0, z_max_km=86,
                       title_suffix="0-86 km")
    plot_spine_sharing(df, out_zoom, z_min_km=0, z_max_km=20,
                       title_suffix="0-20 km (foco del trabajo)")

    print("\n-- Validacion contra tabla ISA oficial --")
    print(val.to_string(index=False))


if __name__ == "__main__":
    main()