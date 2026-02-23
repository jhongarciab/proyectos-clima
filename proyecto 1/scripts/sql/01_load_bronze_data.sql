-- 01_load_bronze_data.sql
-- Load local CSV files into bronze staging tables.
--
-- IMPORTANT:
-- 1) Open SQL client from project root when possible.
-- 2) These paths are project-relative (./data/raw/...).
-- 3) If your PostgreSQL server cannot access local files with COPY,
--    use your client import wizard or switch COPY -> \copy in psql.

TRUNCATE TABLE bronze.staging_ideam_temperature;
TRUNCATE TABLE bronze.staging_ideam_precipitation;
TRUNCATE TABLE bronze.staging_ideam_humidity;
TRUNCATE TABLE bronze.staging_nasa_daily;

-- =========================================================
-- IDEAM temperature (2015-2025)
-- =========================================================
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2015-01-01_2025-12-31_daily.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- IDEAM precipitation (2016-2025)
-- =========================================================
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2015-01-01_2025-12-31_daily.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- IDEAM humidity (2015-2025)
-- =========================================================
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2015-01-01_2025-12-31_daily.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- NASA POWER daily (single file)
-- =========================================================
\copy bronze.staging_nasa_daily (year, doy, t2m, prectotcorr, rh2m) FROM PROGRAM 'sed -n "/-END HEADER-/,\$p" ./data/raw/nasa/nasa_power_pereira_20150101_20251231_daily.csv | tail -n +2' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- Quick sanity checks
-- =========================================================
SELECT 'bronze.staging_ideam_temperature' AS table_name, COUNT(*) AS n_rows FROM bronze.staging_ideam_temperature
UNION ALL
SELECT 'bronze.staging_ideam_precipitation', COUNT(*) FROM bronze.staging_ideam_precipitation
UNION ALL
SELECT 'bronze.staging_ideam_humidity', COUNT(*) FROM bronze.staging_ideam_humidity
UNION ALL
SELECT 'bronze.staging_nasa_daily', COUNT(*) FROM bronze.staging_nasa_daily;