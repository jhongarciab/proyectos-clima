# MP2 — Ítem 2 (estado)

## Avance realizado
1. Se definió formalmente la fuente ERA5 y el dataset mensual de niveles de superficie.
2. Se codificó script de descarga reproducible con request persistente en JSON.
3. Se fijaron variables y dominio en archivo de configuración central.

## Cierre del ítem 2
Descarga ejecutada con credenciales CDS y archivo generado:
- `data/raw/era5_surface_monthly_1996_2025.nc`

Validación rápida del NetCDF descargado:
- Variables: `t2m`, `sp`, `u10`, `v10`
- Tiempo: 360 meses (`1996-01` a `2025-12`)
- Malla espacial: 7 latitudes x 7 longitudes
