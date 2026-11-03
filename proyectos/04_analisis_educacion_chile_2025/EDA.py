import pandas as pd
from pathlib import Path

carpeta = Path(__file__).parent
df = pd.read_csv(
    carpeta / "df_consolidado_establecimientos_2025.csv",
    sep=";",
    decimal=",",
    encoding="utf-8-sig"
)

print("--- NULOS EN INDICADORES ---")
print(df[["PROM_ASIS_POND", "TASA_APROBACION", "TASA_REPROBACION"]].isna().sum())

print("\n--- RESUMEN ESTADÍSTICO ---")
print(df[["TOTAL_EVALUADOS", "PROM_ASIS_POND", "TASA_APROBACION", "TASA_REPROBACION"]].describe().round(2))

print("\n--- VALORES EXTREMOS (OUTLIERS) ---")
print("Colegios con 0% asistencia ponderada:", len(df[df["PROM_ASIS_POND"] == 0]))
print("Colegios con 100% asistencia ponderada:", len(df[df["PROM_ASIS_POND"] == 100]))
print("Colegios con 100% reprobación:", len(df[df["TASA_REPROBACION"] == 100]))