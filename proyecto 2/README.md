# Proyecto 2 — Física del clima y cambio climático

Mini Proyecto 2 centrado en:
- atmósfera estándar ISA,
- climatologías regionales ERA5,
- exportación de capas para QGIS,
- comparación geostrófica en niveles de presión,
- perfil vertical de temperatura frente a ISA,
- entregable final en LaTeX.

## Estructura actual

```text
proyecto 2/
├── data/
│   ├── raw/            # NetCDF y requests JSON descargados desde ERA5/CDS
│   └── processed/      # Reservado para productos intermedios
├── scripts/
│   └── python/
│       ├── 00_config_mp2.py
│       ├── 01_atmosfera_estandar.py
│       ├── 02_download_era5_surface_monthly.py
│       ├── 02b_download_era5_pressure_monthly.py
│       ├── 03_climatologias_regionales.py
│       ├── 03c_item3_mapas_cartograficos.py
│       ├── 03d_capas_qgis.py
│       ├── 04b_geostrofia_nivel_presion.py
│       └── 05_perfil_vertical_comparacion.py
├── notebooks/          # Exploración puntual (no central al flujo final)
├── docs/
│   ├── references/     # Alcance, fuente ERA5 y decisiones de trabajo
│   ├── report/         # Notas de redacción por ítem
│   └── tex/            # Entregable final en LaTeX
└── results/
    ├── plots/          # Figuras finales en PDF
    ├── qgis/           # GeoTIFF/GeoJSON para composición en QGIS
    └── tables/         # Tablas y métricas finales en CSV
```

## Datos esperados en `data/raw/`

- `era5_surface_monthly_1996_2025.nc`
- `era5_surface_request.json`
- `era5_pressure_monthly_1996_2025.nc`
- `era5_pressure_request.json`

## Scripts principales

### 00_config_mp2.py
Configuración central del dominio, periodo, variables de superficie y niveles de presión.

### 01_atmosfera_estandar.py
Construye la atmósfera estándar ISA hasta 86 km, exporta tablas de validación y figuras finales.

### 02_download_era5_surface_monthly.py
Descarga ERA5 monthly means de superficie para el dominio aprobado.

### 02b_download_era5_pressure_monthly.py
Descarga ERA5 monthly means en niveles de presión para el ítem de geostrofía/perfil vertical.

### 03_climatologias_regionales.py
Genera climatologías medias y exporta GeoTIFF + GeoJSON base para QGIS.

### 03c_item3_mapas_cartograficos.py
Produce los mapas finales del ítem 3 a partir de las capas preparadas.

### 03d_capas_qgis.py
Genera capas auxiliares para QGIS: isotermas y ciudades.

### 04b_geostrofia_nivel_presion.py
Evalúa la aproximación geostrófica en múltiples niveles de presión y exporta métricas/figuras.

### 05_perfil_vertical_comparacion.py
Compara el perfil vertical ERA5 vs ISA usando niveles de presión y exporta métricas/figuras.

## Salidas finales esperadas

### `results/plots/`
- `01_atmosfera_estandar_full.pdf`
- `01_atmosfera_estandar_zoom.pdf`
- `mapa_temp_qgis.pdf`
- `mapa_press_qgis.pdf`
- `04_geostrofia_comparacion.pdf`
- `04_geostrofia_rmse_por_nivel.pdf`
- `05_perfil_vertical_temperatura.pdf`
- `05_perfil_vertical_diferencia.pdf`

### `results/qgis/`
- `t2m_climatologia.tif`
- `sp_climatologia.tif`
- `u10_climatologia.tif`
- `v10_climatologia.tif`
- `ws10_climatologia.tif`
- `isobaras_presion.geojson`
- `isotermas_temperatura.geojson`
- `viento_vectores.geojson`
- `ciudades.geojson`

### `results/tables/`
- `01_atmosfera_estandar.csv`
- `01_atmosfera_estandar_validacion.csv`
- `03_climatologia_mensual.csv`
- `04_geostrofia_metricas_nivel.csv`
- `04_geostrofia_metricas_todos_niveles.csv`
- `05_perfil_vertical.csv`
- `05_perfil_vertical_metricas.csv`

## Nota
El entregable `.tex` todavía puede seguir refinándose, pero el flujo principal de datos, scripts y resultados queda organizado alrededor de los archivos finales realmente usados en esta entrega.
