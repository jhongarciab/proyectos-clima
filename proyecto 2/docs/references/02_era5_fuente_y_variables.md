# MP2 — Ítem 2: fuente de datos y variables (superficie)

Para el desarrollo del ítem 2 se adoptó ERA5 como fuente principal de reanálisis, usando el producto de promedios mensuales en niveles de superficie (`reanalysis-era5-single-levels-monthly-means`).

La extracción se configuró sobre el dominio aprobado del proyecto: 5.5°N–4.0°N y -76.5°–-75.0°, para el periodo 1996–2025. El conjunto de variables solicitado corresponde exactamente a lo requerido por el enunciado para superficie: temperatura del aire a 2 m, presión en superficie y componentes zonal/meridional del viento a 10 m.

Variables solicitadas:
- `2m_temperature`
- `surface_pressure`
- `10m_u_component_of_wind`
- `10m_v_component_of_wind`

Formato de descarga: NetCDF (`.nc`).

Scripts asociados:
- `scripts/python/00_config_mp2.py`
- `scripts/python/02_download_era5_surface_monthly.py`
