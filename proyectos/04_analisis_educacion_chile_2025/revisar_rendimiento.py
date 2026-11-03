from pathlib import Path
import numpy as np
import pandas as pd

carpeta = Path(__file__).parent
datos = carpeta / "Directorio-Oficial-EE-2025"

# 1. Cargar datos
print("Cargando bases...")
rend = pd.read_csv(
    datos / "20260303_Resumen_Rendimiento_2025_20260131.csv",
    sep=",",
    encoding="utf-8-sig",
)
dire = pd.read_csv(
    datos / "20250926_Directorio_Oficial_EE_2025_20250430_WEB.csv",
    sep=";",
    encoding="utf-8-sig",
    decimal=",",
)

# 2. Filtrar universo principal: Funcionando (ESTADO_ESTAB == 1) y Niveles Regulares Niños/Jóvenes (2, 5, 7)
rend_reg = rend[
    (rend["ESTADO_ESTAB"] == 1) & (rend["COD_ENSE2"].isin([2, 5, 7]))
].copy()

# 3. Calcular totales por fila/unidad
col_apr = [
    c
    for c in ["APR_HOM_TO", "APR_MUJ_TO", "APR_SI_TO", "APR_NB"]
    if c in rend_reg.columns
]
col_rep = [
    c
    for c in ["REP_HOM_TO", "REP_MUJ_TO", "REP_SI_TO"]
    if c in rend_reg.columns
]
col_ret = [
    c
    for c in ["RET_HOM_TO", "RET_MUJ_TO", "RET_SI_TO"]
    if c in rend_reg.columns
]

rend_reg["TOTAL_APR"] = rend_reg[col_apr].fillna(0).sum(axis=1)
rend_reg["TOTAL_REP"] = rend_reg[col_rep].fillna(0).sum(axis=1)
rend_reg["TOTAL_RET"] = rend_reg[col_ret].fillna(0).sum(axis=1)
rend_reg["EVALUADOS"] = rend_reg["TOTAL_APR"] + rend_reg["TOTAL_REP"]

# Ponderador para asistencia (solo filas con asistencia válida y evaluados > 0)
asis_valida = rend_reg["PROM_ASIS"].notna() & (rend_reg["EVALUADOS"] > 0)
rend_reg["EVALUADOS_ASIS"] = np.where(asis_valida, rend_reg["EVALUADOS"], 0)
rend_reg["POND_ASIS"] = np.where(
    asis_valida, rend_reg["PROM_ASIS"] * rend_reg["EVALUADOS"], 0
)

# 4. Agregación a nivel de Establecimiento (1 fila por RBD)
agg_rend = (
    rend_reg.groupby("RBD")
    .agg(
        TOTAL_EVALUADOS=("EVALUADOS", "sum"),
        TOTAL_APROBADOS=("TOTAL_APR", "sum"),
        TOTAL_REPROBADOS=("TOTAL_REP", "sum"),
        TOTAL_RETIRADOS=("TOTAL_RET", "sum"),
        SUMA_POND_ASIS=("POND_ASIS", "sum"),
        SUMA_EVAL_ASIS=("EVALUADOS_ASIS", "sum"),
    )
    .reset_index()
)

# Indicadores finales calculados
agg_rend["PROM_ASIS_POND"] = np.where(
    agg_rend["SUMA_EVAL_ASIS"] > 0,
    agg_rend["SUMA_POND_ASIS"] / agg_rend["SUMA_EVAL_ASIS"],
    np.nan,
)

agg_rend["TASA_APROBACION"] = np.where(
    agg_rend["TOTAL_EVALUADOS"] > 0,
    (agg_rend["TOTAL_APROBADOS"] / agg_rend["TOTAL_EVALUADOS"]) * 100,
    np.nan,
)

agg_rend["TASA_REPROBACION"] = np.where(
    agg_rend["TOTAL_EVALUADOS"] > 0,
    (agg_rend["TOTAL_REPROBADOS"] / agg_rend["TOTAL_EVALUADOS"]) * 100,
    np.nan,
)

agg_rend.drop(columns=["SUMA_POND_ASIS", "SUMA_EVAL_ASIS"], inplace=True)

# 5. Cruce con el Directorio Oficial
dire_sub = dire[
    [
        "RBD",
        "NOM_RBD",
        "COD_REG_RBD",
        "NOM_REG_RBD_A",
        "COD_COM_RBD",
        "NOM_COM_RBD",
        "COD_DEPE2",
        "RURAL_RBD",
        "PAGO_MATRICULA",
        "PAGO_MENSUAL",
    ]
].drop_duplicates("RBD")

df_final = pd.merge(agg_rend, dire_sub, on="RBD", how="inner")

print("Dimensiones base final consolidada:", df_final.shape)
print("\nPrimeras 5 filas:")
print(
    df_final[
        [
            "RBD",
            "NOM_RBD",
            "NOM_COM_RBD",
            "TOTAL_EVALUADOS",
            "PROM_ASIS_POND",
            "TASA_APROBACION",
        ]
    ].head()
)

# Guardar base procesada lista para análisis/BI
df_final.to_csv(
    datos / "df_consolidado_establecimientos_2025.csv",
    index=False,
    sep=";",
    decimal=",",
    encoding="utf-8-sig",
)
print(
    "\nArchivo 'df_consolidado_establecimientos_2025.csv' guardado exitosamente."
)