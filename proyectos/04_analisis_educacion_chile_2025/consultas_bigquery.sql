-- SELECT * FROM 
-- ========================================================================
-- PROYECTO 4: ANÁLISIS DE RENDIMIENTO Y ASISTENCIA ESCOLAR CHILE (2025)
-- MOTOR: Google BigQuery (Standard SQL)
-- TABLA: `mineduc-analytics.educacion_chile.consolidado_ee_2025`
-- ========================================================================

-- CONSULTA 1: BENCHMARK POR DEPENDENCIA ADMINISTRATIVA
-- Analiza volumen de matrícula, asistencia media y brecha de reprobación
SELECT 
    CASE COD_DEPE2
        WHEN 1 THEN 'Municipal'
        WHEN 2 THEN 'Particular Subvencionado'
        WHEN 3 THEN 'Particular Pagado'
        WHEN 4 THEN 'Corp. Administración Delegada'
        WHEN 5 THEN 'SLEP'
        ELSE 'Otro'
    END AS dependencia,
    COUNT(RBD) AS cantidad_establecimientos,
    SUM(TOTAL_EVALUADOS) AS total_matricula_evaluada,
    ROUND(AVG(PROM_ASIS_POND), 2) AS asistencia_promedio_pct,
    ROUND(AVG(TASA_REPROBACION), 2) AS tasa_reprobacion_promedio_pct,
    ROUND(SUM(TOTAL_RETIRADOS) * 100.0 / NULLIF(SUM(TOTAL_EVALUADOS + TOTAL_RETIRADOS), 0), 2) AS tasa_retiro_pct
FROM `mineduc-analytics.educacion_chile.consolidado_ee_2025`
WHERE TOTAL_EVALUADOS > 0
GROUP BY COD_DEPE2
ORDER BY tasa_reprobacion_promedio_pct DESC;


-- CONSULTA 2: RANKING REGIONAL POR DESERCIÓN / RETIRO POTENCIAL (WINDOW FUNCTION)
-- Agrupa a nivel regional y jerarquiza mediante DENSE_RANK()
WITH resumen_regional AS (
    SELECT 
        NOM_REG_RBD_A AS region,
        COUNT(RBD) AS total_colegios,
        SUM(TOTAL_EVALUADOS) AS total_evaluados,
        SUM(TOTAL_RETIRADOS) AS total_retirados,
        ROUND(AVG(PROM_ASIS_POND), 2) AS asistencia_promedio,
        ROUND(SUM(TOTAL_RETIRADOS) * 100.0 / NULLIF(SUM(TOTAL_EVALUADOS + TOTAL_RETIRADOS), 0), 2) AS tasa_retiro_pct
    FROM `mineduc-analytics.educacion_chile.consolidado_ee_2025`
    WHERE TOTAL_EVALUADOS > 0
    GROUP BY NOM_REG_RBD_A
)
SELECT 
    region,
    total_colegios,
    total_evaluados,
    total_retirados,
    asistencia_promedio,
    tasa_retiro_pct,
    DENSE_RANK() OVER(ORDER BY tasa_retiro_pct DESC) AS ranking_desercion
FROM resumen_regional
ORDER BY ranking_desercion;


-- CONSULTA 3: COMPARATIVA BRECHA URBANA VS RURAL
-- Evalúa las diferencias territoriales en presentismo y desempeño
SELECT 
    CASE RURAL_RBD
        WHEN 0 THEN 'Urbano'
        WHEN 1 THEN 'Rural'
    END AS zona,
    COUNT(RBD) AS establecimientos,
    ROUND(AVG(TOTAL_EVALUADOS), 0) AS promedio_alumnos_colegio,
    ROUND(AVG(PROM_ASIS_POND), 2) AS asistencia_media_pct,
    ROUND(AVG(TASA_REPROBACION), 2) AS reprobacion_media_pct,
    ROUND(AVG(TASA_APROBACION), 2) AS aprobacion_media_pct
FROM `mineduc-analytics.educacion_chile.consolidado_ee_2025`
WHERE TOTAL_EVALUADOS > 0
GROUP BY RURAL_RBD;


-- CONSULTA 4: FOCOS ROJOS OPERACIONALES (OUTLIERS CRÍTICOS)
-- Establecimientos con matrícula significativa (>100), baja asistencia (<85%) y alta reprobación (>10%)
SELECT 
    RBD,
    NOM_RBD,
    NOM_COM_RBD,
    NOM_REG_RBD_A AS region,
    TOTAL_EVALUADOS,
    PROM_ASIS_POND AS asistencia_pct,
    TASA_REPROBACION AS reprobacion_pct,
    TOTAL_RETIRADOS
FROM `mineduc-analytics.educacion_chile.consolidado_ee_2025`
WHERE TOTAL_EVALUADOS >= 100 
  AND PROM_ASIS_POND < 85.0
  AND TASA_REPROBACION > 10.0
ORDER BY TASA_REPROBACION DESC
LIMIT 15;