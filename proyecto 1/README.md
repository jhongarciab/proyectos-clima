# Proyecto 1 — Física del clima y cambio climático

Este proyecto analiza clima para un sitio de interés usando **10 años de datos diarios** y comparando variables comunes entre fuentes.

## Objetivo del trabajo
1. Identificar y describir fuentes de datos para el lugar de interés (escala espacial y temporal).
2. Seleccionar variables comunes (temperatura, precipitación y humedad) en al menos dos fuentes.
3. Descargar, homologar unidades y evaluar calidad (faltantes/missing values).
4. Analizar series y anomalías (diaria, mensual, anual y estacional).
5. Analizar distribuciones (histogramas diarios) y espectro (Fourier).
6. Presentar conclusiones.

## Estructura del repositorio
```text
proyecto 1/
├── data/
│   ├── raw/            # Datos descargados sin modificar
│   └── processed/      # Datos limpios y homologados
├── scripts/            # Scripts de descarga, limpieza y análisis
├── notebooks/          # Exploración y análisis reproducible
├── docs/
│   ├── references/     # Descripción de fuentes y variables
│   ├── tex/            # Trabajo final
│   └── report/         # Entrega escrita (borrador/final)
└── results/
    └── plots/          # Gráficos generados (series, anomalías, histogramas)
```

## Orden recomendado de trabajo
1. `docs/references/` — registrar fuentes y cobertura de datos.
2. `data/raw/` — descargar datos.
3. `scripts/` + `data/processed/` — preprocesar (unidades, faltantes, calidad).
4. `results/plots/` + `docs/figures/` — generar y seleccionar gráficos.
5. `docs/report/` — redactar conclusiones y versión final.
