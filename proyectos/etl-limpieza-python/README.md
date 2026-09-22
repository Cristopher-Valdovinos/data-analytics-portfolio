# 🐍 Pipeline ETL y Limpieza Automatizada de Datos con Python

## 🎯 Contexto de Negocio
En entornos comerciales y de control de gestión, los datos extraídos de sistemas transaccionales suelen presentar inconsistencias: formatos de texto heterogéneos, caracteres monetarios en campos numéricos, registros duplicados y valores nulos. 

Este proyecto implementa un script en **Python (Pandas & NumPy)** para estandarizar, validar y generar un resumen ejecutivo automatizado de transacciones comerciales.

---

## 🛠️ Habilidades Técnicas Aplicadas
* **Librerías:** `pandas`, `numpy`.
* **Depuración de Datos:**
  * Deduplicación de registros basados en identificador único (`drop_duplicates`).
  * Normalización de cadenas de texto (eliminación de espacios y corrección de capitalización con `.str.strip()` y `.str.title()`).
  * Tratamiento de fechas con manejo de errores forzados (`pd.to_datetime(..., errors='coerce')`).
  * Limpieza de strings monetarios y casting a tipos numéricos continuos (`pd.to_numeric`).
  * Imputación controlada de valores nulos utilizando medidas de tendencia central (mediana).
* **Agregación & KPIs:** Resumen de facturación, transacciones y ticket promedio agrupado por categoría mediante `.groupby().agg()`.

---

## 📈 Impacto en Control de Gestión
* **Ahorro de tiempo:** Sustituye tareas manuales repetitivas de limpieza en hojas de cálculo.
* **Calidad de datos:** Asegura que los datos alimenten correctamente dashboards de Power BI o bases relacionales sin distorsionar márgenes ni totales de venta.

---

## 📁 Archivos del Módulo
* `pipeline_limpieza.py`: Código ejecutable con el pipeline de limpieza y consolidación.
