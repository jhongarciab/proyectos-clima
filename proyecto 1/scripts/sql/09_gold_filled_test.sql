-- =============================================================================
-- QUALITY CHECKS — GOLD LAYER
-- Verificación final antes de exportar a Python para análisis
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. CONTEO DE FILAS Y NULLS
-- -----------------------------------------------------------------------------
SELECT
    'ideam_filled' AS fuente,
    COUNT(*) AS total_filas,
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END) AS nulls_temp,
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END) AS nulls_precip,
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END) AS nulls_hum
FROM gold.ideam_daily_filled
UNION ALL
SELECT
    'nasa',
    COUNT(*),
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)
FROM gold.nasa_daily;


-- -----------------------------------------------------------------------------
-- 2. GAPS EN EL CALENDARIO
-- No debe haber fechas faltantes
-- -----------------------------------------------------------------------------
SELECT
    'ideam_filled' AS fuente,
    COUNT(*) AS fechas_faltantes
FROM (
    SELECT generate_series('2015-01-01'::date, '2025-12-31'::date, '1 day')::date AS fecha
) cal
LEFT JOIN gold.ideam_daily_filled f ON f.fecha = cal.fecha
WHERE f.fecha IS NULL
UNION ALL
SELECT
    'nasa',
    COUNT(*)
FROM (
    SELECT generate_series('2015-01-01'::date, '2025-12-31'::date, '1 day')::date AS fecha
) cal
LEFT JOIN gold.nasa_daily n ON n.fecha = cal.fecha
WHERE n.fecha IS NULL;


-- -----------------------------------------------------------------------------
-- 3. ESTADÍSTICAS DESCRIPTIVAS
-- -----------------------------------------------------------------------------
SELECT
    'ideam_filled' AS fuente,
    ROUND(MIN(temperatura_c)::numeric,    2) AS temp_min,
    ROUND(MAX(temperatura_c)::numeric,    2) AS temp_max,
    ROUND(AVG(temperatura_c)::numeric,    2) AS temp_avg,
    ROUND(MIN(precipitacion_mm)::numeric, 2) AS precip_min,
    ROUND(MAX(precipitacion_mm)::numeric, 2) AS precip_max,
    ROUND(AVG(precipitacion_mm)::numeric, 2) AS precip_avg,
    ROUND(MIN(humedad_pct)::numeric,      2) AS hum_min,
    ROUND(MAX(humedad_pct)::numeric,      2) AS hum_max,
    ROUND(AVG(humedad_pct)::numeric,      2) AS hum_avg
FROM gold.ideam_daily_filled
UNION ALL
SELECT
    'nasa',
    ROUND(MIN(temperatura_c)::numeric,    2),
    ROUND(MAX(temperatura_c)::numeric,    2),
    ROUND(AVG(temperatura_c)::numeric,    2),
    ROUND(MIN(precipitacion_mm)::numeric, 2),
    ROUND(MAX(precipitacion_mm)::numeric, 2),
    ROUND(AVG(precipitacion_mm)::numeric, 2),
    ROUND(MIN(humedad_pct)::numeric,      2),
    ROUND(MAX(humedad_pct)::numeric,      2),
    ROUND(AVG(humedad_pct)::numeric,      2)
FROM gold.nasa_daily;


-- -----------------------------------------------------------------------------
-- 4. PERCENTILES — detectar outliers por variable
-- -----------------------------------------------------------------------------
SELECT
    'ideam_filled' AS fuente,
    percentile_cont(0.01) WITHIN GROUP (ORDER BY temperatura_c)    AS temp_p01,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY temperatura_c)    AS temp_p99,
    percentile_cont(0.01) WITHIN GROUP (ORDER BY precipitacion_mm) AS precip_p01,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY precipitacion_mm) AS precip_p99,
    percentile_cont(0.01) WITHIN GROUP (ORDER BY humedad_pct)      AS hum_p01,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY humedad_pct)      AS hum_p99
FROM gold.ideam_daily_filled
UNION ALL
SELECT
    'nasa',
    percentile_cont(0.01) WITHIN GROUP (ORDER BY temperatura_c),
    percentile_cont(0.99) WITHIN GROUP (ORDER BY temperatura_c),
    percentile_cont(0.01) WITHIN GROUP (ORDER BY precipitacion_mm),
    percentile_cont(0.99) WITHIN GROUP (ORDER BY precipitacion_mm),
    percentile_cont(0.01) WITHIN GROUP (ORDER BY humedad_pct),
    percentile_cont(0.99) WITHIN GROUP (ORDER BY humedad_pct)
FROM gold.nasa_daily;


-- -----------------------------------------------------------------------------
-- 5. OUTLIERS EXTREMOS POR VARIABLE
-- Valores fuera de rangos físicamente plausibles para Pereira
-- -----------------------------------------------------------------------------

-- Temperatura fuera de rango 15–30°C
SELECT 'ideam_filled' AS fuente, fecha, temperatura_c
FROM gold.ideam_daily_filled
WHERE temperatura_c < 15 OR temperatura_c > 30
UNION ALL
SELECT 'nasa', fecha, temperatura_c
FROM gold.nasa_daily
WHERE temperatura_c < 15 OR temperatura_c > 30
ORDER BY fuente, fecha;

-- Precipitación > 200 mm
SELECT 'ideam_filled' AS fuente, fecha, precipitacion_mm
FROM gold.ideam_daily_filled
WHERE precipitacion_mm > 200
UNION ALL
SELECT 'nasa', fecha, precipitacion_mm
FROM gold.nasa_daily
WHERE precipitacion_mm > 200
ORDER BY fuente, fecha;

-- Humedad fuera de rango 40–100%
SELECT 'ideam_filled' AS fuente, fecha, humedad_pct
FROM gold.ideam_daily_filled
WHERE humedad_pct < 40 OR humedad_pct > 100
UNION ALL
SELECT 'nasa', fecha, humedad_pct
FROM gold.nasa_daily
WHERE humedad_pct < 40 OR humedad_pct > 100
ORDER BY fuente, fecha;