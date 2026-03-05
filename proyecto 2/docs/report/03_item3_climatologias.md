# MP2 — Ítem 3 (climatologías regionales)

## Estado
Completado (cálculo de climatología mensual regional + figura + tabla).

## Metodología
- Fuente: `data/raw/era5_surface_monthly_1996_2025.nc`.
- Variables: t2m, sp, u10, v10 y derivada ws10=√(u10²+v10²).
- Periodo: 1996–2025 (360 meses).
- Dominio: caja regional definida en el proyecto.
- Procedimiento: media espacial mensual ponderada por área (peso cos(lat)) y luego climatología por mes calendario (enero–diciembre), reportando media y desviación estándar interanual.

## Salidas
- Tabla: `results/tables/03_climatologia_mensual.csv`
- Figura: `results/plots/03_climatologia_mensual_superficie.png`

## Resumen numérico (promedio anual de la climatología mensual)
- Temperatura 2 m: media anual climatológica = 19.570 °C; variabilidad interanual media mensual = 0.662 °C
- Presión superficial: media anual climatológica = 847.960 hPa; variabilidad interanual media mensual = 0.424 hPa
- Viento zonal 10 m (u): media anual climatológica = 0.028 m s$^{-1}$; variabilidad interanual media mensual = 0.059 m s$^{-1}$
- Viento meridional 10 m (v): media anual climatológica = 0.040 m s$^{-1}$; variabilidad interanual media mensual = 0.060 m s$^{-1}$
- Rapidez del viento 10 m: media anual climatológica = 0.611 m s$^{-1}$; variabilidad interanual media mensual = 0.059 m s$^{-1}$