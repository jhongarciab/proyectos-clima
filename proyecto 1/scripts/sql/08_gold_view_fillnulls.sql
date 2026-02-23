-- =============================================================================
-- 04_gold_ideam_filled.sql
-- Tabla gold con serie completa sin NULLs para IDEAM.
-- Estrategia de imputación: promedio climatológico del mismo día del año
-- calculado sobre todos los valores no nulos disponibles en gold.ideam_daily.
-- La tabla gold.ideam_daily original se conserva intacta con NULLs.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. CLIMATOLOGÍA DIARIA
-- Promedio de cada variable por día del año (1–366)
-- usando todos los años con dato disponible.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.climatologia_diaria AS
SELECT
    EXTRACT(DOY FROM fecha)::int                    AS doy,
    ROUND(AVG(temperatura_c)::numeric,    4)        AS temp_clim,
    ROUND(AVG(precipitacion_mm)::numeric, 4)        AS precip_clim,
    ROUND(AVG(humedad_pct)::numeric,      4)        AS hum_clim
FROM gold.ideam_daily
WHERE temperatura_c    IS NOT NULL
   OR precipitacion_mm IS NOT NULL
   OR humedad_pct      IS NOT NULL
GROUP BY doy
ORDER BY doy;


-- -----------------------------------------------------------------------------
-- 2. TABLA CON SERIE COMPLETA IMPUTADA
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS gold.ideam_daily_filled;

CREATE TABLE gold.ideam_daily_filled AS
SELECT
    g.fecha,
    CASE
        WHEN g.temperatura_c IS NOT NULL THEN g.temperatura_c
        ELSE c.temp_clim
    END AS temperatura_c,
    CASE
        WHEN g.precipitacion_mm IS NOT NULL THEN g.precipitacion_mm
        ELSE c.precip_clim
    END AS precipitacion_mm,
    CASE
        WHEN g.humedad_pct IS NOT NULL THEN g.humedad_pct
        ELSE c.hum_clim
    END AS humedad_pct
FROM gold.ideam_daily g
JOIN gold.climatologia_diaria c
    ON EXTRACT(DOY FROM g.fecha)::int = c.doy
ORDER BY g.fecha;

CREATE INDEX ON gold.ideam_daily_filled (fecha);


-- -----------------------------------------------------------------------------
-- 3. VERIFICACIÓN
-- -----------------------------------------------------------------------------

-- No debe haber ningún NULL
SELECT
    COUNT(*)                                                           AS total_filas,
    SUM(CASE WHEN temperatura_c    IS NULL THEN 1 ELSE 0 END)         AS nulls_temp,
    SUM(CASE WHEN precipitacion_mm IS NULL THEN 1 ELSE 0 END)         AS nulls_precip,
    SUM(CASE WHEN humedad_pct      IS NULL THEN 1 ELSE 0 END)         AS nulls_hum
FROM gold.ideam_daily_filled;

-- para verificar que no se introdujo sesgo significativo
SELECT
    'original'  AS tabla,
    ROUND(AVG(temperatura_c)::numeric,    2) AS avg_temp,
    ROUND(AVG(precipitacion_mm)::numeric, 2) AS avg_precip,
    ROUND(AVG(humedad_pct)::numeric,      2) AS avg_hum
FROM gold.ideam_daily
UNION ALL
SELECT
    'filled',
    ROUND(AVG(temperatura_c)::numeric,    2),
    ROUND(AVG(precipitacion_mm)::numeric, 2),
    ROUND(AVG(humedad_pct)::numeric,      2)
FROM gold.ideam_daily_filled;