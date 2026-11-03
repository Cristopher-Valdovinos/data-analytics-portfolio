import pandas as pd
from pathlib import Path

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

carpeta = Path(__file__).parent
ruta = carpeta / "20250926_Directorio_Oficial_EE_2025_20250430_WEB.csv"

df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", decimal=",")

print(df.shape)
print("RBD únicos:", df["RBD"].nunique())
print(df["ESTADO_ESTAB"].value_counts())
print(df["COD_DEPE2"].value_counts())
print(df["RURAL_RBD"].value_counts())
print(df["MAT_TOTAL"].describe())
print(df.isna().sum().sort_values(ascending=False).head(10))
df_ok = df[(df["ESTADO_ESTAB"] == 1) & (df["MATRICULA"] == 1)]
print("Funcionando con matrícula:", df_ok.shape[0])