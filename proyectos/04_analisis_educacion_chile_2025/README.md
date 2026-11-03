# 📊 Análisis de Rendimiento Escolar y Asistencia en Chile (2025)

Pipeline integral de analítica de datos aplicada a la educación escolar en Chile. El proyecto integra procesamiento y limpieza de datos masivos con Python, modelado analítico en Google BigQuery y un tablero de control ejecutivo en Microsoft Power BI.

---

## 🎯 Contexto y Objetivos

- **Monitoreo macro:** Evaluar cobertura nacional, asistencia media ponderada y tasas de reprobación.
- **Brechas institucionales:** Contrastar el desempeño entre dependencias (Municipal, Particular Subvencionado, Particular Pagado, SLEP y Corp. Delegada).
- **Control territorial:** Jerarquizar el desempeño regional e identificar brechas entre zonas urbanas y rurales.
- **Focos críticos (Red Flags):** Detectar establecimientos con matrícula significativa (≥ 100 evaluados), baja asistencia (< 85%) y alta reprobación (> 10%).

---
## 🛠️ Stack Tecnológico y Arquitectura
- **Lenguajes:** Python 3.11+, SQL (GoogleSQL / BigQuery Standard SQL).
- **Procesamiento de Datos:** Pandas, NumPy.
- **Cloud Data Warehouse:** Google BigQuery.
- **Visualización y BI:** Microsoft Power BI Desktop, DAX (Data Analysis Expressions).
- **Control de Versiones:** Git, GitHub.

---
## 📈 Hallazgos Analíticos Clave (SQL & BigQuery)

1. **Brecha por Dependencia Administrativa:**
   - La educación particular pagada lidera con la menor tasa de reprobación y asistencia superior al 93%.
   - Los Servicios Locales de Educación Pública (SLEP) y la administración municipal concentran los mayores desafíos de presentismo escolar.

2. **Asistencia Ponderada Nacional:**
   - El promedio ponderado por volumen de matrícula efectiva se situó en **89,9%**, evitando sesgos estadísticos provocados por colegios de baja matrícula rural o unifamiliares.

3. **Volumen General Evaluado:**
   - Universo total: **8.365 establecimientos** y **2.963.675 estudiantes evaluados**, con una tasa nacional de reprobación del **1,74%**.

---

## 📐 Modelado y Medidas DAX (Power BI)

Para garantizar consistencia y dinamismo ante los filtros interactivos, se implementaron las siguientes medidas DAX principales:

```dax
-- Total de Establecimientos Únicos
Total Establecimientos = DISTINCTCOUNT(df_consolidado_bq[RBD])

-- Población Estudiantil Evaluada
Total Evaluados = SUM(df_consolidado_bq[TOTAL_EVALUADOS])

-- Alumnos Reprobados Totales
Total Reprobados = SUM(df_consolidado_bq[TOTAL_REPROBADOS])

-- Tasa de Reprobación
% Reprobación = DIVIDE([Total Reprobados], [Total Evaluados], 0)

-- Asistencia Ponderada por Matrícula
% Asistencia Ponderada = 
DIVIDE(
    SUMX(df_consolidado_bq, df_consolidado_bq[PROM_ASIS_POND] * df_consolidado_bq[TOTAL_EVALUADOS]),
    [Total Evaluados],
    0
) / 100 
```
---

## 🖥️ Tablero de Control Ejecutivo

![Dashboard Power BI](Captura%20dashboard_educacion_chile_2025.png)

### Componentes del Dashboard:
- **Tarjetas KPI Superiores:** Resumen macro de cobertura (colegios, evaluados, % asistencia ponderada, % reprobación).
- **Segmentadores Dinámicos:** Filtros por Región (`NOM_REG_RBD_A`), Dependencia y Área (Urbano / Rural).
- **Gráficos de Análisis:**
  - Reprobación porcentual por región.
  - Benchmark comparativo por dependencia institucional.
- **Tabla Operacional de Detalle:** Directorio navegable con RBD, nombre del colegio, comuna y métricas clave.
---

## 📂 Estructura del Repositorio

```text
proyecto-4-educacion-chile-2025/
├── consultas_bigquery.sql                      # Scripts SQL (Benchmark, Window Functions, Outliers)
├── convertir_bq.py                             # Script de preparación y exportación a formato BigQuery
├── dashboard_educacion_chile_2025.pbix         # Archivo maestro de Power BI Desktop
├── df_consolidado_bq.csv                       # Dataset limpio y normalizado
├── dispersion_asistencia_reprobacion.png       # Gráfico EDA de dispersión estadística
├── Captura dashboard_educacion_chile_2025.png  # Captura del reporte interactivo
├── EDA.py                                      # Análisis exploratorio inicial de datos
├── README.md                                   # Documentación técnica y ejecutiva
└── scripts_apoyo/
    ├── graficar_correlacion.py
    ├── revisar_directorio.py
    └── revisar_rendimiento.py
```
```
## 🚀 Instrucciones de Reproducción
1. **Clonar el repositorio:**
   ```bash
  git clone https://github.com/tu-usuario/proyecto-4-educacion-chile-2025.git
   cd proyecto-4-educacion-chile-2025
```

2. **Carga y análisis SQL (Google BigQuery):**
   - Importar `df_consolidado_bq.csv` en un dataset de BigQuery.
   - Ejecutar las consultas contenidas en `consultas_bigquery.sql`.

3. **Exploración del Dashboard:**
   - Abrir `dashboard_educacion_chile_2025.pbix` en Microsoft Power BI Desktop para interactuar con los filtros y visualizaciones.