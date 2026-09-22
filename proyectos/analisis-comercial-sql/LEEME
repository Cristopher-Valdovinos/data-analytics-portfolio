# 📊 Análisis Comercial, Rentabilidad y KPIs de Clientes con SQL

## 🎯 Contexto de Negocio
Este proyecto simula el análisis de control de gestión para una empresa retail/B2B. El objetivo es responder preguntas clave de rentabilidad, comportamiento de clientes y evolución del ticket promedio para apoyar la toma de decisiones comerciales.

---

## 🛠️ Competencias Técnicas Demostradas
* **Motor:** MySQL
* **Modelado Relacional:** Diseño de tablas dimensionales (`clientes`, `productos`) y tabla de hechos (`ventas`).
* **Consultas Avanzadas:** 
  * Uniones relacionales (`INNER JOIN`).
  * Agregaciones y métricas calculadas (`SUM`, `ROUND`, ratios de margen).
  * Funciones de ventana (`DENSE_RANK() OVER (...)`).
  * Expresiones de tabla comunes (`WITH / CTE`) para consolidación mensual.

---

## 📈 Hallazgos y Preguntas de Negocio Resueltas

### 1. Margen Bruto y Rentabilidad por Categoría
* Se calculó el ingreso total, costo total y margen porcentual por categoría de producto.
* **Impacto de gestión:** Permite identificar qué líneas aportan mayor volumen de facturación frente a cuáles entregan el mejor retorno operativo.

### 2. Segmentación y Ranking de Clientes (Pareto Comercial)
* Implementación de `DENSE_RANK()` para jerarquizar clientes por monto facturado.
* **Impacto de gestión:** Facilita la detección del 20% de cuentas que generan el 80% del flujo, focalizando estrategias de retención para cuentas corporativas.

### 3. Dinámica Mensual y Ticket Promedio
* Mediante una `CTE`, se agruparon transacciones e ingresos por mes calendario.
* **Impacto de gestión:** Permite monitorear la variación en el tamaño promedio de orden frente a metas operacionales.

---

## 📁 Archivos del Módulo
* `analisis_ventas.sql`: Script DDL y DML completo con esquema, poblamiento de datos y consultas analíticas.
