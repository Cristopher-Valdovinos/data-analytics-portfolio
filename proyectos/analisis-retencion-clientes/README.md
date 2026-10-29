# Análisis de retención y riesgo de fuga de clientes

## Contexto de negocio
Una empresa de suscripción necesita entender qué perfiles presentan mayor fuga (*churn*), qué ingresos están expuestos y dónde priorizar acciones de retención. Este proyecto simula un caso de analítica comercial de principio a fin.

> **Transparencia:** los datos son sintéticos y se generan con una semilla fija. No representan clientes ni resultados de una empresa real. Las relaciones incorporadas en la simulación sirven para practicar el análisis, no para demostrar causalidad.

## Preguntas de negocio
1. ¿Cuál es la tasa general de fuga y cómo varía por plan?
2. ¿Qué relación se observa entre antigüedad y fuga?
3. ¿Qué segmentos concentran más clientes e ingresos en riesgo?
4. ¿Qué acciones de retención convendría probar y cómo medir su impacto?

## Stack
- **Python:** generación reproducible de datos y análisis con pandas.
- **SQL (MySQL 8+):** KPIs, segmentación y priorización de clientes.
- **Analítica de negocio:** definición de métricas, interpretación y recomendaciones.

## Estructura
```text
analisis-retencion-clientes/
├── README.md
├── requirements.txt
├── data/                  # Se genera localmente; no contiene datos reales
├── sql/
│   └── consultas_retencion.sql
└── src/
    ├── generar_datos.py
    └── analizar_retencion.py
```

## Cómo ejecutarlo
Desde la carpeta `proyectos/analisis-retencion-clientes`:

```bash
python -m pip install -r requirements.txt
python src/generar_datos.py
python src/analizar_retencion.py
```

El generador crea `data/clientes.csv` con 1.200 registros reproducibles. El análisis imprime KPIs y guarda tablas agregadas en `outputs/`. No requiere API ni credenciales.

## Definiciones
- **Churn:** cliente marcado como dado de baja en el periodo simulado (`churned = 1`).
- **Tasa de churn:** clientes con churn dividido por clientes del segmento.
- **Ingreso mensual en riesgo:** suma del cargo mensual de clientes con churn, útil como exposición descriptiva; no equivale a pérdida futura confirmada.
- **Segmento de riesgo operativo:** regla transparente basada en tickets de soporte, retrasos de pago y días desde la última compra. Es una priorización exploratoria, no un modelo predictivo validado.

## Criterios de calidad
- Identificador único por cliente.
- Validación de nulos, duplicados y rangos básicos.
- Semilla fija para poder reproducir los resultados.
- Separación entre datos, código, consultas y resultados.
- Interpretación prudente: asociación no implica causalidad y los datos sintéticos limitan la generalización.

## Entregables
- `outputs/kpis_generales.csv`
- `outputs/churn_por_plan.csv`
- `outputs/churn_por_antiguedad.csv`
- `outputs/clientes_priorizados.csv`

## Próximas mejoras
1. Incorporar datos reales anonimizados y diccionario de datos.
2. Diseñar un dashboard en Power BI con filtros por plan, antigüedad y riesgo.
3. Evaluar una intervención de retención con grupo de control y medir retención incremental, margen y coste por cliente retenido.
4. Si se dispone de datos temporales suficientes, evaluar un modelo predictivo con validación temporal y métricas adecuadas.

---
Proyecto de portafolio de Cristopher Valdovinos | Ingeniería Comercial · Data Analytics & Reporting
