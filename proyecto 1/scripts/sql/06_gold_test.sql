-- =============================================================================
-- GOLD LAYER — VALIDATION TESTS
-- Verifies that Gold layer views are correctly constructed and ready
-- for analytical consumption.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- T01. Both views contain exactly 4,018 rows
--       (Period: 2015-01-01 to 2025-12-31)
-- Expected: 4,018 rows in each view
-- -----------------------------------------------------------------------------
SELECT 'ideam' AS fuente, COUNT(*) AS n_filas FROM gold.ideam_daily
UNION ALL
SELECT 'nasa',             COUNT(*) FROM gold.nasa_daily;

-- -----------------------------------------------------------------------------
-- T02. No duplicate dates in either view
-- Expected: 0 rows returned for both sources
-- -----------------------------------------------------------------------------
SELECT 'ideam' AS fuente, fecha, COUNT(*) AS n
FROM gold.ideam_daily
GROUP BY fecha HAVING COUNT(*) > 1
UNION ALL
SELECT 'nasa', fecha, COUNT(*)
FROM gold.nasa_daily
GROUP BY fecha HAVING COUNT(*) > 1;


-- -----------------------------------------------------------------------------
-- T03. No calendar gaps (continuous daily coverage without missing dates)
-- Expected: 0 rows returned for both sources
-- -----------------------------------------------------------------------------
WITH calendario AS (
    SELECT generate_series(
        '2015-01-01'::date,
        '2025-12-31'::date,
        '1 day'::interval
    )::date AS fecha
)
SELECT 'ideam' AS fuente, c.fecha AS fecha_faltante
FROM calendario c LEFT JOIN gold.ideam_daily i ON i.fecha = c.fecha
WHERE i.fecha IS NULL
UNION ALL
SELECT 'nasa', c.fecha
FROM calendario c LEFT JOIN gold.nasa_daily n ON n.fecha = c.fecha
WHERE n.fecha IS NULL;


-- -----------------------------------------------------------------------------
-- T04. Physically plausible ranges (NULL values ignored)
-- Expected: 0 rows returned in each validation query
-- -----------------------------------------------------------------------------
-- Temperature outside plausible range (5–40 °C)
SELECT 'ideam' AS fuente, fecha, temperatura_c
FROM gold.ideam_daily
WHERE temperatura_c < 5 OR temperatura_c > 40
UNION ALL
SELECT 'nasa', fecha, temperatura_c
FROM gold.nasa_daily
WHERE temperatura_c < 5 OR temperatura_c > 40;

-- Humidity outside physical bounds (1–100 %)
SELECT 'ideam' AS fuente, fecha, humedad_pct
FROM gold.ideam_daily
WHERE humedad_pct < 1 OR humedad_pct > 100
UNION ALL
SELECT 'nasa', fecha, humedad_pct
FROM gold.nasa_daily
WHERE humedad_pct < 1 OR humedad_pct > 100;

-- Negative precipitation values
SELECT 'ideam' AS fuente, fecha, precipitacion_mm
FROM gold.ideam_daily
WHERE precipitacion_mm < 0
UNION ALL
SELECT 'nasa', fecha, precipitacion_mm
FROM gold.nasa_daily
WHERE precipitacion_mm < 0;


-- -----------------------------------------------------------------------------
-- T05. NULL summary by variable and data source
-- Informational: no fixed expected value.
-- Used to document final data coverage in the Gold layer.
-- -----------------------------------------------------------------------------
SELECT
    'ideam'                                                                  AS fuente,
    COUNT(*)                                                                 AS n_filas,
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END)                AS nulos_temp,
    ROUND(100.0 * SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                     AS pct_nulos_temp,
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END)                AS nulos_precip,
    ROUND(100.0 * SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                     AS pct_nulos_precip,
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)                AS nulos_hum,
    ROUND(100.0 * SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                     AS pct_nulos_hum
FROM gold.ideam_daily
UNION ALL
SELECT
    'nasa',
    COUNT(*),
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2),
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2),
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM gold.nasa_daily;


-- -----------------------------------------------------------------------------
-- TEST SUMMARY
-- Expected outcome: all checks return ✓ OK
-- -----------------------------------------------------------------------------
WITH resultados AS (
    SELECT 'T01 filas ideam = 4018'            AS test, ABS(COUNT(*) - 4018) AS n FROM gold.ideam_daily
    UNION ALL
    SELECT 'T01 filas nasa = 4018',             ABS(COUNT(*) - 4018)          FROM gold.nasa_daily
    UNION ALL
    SELECT 'T02 duplicados ideam',              COUNT(*) FROM (SELECT fecha FROM gold.ideam_daily GROUP BY fecha HAVING COUNT(*) > 1) x
    UNION ALL
    SELECT 'T02 duplicados nasa',               COUNT(*) FROM (SELECT fecha FROM gold.nasa_daily  GROUP BY fecha HAVING COUNT(*) > 1) x
    UNION ALL
    SELECT 'T04 temp fuera rango ideam',        COUNT(*) FROM gold.ideam_daily WHERE temperatura_c    < 5  OR temperatura_c    > 40
    UNION ALL
    SELECT 'T04 temp fuera rango nasa',         COUNT(*) FROM gold.nasa_daily  WHERE temperatura_c    < 5  OR temperatura_c    > 40
    UNION ALL
    SELECT 'T04 humedad fuera rango ideam',     COUNT(*) FROM gold.ideam_daily WHERE humedad_pct      < 1  OR humedad_pct      > 100
    UNION ALL
    SELECT 'T04 humedad fuera rango nasa',      COUNT(*) FROM gold.nasa_daily  WHERE humedad_pct      < 1  OR humedad_pct      > 100
    UNION ALL
    SELECT 'T04 precipitacion negativa ideam',  COUNT(*) FROM gold.ideam_daily WHERE precipitacion_mm < 0
    UNION ALL
    SELECT 'T04 precipitacion negativa nasa',   COUNT(*) FROM gold.nasa_daily  WHERE precipitacion_mm < 0
)
SELECT
    test,
    n,
    CASE WHEN n = 0 THEN '✓ OK' ELSE '✗ FALLO' END AS resultado
FROM resultados
ORDER BY test;