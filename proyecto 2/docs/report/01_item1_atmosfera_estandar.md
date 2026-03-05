# MP2 — Ítem 1 (atmósfera estándar)

## Estado
Completado (cálculo + figura + validación numérica).

## Implementación
Script: `scripts/python/01_atmosfera_estandar.py`

Supuestos ISA en 0–20 km:
- 0–11 km: gradiente térmico constante `L=-6.5 K/km`
- 11–20 km: capa isotérmica con `T=216.65 K`

Constantes:
- `g0 = 9.80665 m/s²`
- `Rd = 287.05 J/(kg·K)`
- `T0 = 288.15 K`
- `p0 = 101325 Pa`

## Salidas
- Tabla principal: `results/tables/01_atmosfera_estandar.csv`
- Validación: `results/tables/01_atmosfera_estandar_validacion.csv`
- Figura: `results/plots/01_atmosfera_estandar.png`

## Verificación de resultados
- `p(z)` monótonamente decreciente: **sí**
- `rho(z)` monótonamente decreciente: **sí**
- Error relativo máximo ley de gases ideales: `2.62e-16`
- Error relativo medio balance hidrostático: `9.37e-05`

Puntos de control:
- `z=0 km`: `T=288.15 K`, `p=101325 Pa`, `rho=1.2250 kg/m³`
- `z=11 km`: `T=216.65 K`, `p=22631.7 Pa`
- `z=20 km`: `T=216.65 K`, `p=5474.7 Pa`
