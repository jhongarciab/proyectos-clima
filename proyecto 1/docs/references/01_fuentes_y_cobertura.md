# Fuentes de datos y cobertura (Proyecto 1)

## Objetivo de esta sección
Registrar las fuentes de datos para el análisis climático de **Pereira (Risaralda)**, indicando cobertura espacial y temporal, variables disponibles y formato de acceso.

---

## IDEAM (Colombia) — datos observacionales

### Plataforma
- Portal de datos abiertos: **datos.gov.co** (publicador: IDEAM / Instituto de Hidrología, Meteorología y Estudios Ambientales).

### Datasets seleccionados (variables clásicas)
- **Temperatura ambiente del aire**  
  ID: `sbwg-7ju4`
- **Precipitación**  
  ID: `s54a-sgyg`
- **Humedad del aire**  
  ID: `uext-mhny`

### Cobertura espacial
- Estaciones meteorológicas en Colombia.
- Para este proyecto: filtro por departamento **Risaralda** y municipio **Pereira** (o estaciones cercanas con mejor continuidad).

### Cobertura temporal
- Series con observaciones históricas (a validar por estación).
- Meta del proyecto: construir una serie diaria de al menos **10 años**.

### Resolución temporal
- Registro observacional por estación/sensor; posteriormente se agregará a escala diaria para el análisis.

### Formato y acceso
- API Socrata (`.json`) y descarga desde portal.
- Campos típicos: estación, fecha, valor observado, municipio, departamento, lat/lon, unidad.

### Observaciones para el preprocesamiento
- Verificar unidades por variable.
- Homologar frecuencia temporal (diaria).
- Identificar missing values y porcentaje de faltantes.

---

## Resumen de cobertura para el proyecto

- **Lugar de interés:** Pereira, Risaralda, Colombia.
- **Escala temporal objetivo:** 10 años de datos diarios.
- **Variables foco:** temperatura, precipitación, humedad.
- **Fuente de datos:** únicamente IDEAM (3 datasets seleccionados).
- **Estrategia:**
  1. Filtrar por Risaralda/Pereira.
  2. Estandarizar unidades y tratar faltantes.
  3. Construir series diarias y análisis (anomalías, histogramas y Fourier).
