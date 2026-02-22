# Data Sources and Coverage (Project 1)

## Objective
Document the selected data sources for climate analysis in **Pereira (Risaralda, Colombia)**, including spatial scale, temporal scale, available variables, and access format.

---

## 1) IDEAM (Colombia) — observational station data

### Platform
- Open data portal: **datos.gov.co** (publisher: IDEAM).

### Datasets (selected climate variables)
- **Air temperature** — `sbwg-7ju4`
- **Precipitation** — `s54a-sgyg`
- **Air humidity** — `uext-mhny`

### Spatial scale
- Point/station observations across Colombia.
- Project focus: Risaralda (Pereira and nearby station coverage when needed).

### Temporal scale
- Native observations at sub-daily frequency (sensor-level records).
- Aggregated to **daily** values for this project.

### Access format
- Socrata API (`.json`) and portal export.

---

## 2) NASA POWER — gridded daily climate data

### Platform
- NASA POWER API:
  `https://power.larc.nasa.gov/api/temporal/daily/point`

### Variables selected for comparison
- `T2M` (temperature at 2m)
- `PRECTOTCORR` (corrected precipitation)
- `RH2M` (relative humidity at 2m)

### Spatial scale
- Gridded product queried at a geographic point (Pereira coordinates).

### Temporal scale
- **Daily** time series.

### Access format
- API response in CSV/JSON.

---

## Coverage summary for this project

- **Location:** Pereira, Risaralda, Colombia.
- **Period:** 2015–2025 (daily).
- **Core variables:** temperature, precipitation, humidity.
- **Sources:** IDEAM + NASA POWER.

## Why these two sources
- IDEAM provides local observational station data.
- NASA POWER provides a consistent gridded daily reference.
- Together they satisfy the requirement of comparing common variables across two different databases.
