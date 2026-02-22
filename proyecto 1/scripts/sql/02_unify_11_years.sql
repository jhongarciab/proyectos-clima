-- 02_unify_11_years.sql
-- Transform data from bronze staging tables into silver clean tables.
-- Expected bronze tables:
--   bronze.staging_ideam_temperature
--   bronze.staging_ideam_precipitation
--   bronze.staging_ideam_humidity
--   bronze.staging_nasa_daily

CREATE SCHEMA IF NOT EXISTS silver;

-- =========================================================
-- SILVER: IDEAM per-variable clean tables (2015-2025)
-- =========================================================
DROP TABLE IF EXISTS silver.ideam_temperature_daily;
CREATE TABLE silver.ideam_temperature_daily AS
WITH x AS (
  SELECT
    trim(codigoestacion) AS codigoestacion,
    trim(nombreestacion) AS nombreestacion,
    upper(trim(departamento)) AS departamento,
    upper(trim(municipio)) AS municipio,
    CAST(fecha AS date) AS fecha,
    CAST(valor_diario AS double precision) AS temperature_c,
    trim(unidadmedida) AS unidadmedida,
    source_file,
    ROW_NUMBER() OVER (
      PARTITION BY trim(codigoestacion), CAST(fecha AS date)
      ORDER BY source_file DESC NULLS LAST
    ) AS rn
  FROM bronze.staging_ideam_temperature
  WHERE CAST(fecha AS date) BETWEEN DATE '2015-01-01' AND DATE '2025-12-31'
    AND valor_diario IS NOT NULL
)
SELECT codigoestacion, nombreestacion, departamento, municipio, fecha, temperature_c, unidadmedida
FROM x
WHERE rn = 1
  AND temperature_c BETWEEN -20 AND 60;

DROP TABLE IF EXISTS silver.ideam_precipitation_daily;
CREATE TABLE silver.ideam_precipitation_daily AS
WITH x AS (
  SELECT
    trim(codigoestacion) AS codigoestacion,
    trim(nombreestacion) AS nombreestacion,
    upper(trim(departamento)) AS departamento,
    upper(trim(municipio)) AS municipio,
    CAST(fecha AS date) AS fecha,
    CAST(valor_diario AS double precision) AS precipitation_mm,
    trim(unidadmedida) AS unidadmedida,
    source_file,
    ROW_NUMBER() OVER (
      PARTITION BY trim(codigoestacion), CAST(fecha AS date)
      ORDER BY source_file DESC NULLS LAST
    ) AS rn
  FROM bronze.staging_ideam_precipitation
  WHERE CAST(fecha AS date) BETWEEN DATE '2015-01-01' AND DATE '2025-12-31'
    AND valor_diario IS NOT NULL
)
SELECT codigoestacion, nombreestacion, departamento, municipio, fecha, precipitation_mm, unidadmedida
FROM x
WHERE rn = 1
  AND precipitation_mm >= 0;

DROP TABLE IF EXISTS silver.ideam_humidity_daily;
CREATE TABLE silver.ideam_humidity_daily AS
WITH x AS (
  SELECT
    trim(codigoestacion) AS codigoestacion,
    trim(nombreestacion) AS nombreestacion,
    upper(trim(departamento)) AS departamento,
    upper(trim(municipio)) AS municipio,
    CAST(fecha AS date) AS fecha,
    CAST(valor_diario AS double precision) AS humidity_pct,
    trim(unidadmedida) AS unidadmedida,
    source_file,
    ROW_NUMBER() OVER (
      PARTITION BY trim(codigoestacion), CAST(fecha AS date)
      ORDER BY source_file DESC NULLS LAST
    ) AS rn
  FROM bronze.staging_ideam_humidity
  WHERE CAST(fecha AS date) BETWEEN DATE '2015-01-01' AND DATE '2025-12-31'
    AND valor_diario IS NOT NULL
)
SELECT codigoestacion, nombreestacion, departamento, municipio, fecha, humidity_pct, unidadmedida
FROM x
WHERE rn = 1
  AND humidity_pct BETWEEN 0 AND 100;

-- =========================================================
-- SILVER: IDEAM wide table (single table with the 3 variables)
-- =========================================================
DROP TABLE IF EXISTS silver.ideam_daily_wide;
CREATE TABLE silver.ideam_daily_wide AS
SELECT
  t.codigoestacion,
  t.nombreestacion,
  t.departamento,
  t.municipio,
  t.fecha,
  t.temperature_c,
  p.precipitation_mm,
  h.humidity_pct
FROM silver.ideam_temperature_daily t
LEFT JOIN silver.ideam_precipitation_daily p
  ON t.codigoestacion = p.codigoestacion AND t.fecha = p.fecha
LEFT JOIN silver.ideam_humidity_daily h
  ON t.codigoestacion = h.codigoestacion AND t.fecha = h.fecha;

-- =========================================================
-- SILVER: NASA clean daily table
-- =========================================================
DROP TABLE IF EXISTS silver.nasa_daily;
CREATE TABLE silver.nasa_daily AS
WITH x AS (
  SELECT
    make_date(CAST(year AS int), CAST(mo AS int), CAST(dy AS int)) AS fecha,
    CAST(t2m AS double precision) AS temperature_c,
    CAST(prectotcorr AS double precision) AS precipitation_mm,
    CAST(rh2m AS double precision) AS humidity_pct,
    source_file
  FROM bronze.staging_nasa_daily
)
SELECT fecha, temperature_c, precipitation_mm, humidity_pct
FROM x
WHERE fecha BETWEEN DATE '2015-01-01' AND DATE '2025-12-31'
  AND temperature_c BETWEEN -50 AND 60
  AND precipitation_mm >= 0
  AND humidity_pct BETWEEN 0 AND 100;

-- =========================================================
-- Quick row-count sanity check
-- =========================================================
SELECT 'silver.ideam_temperature_daily' AS table_name, COUNT(*) AS n_rows FROM silver.ideam_temperature_daily
UNION ALL
SELECT 'silver.ideam_precipitation_daily', COUNT(*) FROM silver.ideam_precipitation_daily
UNION ALL
SELECT 'silver.ideam_humidity_daily', COUNT(*) FROM silver.ideam_humidity_daily
UNION ALL
SELECT 'silver.ideam_daily_wide', COUNT(*) FROM silver.ideam_daily_wide
UNION ALL
SELECT 'silver.nasa_daily', COUNT(*) FROM silver.nasa_daily;
