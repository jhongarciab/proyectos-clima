-- =============================================================================
-- GOLD LAYER: Final analytical views for IDEAM and NASA POWER.
--
-- Responsibilities of this layer:
--   1. Compute daily station-averaged values for IDEAM by variable and date.
--   2. Construct a complete calendar backbone (2015–2025).
--   3. Expose both data sources with identical analytical structure.
--
-- Views:
--   gold.ideam_daily  — Daily average across selected IDEAM stations
--   gold.nasa_daily   — NASA POWER daily series (analysis-ready structure)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. IDEAM DAILY
-- Daily averages computed across available stations for each variable.
-- The complete calendar ensures that every date in the analysis period
-- appears exactly once, with NULL values when no station reports data.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.ideam_daily AS
WITH calendario AS (
    SELECT generate_series(
        '2015-01-01'::date,
        '2025-12-31'::date,
        '1 day'::interval
    )::date AS fecha
),
temp AS (
    SELECT fecha, AVG(valor_diario_c) AS temperatura_c
    FROM silver.ideam_temperature
    GROUP BY fecha
),
precip AS (
    SELECT fecha, AVG(valor_diario_mm) AS precipitacion_mm
    FROM silver.ideam_precipitation
    GROUP BY fecha
),
hum AS (
    SELECT fecha, AVG(valor_diario_pct) AS humedad_pct
    FROM silver.ideam_humidity
    GROUP BY fecha
)
SELECT
    c.fecha,
    t.temperatura_c,
    p.precipitacion_mm,
    h.humedad_pct
FROM calendario c
LEFT JOIN temp    t ON t.fecha = c.fecha
LEFT JOIN precip  p ON p.fecha = c.fecha
LEFT JOIN hum     h ON h.fecha = c.fecha
ORDER BY c.fecha;


-- -----------------------------------------------------------------------------
-- 2. NASA DAILY
-- NASA POWER daily time series restricted to analytical variables only.
-- Auxiliary columns from the Silver layer are intentionally excluded.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.nasa_daily AS
SELECT
    fecha,
    temperatura_c,
    precipitacion_mm,
    humedad_pct
FROM silver.nasa_daily
ORDER BY fecha;


-- -----------------------------------------------------------------------------
-- Sanity checks
-- -----------------------------------------------------------------------------

-- Both views must contain exactly 4,018 rows (2015–2025 inclusive).
SELECT 'ideam' AS fuente, COUNT(*) AS n_filas FROM gold.ideam_daily
UNION ALL
SELECT 'nasa',            COUNT(*) FROM gold.nasa_daily;

-- Compare NULL counts per variable across both sources.
SELECT
    'ideam'                                                                  AS fuente,
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END)                AS nulos_temp,
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END)                AS nulos_precip,
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)                AS nulos_humedad
FROM gold.ideam_daily
UNION ALL
SELECT
    'nasa',
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)
FROM gold.nasa_daily;

-- Preview first rows from each source.
SELECT 'ideam' AS fuente, * FROM gold.ideam_daily LIMIT 5;
SELECT 'nasa'  AS fuente, * FROM gold.nasa_daily  LIMIT 5;