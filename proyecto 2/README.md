# Proyecto 2 — Física del clima y cambio climático

Estructura base del MP2, siguiendo el flujo de trabajo del MP1.

## Objetivo general
Implementar el análisis de atmósfera estándar, climatologías regionales de reanálisis,
comparación geostrófica y perfil vertical de temperatura según el enunciado del Mini Proyecto 2.

## Estructura
```text
proyecto 2/
├── data/
│   ├── raw/            # Datos descargados sin modificar (reanálisis/DEM)
│   └── processed/      # Datos limpios y transformados para análisis
├── scripts/
│   ├── python/         # Descarga, limpieza, cálculos y gráficas
│   └── sql/            # (Opcional) consultas/transformaciones tabulares
├── notebooks/          # Exploración y validación reproducible
├── docs/
│   ├── references/     # Fuentes, cobertura, variables y decisiones
│   ├── report/         # Borradores y narrativa de resultados
│   └── tex/            # Entregable en LaTeX
└── results/
    ├── plots/          # Figuras finales
    └── tables/         # Tablas y métricas comparativas
```
