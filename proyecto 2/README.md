# Proyecto 2 — Física del clima y cambio climático

Este proyecto desarrolla el **Mini Proyecto 2** usando atmósfera estándar y datos ERA5 mensuales para análisis regional, comparación dinámica y perfil vertical.

## Objetivo del trabajo
1. Construir y validar la atmósfera estándar ISA.
2. Descargar y organizar climatologías regionales ERA5 de superficie.
3. Exportar capas y mapas climatológicos para apoyo cartográfico en QGIS.
4. Evaluar la aproximación geostrófica usando niveles de presión.
5. Comparar el perfil vertical de temperatura ERA5 con la atmósfera estándar.
6. Integrar resultados en el entregable final.

## Estructura del repositorio
```text
proyecto 2/
├── data/
│   ├── raw/            # Datos descargados sin modificar (ERA5/CDS)
│   └── processed/      # Datos intermedios o transformados
├── scripts/
│   └── python/         # Descarga, cálculos, exportación y figuras
├── notebooks/          # Exploración y validación reproducible
├── docs/
│   ├── references/     # Alcance, fuentes y decisiones de trabajo
│   ├── tex/            # Entregable final en LaTeX
│   └── report/         # Borradores/notas por ítem
└── results/
    ├── plots/          # Figuras finales
    ├── qgis/           # Capas GeoTIFF y GeoJSON para QGIS
    └── tables/         # Tablas y métricas exportadas
```

## Orden recomendado de trabajo
1. `docs/references/` — registrar alcance, variables y cobertura.
2. `data/raw/` — descargar ERA5 de superficie y niveles de presión.
3. `scripts/python/01...02...` — construir atmósfera estándar y preparar datos base.
4. `scripts/python/03...` + `results/qgis/` — generar climatologías y capas para QGIS.
5. `scripts/python/04...05...` + `results/plots/` + `results/tables/` — producir métricas y figuras finales.
6. `docs/tex/` y `docs/report/` — consolidar la entrega escrita.
