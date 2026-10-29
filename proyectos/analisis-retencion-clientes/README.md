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

## Resultados del escenario simulado

Con la semilla `20261028`, el conjunto genera estos resultados reproducibles:

| Indicador | Resultado |
|---|---:|
| Clientes simulados | 1.200 |
| Clientes con churn | 248 |
| Tasa general de churn | 20,67% |
| Cargo mensual asociado a clientes con churn | $4.868.520 CLP |
| Cargo mensual promedio por cliente | $19.975 CLP |

### Hallazgos descriptivos

- **La antigüedad inicial concentra una tasa de churn más alta:** 35,48% en clientes de 1–3 meses y 35,00% en clientes de 4–6 meses, frente a 18,18% en el grupo de 25–60 meses.
- **Los retrasos de pago aparecen asociados a una mayor tasa de churn en esta simulación:** 35,04% para clientes con dos o más retrasos en 90 días. Este dato describe una asociación del dataset sintético; no prueba causalidad.
- **El plan Básico tiene la mayor tasa por plan:** 21,72%, frente a 19,87% en Estándar y 19,59% en Premium.
- **El cargo mensual asociado al churn no es una pérdida futura confirmada:** representa la suma de los cargos de los clientes etiquetados con churn en el escenario simulado.

> **Limitación metodológica importante:** las etiquetas de churn se generaron mediante una regla probabilística que utiliza variables como antigüedad, tickets de soporte, retrasos de pago y actividad reciente. Por tanto, estos resultados sirven para demostrar un flujo de análisis reproducible, no para afirmar que esas relaciones existen en una empresa real ni para validar un modelo predictivo.

### Recomendaciones de negocio para probar

1. Diseñar un contacto de bienvenida y seguimiento durante los primeros seis meses, con medición de retención por cohorte.
2. Revisar motivos y resolución de tickets de soporte antes de definir acciones específicas.
3. Probar recordatorios de pago y seguimiento preventivo para clientes con retrasos, midiendo el resultado contra un grupo de control.
4. Evaluar cada iniciativa mediante tasa de retención incremental, margen retenido y coste por cliente retenido; no solo por número de contactos.

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
