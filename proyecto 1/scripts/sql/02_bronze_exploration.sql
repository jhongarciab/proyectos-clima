-- =============================================================================
-- IDEAM BRONZE EXPLORATION QUERIES
-- Purpose: Understand station coverage, data quality, and anomalies before
--          building the silver layer.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. STATION OVERVIEW PER VARIABLE
--    For each station: record count, date range, coverage %, avg, min, max.
--    Used to decide which stations are representative of Pereira's urban climate.
-- -----------------------------------------------------------------------------
-- Temperature
SELECT
    codigoestacion,
    nombreestacion,
    municipio,
    COUNT(*)                                                              AS n_records,
    MIN(fecha)                                                            AS date_start,
    MAX(fecha)                                                            AS date_end,
    ROUND(100.0 * COUNT(*) / (MAX(fecha) - MIN(fecha) + 1), 1)           AS coverage_pct,
    ROUND(AVG(valor_diario)::numeric, 2)                                  AS avg_value,
    MIN(valor_diario)                                                     AS min_value,
    MAX(valor_diario)                                                     AS max_value
FROM bronze.staging_ideam_temperature
GROUP BY codigoestacion, nombreestacion, municipio
ORDER BY n_records DESC;

-- Humidity
SELECT
    codigoestacion,
    nombreestacion,
    municipio,
    COUNT(*)                                                              AS n_records,
    MIN(fecha)                                                            AS date_start,
    MAX(fecha)                                                            AS date_end,
    ROUND(100.0 * COUNT(*) / (MAX(fecha) - MIN(fecha) + 1), 1)           AS coverage_pct,
    ROUND(AVG(valor_diario)::numeric, 2)                                  AS avg_value,
    MIN(valor_diario)                                                     AS min_value,
    MAX(valor_diario)                                                     AS max_value
FROM bronze.staging_ideam_humidity
GROUP BY codigoestacion, nombreestacion, municipio
ORDER BY n_records DESC;

-- Precipitation
SELECT
    codigoestacion,
    nombreestacion,
    municipio,
    COUNT(*)                                                              AS n_records,
    MIN(fecha)                                                            AS date_start,
    MAX(fecha)                                                            AS date_end,
    ROUND(100.0 * COUNT(*) / (MAX(fecha) - MIN(fecha) + 1), 1)           AS coverage_pct,
    ROUND(AVG(valor_diario)::numeric, 2)                                  AS avg_value,
    MIN(valor_diario)                                                     AS min_value,
    MAX(valor_diario)                                                     AS max_value
FROM bronze.staging_ideam_precipitation
GROUP BY codigoestacion, nombreestacion, municipio
ORDER BY n_records DESC;


-- -----------------------------------------------------------------------------
-- 2. UNIT CONSISTENCY CHECK
--    Verify that all records across variables use a single unit of measure.
--    Expected: °C for temperature, mm for precipitation, % for humidity.
-- -----------------------------------------------------------------------------
SELECT 'temperature'   AS variable, unidadmedida, COUNT(*) AS n
FROM bronze.staging_ideam_temperature  GROUP BY unidadmedida
UNION ALL
SELECT 'precipitation', unidadmedida, COUNT(*)
FROM bronze.staging_ideam_precipitation GROUP BY unidadmedida
UNION ALL
SELECT 'humidity',      unidadmedida, COUNT(*)
FROM bronze.staging_ideam_humidity      GROUP BY unidadmedida
ORDER BY variable, n DESC;


-- -----------------------------------------------------------------------------
-- 3. DUPLICATE DATE CHECK (same station code, same date, more than one row)
--    Some stations appear under two names in the API (renamed/reconnected).
--    This verifies there are no overlapping dates between those entries.
-- -----------------------------------------------------------------------------
-- Temperature
SELECT codigoestacion, fecha, COUNT(*) AS n_entries
FROM bronze.staging_ideam_temperature
GROUP BY codigoestacion, fecha
HAVING COUNT(*) > 1
ORDER BY codigoestacion, fecha
LIMIT 50;

-- Humidity
SELECT codigoestacion, fecha, COUNT(*) AS n_entries
FROM bronze.staging_ideam_humidity
GROUP BY codigoestacion, fecha
HAVING COUNT(*) > 1
ORDER BY codigoestacion, fecha
LIMIT 50;

-- Precipitation
SELECT codigoestacion, fecha, COUNT(*) AS n_entries
FROM bronze.staging_ideam_precipitation
GROUP BY codigoestacion, fecha
HAVING COUNT(*) > 1
ORDER BY codigoestacion, fecha
LIMIT 50;


-- -----------------------------------------------------------------------------
-- 4. ZERO-VALUE ANALYSIS FOR TEMPERATURE AND HUMIDITY
--    Zero is physically impossible for humidity in Pereira and highly suspicious
--    for temperature. These are likely sentinel values or sensor errors.
-- -----------------------------------------------------------------------------
-- Temperature zeros
SELECT
    codigoestacion,
    nombreestacion,
    COUNT(*)                                                                   AS total_records,
    SUM(CASE WHEN valor_diario = 0 THEN 1 ELSE 0 END)                         AS n_zeros,
    ROUND(100.0 * SUM(CASE WHEN valor_diario = 0 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                       AS pct_zeros
FROM bronze.staging_ideam_temperature
GROUP BY codigoestacion, nombreestacion
ORDER BY n_zeros DESC;

-- Humidity zeros
SELECT
    codigoestacion,
    nombreestacion,
    COUNT(*)                                                                   AS total_records,
    SUM(CASE WHEN valor_diario = 0 THEN 1 ELSE 0 END)                         AS n_zeros,
    ROUND(100.0 * SUM(CASE WHEN valor_diario = 0 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                       AS pct_zeros
FROM bronze.staging_ideam_humidity
GROUP BY codigoestacion, nombreestacion
ORDER BY n_zeros DESC;


-- -----------------------------------------------------------------------------
-- 5. PRECIPITATION EXTREME VALUES
--    Values above 100 mm/day are rare in Pereira. Values at round numbers
--    repeated across multiple days (e.g., exactly 288 mm) are likely
--    sensor overflow codes or sentinel values, not real rainfall.
-- -----------------------------------------------------------------------------
-- All days above 100 mm, ordered by value descending
SELECT
    codigoestacion,
    nombreestacion,
    fecha,
    valor_diario
FROM bronze.staging_ideam_precipitation
WHERE valor_diario > 100
ORDER BY valor_diario DESC;

-- Percentile distribution per station to contextualize extremes
SELECT
    codigoestacion,
    nombreestacion,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY valor_diario)::numeric, 2) AS p25,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY valor_diario)::numeric, 2) AS p50,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY valor_diario)::numeric, 2) AS p75,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY valor_diario)::numeric, 2) AS p90,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY valor_diario)::numeric, 2) AS p95,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY valor_diario)::numeric, 2) AS p99,
    MAX(valor_diario)                                                              AS max_value
FROM bronze.staging_ideam_precipitation
GROUP BY codigoestacion, nombreestacion
ORDER BY max_value DESC;