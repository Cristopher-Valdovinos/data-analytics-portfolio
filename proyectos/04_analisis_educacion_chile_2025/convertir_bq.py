import pandas as pd
from pathlib import Path

carpeta = Path(__file__).parent
datos = carpeta / "Directorio-Oficial-EE-2025"

# 1. Leer el archivo generado anteriormente (separado por ; y decimal con ,)
df = pd.read_csv(
    datos / "df_consolidado_establecimientos_2025.csv",
    sep=";",
    decimal=","
)

# 2. Guardar versión estándar para BigQuery (separado por , y decimal con .)
ruta_salida = carpeta / "df_consolidado_bq.csv"
df.to_csv(ruta_salida, index=False, sep=",", decimal=".")

print(f"Archivo generado exitosamente: {ruta_salida.name}")
print(f"Filas: {len(df)} | Columnas: {len(df.columns)}")