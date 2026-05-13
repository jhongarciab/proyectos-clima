# Proyecto 4 — Física del clima y cambio climático

Este proyecto desarrolla el **Mini Proyecto 4** sobre teleconexiones climáticas en el Eje Cafetero, evaluando la relación de la precipitación y la temperatura con los índices **Niño 3.4 (ENSO)** y **AMO** usando series mensuales y correlación cruzada con rezago.

## Objetivo del trabajo
1. Definir la región de estudio en el Eje Cafetero y seleccionar variables climáticas relevantes.
2. Descargar y organizar datos mensuales de **ERA5** y de índices climáticos de **NOAA PSL**.
3. Construir anomalías y series temporales comparables para precipitación, temperatura e índices.
4. Cuantificar teleconexiones mediante correlación de Pearson con rezago.
5. Identificar patrones espaciales y temporales de acoplamiento entre ENSO, AMO y el clima regional.
6. Integrar resultados, figuras y discusión en el entregable final.

## Estructura del repositorio
```text
proyecto 4/
├── datos/
│   └── crudos/
│       ├── era5/           # Datos ERA5 descargados
│       └── indices_noaa/   # Índices climáticos NOAA PSL (ENSO, AMO, etc.)
├── scripts/
│   ├── descargar_era5.py   # Descarga de datos ERA5
│   └── procesamiento.ipynb # Procesamiento, análisis y figuras
├── figuras/
│   ├── fig1_mapas_correlacion.png
│   ├── fig2_series_temporales.png
│   ├── fig3_correlograma.png
│   └── mapa.pdf            # Mapa de la región de estudio
├── docs/
│   ├── entregable.tex      # Documento principal en LaTeX
│   ├── entregable.pdf      # Entrega compilada
│   └── referencias_miniproyecto4.bib
└── README.md
```

## Orden recomendado de trabajo
1. `docs/entregable.tex` — revisar alcance, región de estudio y narrativa del trabajo.
2. `datos/crudos/indices_noaa/` + `datos/crudos/era5/` — organizar insumos base.
3. `scripts/descargar_era5.py` — reproducir o actualizar la descarga de ERA5 si hace falta.
4. `scripts/procesamiento.ipynb` — calcular anomalías, correlaciones rezagadas y generar salidas.
5. `figuras/` — revisar mapas, series temporales y correlogramas finales.
6. `docs/` — consolidar bibliografía, discusión y versión final del entregable.
