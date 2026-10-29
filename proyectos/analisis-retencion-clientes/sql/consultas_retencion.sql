-- Proyecto: Análisis de retención y riesgo de fuga
-- Motor: MySQL 8+
-- Cargar data/clientes.csv en una tabla llamada clientes.
-- Los datos son sintéticos. Ingreso asociado a churn es descriptivo, no pérdida futura confirmada.

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

-- 4. Clientes para revisión comercial: reglas simples, transparentes y no predictivas
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
