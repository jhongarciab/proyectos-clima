-- db_init.sql
-- Bootstrap for Project 1 climate warehouse.
-- Creates schemas and bronze staging tables for IDEAM + NASA POWER.

-- Optional (run from admin DB, not inside this DB session):
-- CREATE DATABASE clima_db;

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- =========================================================
-- BRONZE: IDEAM staging tables (one per variable)
-- =========================================================
DROP TABLE IF EXISTS bronze.staging_ideam_temperature;
CREATE TABLE bronze.staging_ideam_temperature (
  codigoestacion text,
  nombreestacion text,
  departamento text,
  municipio text,
  fecha text,
  valor_diario text,
  unidadmedida text,
  source_file text
);

DROP TABLE IF EXISTS bronze.staging_ideam_precipitation;
CREATE TABLE bronze.staging_ideam_precipitation (
  codigoestacion text,
  nombreestacion text,
  departamento text,
  municipio text,
  fecha text,
  valor_diario text,
  unidadmedida text,
  source_file text
);

DROP TABLE IF EXISTS bronze.staging_ideam_humidity;
CREATE TABLE bronze.staging_ideam_humidity (
  codigoestacion text,
  nombreestacion text,
  departamento text,
  municipio text,
  fecha text,
  valor_diario text,
  unidadmedida text,
  source_file text
);

-- =========================================================
-- BRONZE: NASA POWER staging table
-- =========================================================
DROP TABLE IF EXISTS bronze.staging_nasa_daily;
CREATE TABLE bronze.staging_nasa_daily (
  year text,
  mo text,
  dy text,
  t2m text,
  prectotcorr text,
  rh2m text,
  source_file text
);
