-- Proyecto: Análisis de retención y riesgo de fuga
-- Motor: MySQL 8+
-- Datos sintéticos: no representan clientes ni resultados reales.
-- Importa data/clientes.csv en la tabla clientes después de crearla.

CREATE TABLE IF NOT EXISTS clientes (
    customer_id INT NOT NULL PRIMARY KEY,
    plan VARCHAR(20) NOT NULL,
    tenure_months TINYINT UNSIGNED NOT NULL,
    monthly_fee_clp INT UNSIGNED NOT NULL,
    support_tickets_90d TINYINT UNSIGNED NOT NULL,
    payment_delay_count_90d TINYINT UNSIGNED NOT NULL,
    days_since_last_purchase SMALLINT UNSIGNED NOT NULL,
    churned TINYINT NOT NULL,
    CONSTRAINT chk_clientes_tenure CHECK (tenure_months BETWEEN 1 AND 60),
    CONSTRAINT chk_clientes_monthly_fee CHECK (monthly_fee_clp > 0),
    CONSTRAINT chk_clientes_churned CHECK (churned IN (0, 1))
);

-- 1. KPIs ejecutivos
SELECT
    COUNT(*) AS clientes,
    SUM(churned) AS clientes_churn,
    ROUND(100.0 * SUM(churned) / NULLIF(COUNT(*), 0), 2) AS tasa_churn_pct,
    SUM(CASE WHEN churned = 1 THEN monthly_fee_clp ELSE 0 END)
        AS ingreso_mensual_asociado_churn_clp,
    ROUND(AVG(monthly_fee_clp), 0) AS cargo_mensual_promedio_clp
FROM clientes;

-- 2. Churn y exposición de ingresos por plan
SELECT
    plan,
    COUNT(*) AS clientes,
    SUM(churned) AS clientes_churn,
    ROUND(100.0 * SUM(churned) / NULLIF(COUNT(*), 0), 2) AS tasa_churn_pct,
    SUM(CASE WHEN churned = 1 THEN monthly_fee_clp ELSE 0 END)
        AS ingreso_mensual_asociado_churn_clp
FROM clientes
GROUP BY plan
ORDER BY tasa_churn_pct DESC;

-- 3. Churn por tramo de antigüedad
SELECT
    CASE
        WHEN tenure_months <= 3 THEN '01. 1-3 meses'
        WHEN tenure_months <= 6 THEN '02. 4-6 meses'
        WHEN tenure_months <= 12 THEN '03. 7-12 meses'
        WHEN tenure_months <= 24 THEN '04. 13-24 meses'
        ELSE '05. 25-60 meses'
    END AS tramo_antiguedad,
    COUNT(*) AS clientes,
    SUM(churned) AS clientes_churn,
    ROUND(100.0 * SUM(churned) / NULLIF(COUNT(*), 0), 2) AS tasa_churn_pct
FROM clientes
GROUP BY tramo_antiguedad
ORDER BY tramo_antiguedad;

-- 4. Churn por cantidad de retrasos de pago en los últimos 90 días
SELECT
    CASE
        WHEN payment_delay_count_90d = 0 THEN '0 retrasos'
        WHEN payment_delay_count_90d = 1 THEN '1 retraso'
        ELSE '2+ retrasos'
    END AS tramo_retrasos_pago,
    COUNT(*) AS clientes,
    SUM(churned) AS clientes_churn,
    ROUND(100.0 * SUM(churned) / NULLIF(COUNT(*), 0), 2) AS tasa_churn_pct
FROM clientes
GROUP BY tramo_retrasos_pago
ORDER BY CASE tramo_retrasos_pago
    WHEN '0 retrasos' THEN 1
    WHEN '1 retraso' THEN 2
    ELSE 3
END;

-- 5. Clientes para revisión comercial: reglas simples, transparentes y no predictivas
SELECT
    customer_id, plan, tenure_months, monthly_fee_clp,
    support_tickets_90d, payment_delay_count_90d, days_since_last_purchase,
    (support_tickets_90d >= 3)
      + (payment_delay_count_90d >= 2)
      + (days_since_last_purchase > 45)
      + (tenure_months <= 6) AS priority_score
FROM clientes
WHERE (support_tickets_90d >= 3)
   OR (payment_delay_count_90d >= 2)
   OR (days_since_last_purchase > 45)
   OR (tenure_months <= 6)
ORDER BY priority_score DESC, monthly_fee_clp DESC
LIMIT 100;
