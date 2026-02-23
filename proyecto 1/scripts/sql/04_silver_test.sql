-- =============================================================================
-- SILVER LAYER — VALIDATION TESTS
-- Verifies that all cleaning rules applied in the Silver layer are correct.
-- Expected results are specified in each test block.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- T01. No zero values in temperature
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT codigoestacion, nombreestacion, fecha, valor_diario_c
FROM silver.ideam_temperature
WHERE valor_diario_c = 0;

-- -----------------------------------------------------------------------------
-- T02. No zero values in humidity
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT codigoestacion, nombreestacion, fecha, valor_diario_pct
FROM silver.ideam_humidity
WHERE valor_diario_pct = 0;

-- -----------------------------------------------------------------------------
-- T03. No sentinel value 288 in Matecaña precipitation
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT codigoestacion, nombreestacion, fecha, valor_diario_mm
FROM silver.ideam_precipitation
WHERE codigoestacion = '0026125710'
  AND valor_diario_mm = 288;


-- -----------------------------------------------------------------------------
-- T04. Only authorized stations present in all three tables
-- Expected: Only station codes
--           0026125710, 0026125508, 0026135501
-- -----------------------------------------------------------------------------
SELECT DISTINCT codigoestacion, nombreestacion
FROM silver.ideam_temperature
UNION
SELECT DISTINCT codigoestacion, nombreestacion
FROM silver.ideam_humidity
UNION
SELECT DISTINCT codigoestacion, nombreestacion
FROM silver.ideam_precipitation
ORDER BY codigoestacion;

-- -----------------------------------------------------------------------------
-- T05. All dates within analysis period (2015-01-01 to 2025-12-31)
-- Expected: 0 rows in each table
-- -----------------------------------------------------------------------------
SELECT 'temperatura' AS tabla, COUNT(*) AS fuera_de_rango
FROM silver.ideam_temperature
WHERE fecha < '2015-01-01' OR fecha > '2025-12-31'
UNION ALL
SELECT 'humedad', COUNT(*)
FROM silver.ideam_humidity
WHERE fecha < '2015-01-01' OR fecha > '2025-12-31'
UNION ALL
SELECT 'precipitacion', COUNT(*)
FROM silver.ideam_precipitation
WHERE fecha < '2015-01-01' OR fecha > '2025-12-31';

-- -----------------------------------------------------------------------------
-- T06. No duplicates (same station code + same date)
-- Expected: 0 rows in each table
-- -----------------------------------------------------------------------------
SELECT 'temperatura' AS tabla, codigoestacion, fecha, COUNT(*) AS n
FROM silver.ideam_temperature
GROUP BY codigoestacion, fecha
HAVING COUNT(*) > 1
UNION ALL
SELECT 'humedad', codigoestacion, fecha, COUNT(*)
FROM silver.ideam_humidity
GROUP BY codigoestacion, fecha
HAVING COUNT(*) > 1
UNION ALL
SELECT 'precipitacion', codigoestacion, fecha, COUNT(*)
FROM silver.ideam_precipitation
GROUP BY codigoestacion, fecha
HAVING COUNT(*) > 1;

-- -----------------------------------------------------------------------------
-- T07. Temperature within physically plausible range for Pereira (5–40 °C)
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT codigoestacion, nombreestacion, fecha, valor_diario_c
FROM silver.ideam_temperature
WHERE valor_diario_c < 5 OR valor_diario_c > 40;

-- -----------------------------------------------------------------------------
-- T08. Humidity within physical bounds (1–100 %)
-- Zero already nullified in T02
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT codigoestacion, nombreestacion, fecha, valor_diario_pct
FROM silver.ideam_humidity
WHERE valor_diario_pct < 1 OR valor_diario_pct > 100;

-- -----------------------------------------------------------------------------
-- T09. No negative precipitation values
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT codigoestacion, nombreestacion, fecha, valor_diario_mm
FROM silver.ideam_precipitation
WHERE valor_diario_mm < 0;

-- -----------------------------------------------------------------------------
-- T10. NASA: calendar date correctly constructed, no gaps
-- Expected: 0 rows (no missing calendar dates)
-- -----------------------------------------------------------------------------
WITH calendario AS (
    SELECT generate_series(
        '2015-01-01'::date,
        '2025-12-31'::date,
        '1 day'::interval
    )::date AS fecha
)
SELECT c.fecha
FROM calendario c
LEFT JOIN silver.nasa_daily n ON n.fecha = c.fecha
WHERE n.fecha IS NULL;

-- -----------------------------------------------------------------------------
-- T11. NASA: no negative values in any variable
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT fecha, temperatura_c, precipitacion_mm, humedad_pct
FROM silver.nasa_daily
WHERE temperatura_c    < 0
   OR precipitacion_mm < 0
   OR humedad_pct      < 0;


-- -----------------------------------------------------------------------------
-- T12. NASA: humidity within physical bounds (0–100 %)
-- Expected: 0 rows
-- -----------------------------------------------------------------------------
SELECT fecha, humedad_pct
FROM silver.nasa_daily
WHERE humedad_pct < 0 OR humedad_pct > 100;


-- -----------------------------------------------------------------------------
-- TEST SUMMARY
-- Counts how many tests failed (n > 0 indicates an issue)
-- -----------------------------------------------------------------------------
WITH resultados AS (
    SELECT 'T01 ceros temperatura'            AS test, COUNT(*) AS n FROM silver.ideam_temperature WHERE valor_diario_c = 0
    UNION ALL
    SELECT 'T02 ceros humedad',                        COUNT(*) FROM silver.ideam_humidity WHERE valor_diario_pct = 0
    UNION ALL
    SELECT 'T03 centinela 288 precipitacion',           COUNT(*) FROM silver.ideam_precipitation WHERE codigoestacion = '0026125710' AND valor_diario_mm = 288
    UNION ALL
    SELECT 'T05 fechas fuera de rango temperatura',     COUNT(*) FROM silver.ideam_temperature WHERE fecha < '2015-01-01' OR fecha > '2025-12-31'
    UNION ALL
    SELECT 'T05 fechas fuera de rango humedad',         COUNT(*) FROM silver.ideam_humidity WHERE fecha < '2015-01-01' OR fecha > '2025-12-31'
    UNION ALL
    SELECT 'T05 fechas fuera de rango precipitacion',   COUNT(*) FROM silver.ideam_precipitation WHERE fecha < '2015-01-01' OR fecha > '2025-12-31'
    UNION ALL
    SELECT 'T06 duplicados temperatura',                COUNT(*) FROM (SELECT codigoestacion, fecha FROM silver.ideam_temperature GROUP BY codigoestacion, fecha HAVING COUNT(*) > 1) x
    UNION ALL
    SELECT 'T06 duplicados humedad',                    COUNT(*) FROM (SELECT codigoestacion, fecha FROM silver.ideam_humidity GROUP BY codigoestacion, fecha HAVING COUNT(*) > 1) x
    UNION ALL
    SELECT 'T06 duplicados precipitacion',              COUNT(*) FROM (SELECT codigoestacion, fecha FROM silver.ideam_precipitation GROUP BY codigoestacion, fecha HAVING COUNT(*) > 1) x
    UNION ALL
    SELECT 'T07 temperatura fuera de rango fisico',     COUNT(*) FROM silver.ideam_temperature WHERE valor_diario_c < 5 OR valor_diario_c > 40
    UNION ALL
    SELECT 'T08 humedad fuera de rango fisico',         COUNT(*) FROM silver.ideam_humidity WHERE valor_diario_pct < 1 OR valor_diario_pct > 100
    UNION ALL
    SELECT 'T09 precipitacion negativa',                COUNT(*) FROM silver.ideam_precipitation WHERE valor_diario_mm < 0
    UNION ALL
    SELECT 'T11 nasa valores negativos',                COUNT(*) FROM silver.nasa_daily WHERE temperatura_c < 0 OR precipitacion_mm < 0 OR humedad_pct < 0
    UNION ALL
    SELECT 'T12 nasa humedad fuera de rango',           COUNT(*) FROM silver.nasa_daily WHERE humedad_pct < 0 OR humedad_pct > 100
)
SELECT
    test,
    n,
    CASE WHEN n = 0 THEN '✓ OK' ELSE '✗ FALLO' END AS resultado
FROM resultados
ORDER BY test;