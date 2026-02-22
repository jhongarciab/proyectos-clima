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
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2015-01-01_2015-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2016-01-01_2016-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2017-01-01_2017-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2018-01-01_2018-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2019-01-01_2019-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2020-01-01_2020-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2021-01-01_2021-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2022-01-01_2022-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2023-01-01_2023-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2024-01-01_2024-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_temperature (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/temperature/ideam_temperature_risaralda_pereira_2025-01-01_2025-12-31_daily.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- IDEAM precipitation (2016-2025)
-- =========================================================
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2016-01-01_2016-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2017-01-01_2017-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2018-01-01_2018-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2019-01-01_2019-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2020-01-01_2020-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2021-01-01_2021-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2022-01-01_2022-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2023-01-01_2023-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2024-01-01_2024-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_precipitation (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/precipitation/ideam_precipitation_risaralda_pereira_2025-01-01_2025-12-31_daily.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- IDEAM humidity (2015-2025)
-- =========================================================
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2015-01-01_2015-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2016-01-01_2016-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2017-01-01_2017-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2018-01-01_2018-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2019-01-01_2019-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2020-01-01_2020-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2021-01-01_2021-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2022-01-01_2022-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2023-01-01_2023-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2024-01-01_2024-12-31_daily.csv' WITH (FORMAT csv, HEADER true);
\copy bronze.staging_ideam_humidity (codigoestacion,nombreestacion,departamento,municipio,fecha,valor_diario,unidadmedida) FROM './data/raw/ideam/humidity/ideam_humidity_risaralda_pereira_2025-01-01_2025-12-31_daily.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================
-- NASA POWER daily (single file)
-- =========================================================
\copy bronze.staging_nasa_daily (year, mo, dy, t2m, prectotcorr, rh2m) FROM './data/raw/nasa/nasa_power/nasa_power_pereira_20150101_20251231_daily.csv' WITH (FORMAT csv, HEADER true);

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