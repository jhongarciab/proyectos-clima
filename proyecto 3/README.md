# Replicación — Jakob et al. (2019)
## Radiative Convective Equilibrium and Organized Convection: An Observational Perspective
**DOI:** 10.1029/2018JD030092

---

## Estructura de carpetas

proyecto 3/
├── datos/
│   ├── ceres/raw/
│   ├── gpcp/raw/
│   ├── ncep/raw/
│   └── procesados/
├── figuras/
├── datos.ipynb          # Pipeline de datos
└── figuras.ipynb        # Figuras

---

## 1. CERES SYN1deg-Day Ed4.2

**Fuente:** https://ceres.larc.nasa.gov/data/
**Producto:** SYN1deg → SYN1deg-Day → Order Data
**Variables seleccionadas:**
- Observed TOA Fluxes → Net Flux → All Sky
- Adjusted All-Sky Profile Fluxes → Surface:
  - Shortwave Flux Up
  - Shortwave Flux Down
  - Longwave Flux Up
  - Longwave Flux Down

**Configuración:**
- Temporal Resolution: Daily
- Spatial Resolution: Regional (1° × 1° global grid)
- Satellite: Terra+Aqua/NOAA20 Edition 4.2
- Time Range: 01-2001 → 12-2009
- Format: NetCDF4

El sistema genera una orden y envía un email cuando los archivos
están listos. El email incluye un archivo fileURLs.txt.

**Descarga por batch:**

    mkdir -p datos/ceres/raw
    cd datos/ceres/raw

    wget --load-cookies ~/.urs_cookies \
         --save-cookies ~/.urs_cookies \
         --auth-no-challenge=on \
         --keep-session-cookies \
         --content-disposition \
         -i https://ceres-tool.larc.nasa.gov/ord-tool/data1//CERES_<ORDER_ID>/fileURLs.txt

Reemplazar <ORDER_ID> con el ID recibido por email.
Los archivos pesan ~968 MB cada uno. El servidor corta la conexión
varias veces pero wget retoma automáticamente desde donde se quedó.

---

## 2. GPCP Version 3.3 Daily (0.5°)

**Fuente:** https://disc.gsfc.nasa.gov/datasets/GPCPDAY_3.3/summary
**Requiere:** Cuenta NASA Earthdata con acceso a GES DISC autorizado

**Pasos en la interfaz:**
1. Ir a Subset/Get Data
2. Select Variables: precip únicamente
3. Date Range: 2001-01-01 → 2009-12-31
4. Format: NetCDF
5. Descargar el archivo .txt con la lista de URLs

**Descarga por batch:**

    mkdir -p datos/gpcp/raw
    cd datos/gpcp/raw

    wget --load-cookies ~/.urs_cookies \
         --save-cookies ~/.urs_cookies \
         --auth-no-challenge=on \
         --keep-session-cookies \
         --content-disposition \
         --wait=1 \
         -i ~/Downloads/subset_GPCPDAY_3_3_<timestamp>.txt

Se descargan ~3,287 archivos (~416 KB cada uno, ~1.5 GB total).
El --wait=1 evita saturar el servidor de NASA.
Resolución original: 0.5° × 0.5°. Se regridea a 1° × 1° en el pipeline.

---

## 3. NCEP Reanalysis 1 — Omega 500 hPa

**Fuente:** https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/pressure/
**Sin autenticación requerida**

    mkdir -p datos/ncep/raw
    cd datos/ncep/raw

    for year in {2001..2009}; do
        wget https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/pressure/omega.$year.nc
    done

9 archivos × ~113 MB = ~1 GB total.
Resolución: 2.5° × 2.5°, 12 niveles de presión.
En el pipeline se extrae únicamente el nivel 500 hPa.

---

## 4. NCEP Reanalysis 1 — Sensible Heat Flux

**Fuente:** https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Dailies/surface_gauss/
**Sin autenticación requerida**

    cd datos/ncep/raw

    for year in {2001..2009}; do
        wget https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Dailies/surface_gauss/shtfl.sfc.gauss.$year.nc
    done

9 archivos. Resolución gaussiana ~1.875° × ~1.904°.
Se interpola a 1° × 1° en el pipeline.

---

## Notas de replicabilidad

- Los datos de CERES corresponden a la Edición 4.2 (mayo 2025),
  mientras que Jakob (2019) usó la Edición 4a. Las diferencias en
  Q_R son menores a 2 W/m².
- GPCP v3.3 (0.5°) reemplaza al v1.2 (1°) usado por Jakob. La
  precipitación tropical media es ~18% mayor, lo que eleva D_RCE
  de 3.3 a ~17 W/m² en el promedio tropical. Los patrones
  espaciales son equivalentes.
- H (NCEP shtfl) reproduce exactamente el valor del paper: 22.6 W/m².
- El período de análisis es idéntico al paper: 2001–2009 (3,287 días).