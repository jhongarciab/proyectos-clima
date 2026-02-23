-- =============================================================================
-- Silver Layer: Data cleaning and standardization for IDEAM and NASA POWER.
--
-- Responsibilities of this layer:
--   1. Filter IDEAM stations that are not representative of urban Pereira.
--   2. Restrict the analysis period to 2015-01-01 through 2025-12-31.
--   3. Convert sentinel values to NULL:
--        - Zeros in temperature and humidity.
--        - Value 288 in precipitation (Matecaña overflow event).
--   4. Construct calendar date in NASA POWER using YEAR + DOY.
--   5. Compute and report missing data metrics per station.
--
-- Included stations (by code):
--   0026125710  Matecaña Airport   (duplicated in API, same station code)
--   0026125508  La Catalina        (duplicated in API, same station code)
--   0026135501  El Pílamo          (duplicated in API, same station code)
--
-- Source tables:
--   bronze.staging_ideam_*
--   bronze.staging_nasa_daily
--
-- Target tables:
--   silver.ideam_temperature
--   silver.ideam_humidity
--   silver.ideam_precipitation
--   silver.nasa_daily
-- =============================================================================
DROP TABLE IF EXISTS gold.ideam_daily_filled CASCADE;
DROP VIEW  IF EXISTS gold.ideam_daily        CASCADE;
DROP VIEW  IF EXISTS gold.nasa_daily         CASCADE;
DROP VIEW  IF EXISTS gold.climatologia_diaria CASCADE;
-- -----------------------------------------------------------------------------
-- 1. IDEAM — TEMPERATURE
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS silver.ideam_temperature;

CREATE TABLE silver.ideam_temperature AS
SELECT
    codigoestacion,
    nombreestacion,
    departamento,
    municipio,
    fecha,
    -- Ceros son valores centinela: temperatura 0 °C es imposible en Pereira
    CASE WHEN valor_diario = 0 THEN NULL ELSE valor_diario END AS valor_diario_c,
    unidadmedida
FROM bronze.staging_ideam_temperature
WHERE
    -- Solo estaciones representativas de Pereira urbana
    codigoestacion IN ('0026125710', '0026125508', '0026135501')
    -- Período de análisis
    AND fecha BETWEEN '2015-01-01' AND '2025-12-31';

-- Índices para consultas posteriores
CREATE INDEX ON silver.ideam_temperature (fecha);
CREATE INDEX ON silver.ideam_temperature (codigoestacion);

-- Sanity check
SELECT
    codigoestacion,
    nombreestacion,
    COUNT(*)                                                                AS n_registros,
    SUM(CASE WHEN valor_diario_c IS NULL THEN 1 ELSE 0 END)                AS n_nulos,
    ROUND(100.0 * SUM(CASE WHEN valor_diario_c IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                    AS pct_nulos,
    MIN(fecha)                                                              AS fecha_inicio,
    MAX(fecha)                                                              AS fecha_fin,
    ROUND(AVG(valor_diario_c)::numeric, 2)                                  AS promedio_c
FROM silver.ideam_temperature
GROUP BY codigoestacion, nombreestacion
ORDER BY codigoestacion, nombreestacion;


-- -----------------------------------------------------------------------------
-- 2. IDEAM — HUMIDITY
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS silver.ideam_humidity;

CREATE TABLE silver.ideam_humidity AS
SELECT
    codigoestacion,
    nombreestacion,
    departamento,
    municipio,
    fecha,
    -- Valores < 1 % son físicamente imposibles en Pereira (ceros exactos y
    -- valores residuales de sensor defectuoso se tratan igual)
CASE
    WHEN valor_diario < 1 THEN NULL
    WHEN codigoestacion = '0026125710' AND valor_diario < 40 THEN NULL
    ELSE valor_diario
END AS valor_diario_pct
FROM bronze.staging_ideam_humidity
WHERE
    codigoestacion IN ('0026125710', '0026125508', '0026135501')
    AND fecha BETWEEN '2015-01-01' AND '2025-12-31';

CREATE INDEX ON silver.ideam_humidity (fecha);
CREATE INDEX ON silver.ideam_humidity (codigoestacion);

-- Sanity check
SELECT
    codigoestacion,
    nombreestacion,
    COUNT(*)                                                                AS n_registros,
    SUM(CASE WHEN valor_diario_pct IS NULL THEN 1 ELSE 0 END)              AS n_nulos,
    ROUND(100.0 * SUM(CASE WHEN valor_diario_pct IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                    AS pct_nulos,
    MIN(fecha)                                                              AS fecha_inicio,
    MAX(fecha)                                                              AS fecha_fin,
    ROUND(AVG(valor_diario_pct)::numeric, 2)                               AS promedio_pct
FROM silver.ideam_humidity
GROUP BY codigoestacion, nombreestacion
ORDER BY codigoestacion, nombreestacion;


-- -----------------------------------------------------------------------------
-- 3. IDEAM — PRECIPITATION
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS silver.ideam_precipitation;

CREATE TABLE silver.ideam_precipitation AS
SELECT
    codigoestacion,
    nombreestacion,
    departamento,
    municipio,
    fecha,
    -- Valor 288 en Matecaña es centinela de desbordamiento de sensor (feb-mar 2022)
    CASE
        WHEN valor_diario > 125 THEN NULL
        ELSE valor_diario
    END AS valor_diario_mm,
    unidadmedida
FROM bronze.staging_ideam_precipitation
WHERE
    codigoestacion IN ('0026125710', '0026125508', '0026135501')
    AND fecha BETWEEN '2015-01-01' AND '2025-12-31';

CREATE INDEX ON silver.ideam_precipitation (fecha);
CREATE INDEX ON silver.ideam_precipitation (codigoestacion);

-- Sanity check
SELECT
    codigoestacion,
    nombreestacion,
    COUNT(*)                                                                AS n_registros,
    SUM(CASE WHEN valor_diario_mm IS NULL THEN 1 ELSE 0 END)               AS n_nulos,
    ROUND(100.0 * SUM(CASE WHEN valor_diario_mm IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                    AS pct_nulos,
    MIN(fecha)                                                              AS fecha_inicio,
    MAX(fecha)                                                              AS fecha_fin,
    ROUND(AVG(valor_diario_mm)::numeric, 2)                                AS promedio_mm,
    MAX(valor_diario_mm)                                                    AS maximo_mm
FROM silver.ideam_precipitation
GROUP BY codigoestacion, nombreestacion
ORDER BY codigoestacion, nombreestacion;


-- -----------------------------------------------------------------------------
-- 4. NASA POWER
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS silver.nasa_daily;

CREATE TABLE silver.nasa_daily AS
SELECT
    -- Construir fecha desde año + día del año
    (make_date(year, 1, 1) + (doy - 1) * INTERVAL '1 day')::date AS fecha,
    year,
    doy,
    -- Nombres descriptivos alineados con terminología del proyecto
    t2m            AS temperatura_c,
    prectotcorr    AS precipitacion_mm,
    rh2m           AS humedad_pct
FROM bronze.staging_nasa_daily
WHERE
    -- Período de análisis (year basta, doy garantiza integridad)
    year BETWEEN 2015 AND 2025
ORDER BY fecha;

CREATE INDEX ON silver.nasa_daily (fecha);

-- Sanity check
SELECT
    COUNT(*)                                                               AS n_registros,
    MIN(fecha)                                                             AS fecha_inicio,
    MAX(fecha)                                                             AS fecha_fin,
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END)             AS nulos_temp,
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END)             AS nulos_precip,
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)             AS nulos_humedad,
    ROUND(AVG(temperatura_c)::numeric, 2)                                 AS avg_temp_c,
    ROUND(AVG(precipitacion_mm)::numeric, 2)                              AS avg_precip_mm,
    ROUND(AVG(humedad_pct)::numeric, 2)                                   AS avg_humedad_pct
FROM silver.nasa_daily;


-- -----------------------------------------------------------------------------
-- 5. IDEAM Missing Data Coverage by Station
-- -----------------------------------------------------------------------------

WITH calendario AS (
    SELECT generate_series(
        '2015-01-01'::date,
        '2025-12-31'::date,
        '1 day'::interval
    )::date AS fecha
),
estaciones AS (
    -- Agrupar por codigoestacion para evitar duplicados por renombramiento
    SELECT DISTINCT codigoestacion
    FROM silver.ideam_temperature
    UNION
    SELECT DISTINCT codigoestacion
    FROM silver.ideam_humidity
    UNION
    SELECT DISTINCT codigoestacion
    FROM silver.ideam_precipitation
),
cobertura_temperatura AS (
    SELECT
        e.codigoestacion,
        'temperatura'                                                        AS variable,
        COUNT(c.fecha)                                                       AS dias_calendario,
        COUNT(t.fecha)                                                       AS dias_con_dato,
        COUNT(c.fecha) - COUNT(t.fecha)                                      AS dias_faltantes,
        ROUND(100.0 * (COUNT(c.fecha) - COUNT(t.fecha)) / COUNT(c.fecha), 2) AS pct_faltantes
    FROM estaciones e
    CROSS JOIN calendario c
    LEFT JOIN silver.ideam_temperature t
        ON t.codigoestacion = e.codigoestacion
        AND t.fecha = c.fecha
        AND t.valor_diario_c IS NOT NULL
    GROUP BY e.codigoestacion
),
cobertura_humedad AS (
    SELECT
        e.codigoestacion,
        'humedad'                                                            AS variable,
        COUNT(c.fecha)                                                       AS dias_calendario,
        COUNT(h.fecha)                                                       AS dias_con_dato,
        COUNT(c.fecha) - COUNT(h.fecha)                                      AS dias_faltantes,
        ROUND(100.0 * (COUNT(c.fecha) - COUNT(h.fecha)) / COUNT(c.fecha), 2) AS pct_faltantes
    FROM estaciones e
    CROSS JOIN calendario c
    LEFT JOIN silver.ideam_humidity h
        ON h.codigoestacion = e.codigoestacion
        AND h.fecha = c.fecha
        AND h.valor_diario_pct IS NOT NULL
    GROUP BY e.codigoestacion
),
cobertura_precipitacion AS (
    SELECT
        e.codigoestacion,
        'precipitacion'                                                      AS variable,
        COUNT(c.fecha)                                                       AS dias_calendario,
        COUNT(p.fecha)                                                       AS dias_con_dato,
        COUNT(c.fecha) - COUNT(p.fecha)                                      AS dias_faltantes,
        ROUND(100.0 * (COUNT(c.fecha) - COUNT(p.fecha)) / COUNT(c.fecha), 2) AS pct_faltantes
    FROM estaciones e
    CROSS JOIN calendario c
    LEFT JOIN silver.ideam_precipitation p
        ON p.codigoestacion = e.codigoestacion
        AND p.fecha = c.fecha
        AND p.valor_diario_mm IS NOT NULL
    GROUP BY e.codigoestacion
)
SELECT * FROM cobertura_temperatura
UNION ALL
SELECT * FROM cobertura_humedad
UNION ALL
SELECT * FROM cobertura_precipitacion
ORDER BY variable, codigoestacion;