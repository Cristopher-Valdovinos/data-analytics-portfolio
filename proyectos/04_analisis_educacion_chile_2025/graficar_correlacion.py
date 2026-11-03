import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

carpeta = Path(__file__).parent

# 1. Cargar datos consolidados
df = pd.read_csv(
    carpeta / "Directorio-Oficial-EE-2025" / "df_consolidado_establecimientos_2025.csv",
    sep=";",
    decimal=",",
    encoding="utf-8-sig",
)

# 2. Filtrar filas con datos válidos en los indicadores clave
df_plot = df.dropna(subset=["PROM_ASIS_POND", "TASA_REPROBACION"]).copy()

# 3. Mapear dependencias administrativas según diccionario oficial
dic_depe = {
    1: "Municipal",
    2: "Part. Subvencionado",
    3: "Part. Pagado",
    4: "Corp. Administración Delegada",
    5: "SLEP"
}
df_plot["Dependencia"] = df_plot["COD_DEPE2"].map(dic_depe)

# 4. Configurar estética del gráfico
sns.set_theme(style="whitegrid", font_scale=1.0)
fig, ax = plt.subplots(figsize=(11, 6.5))

colores = {
    "Municipal": "#e74c3c",
    "Part. Subvencionado": "#3498db",
    "Part. Pagado": "#2ecc71",
    "Corp. Administración Delegada": "#9b59b6",
    "SLEP": "#e67e22"
}

sns.scatterplot(
    data=df_plot,
    x="PROM_ASIS_POND",
    y="TASA_REPROBACION",
    hue="Dependencia",
    palette=colores,
    alpha=0.45,
    s=35,
    ax=ax
)

# Acotar visualización para descartar ruido extremo y centrar el análisis
ax.set_xlim(65, 100)
ax.set_ylim(-0.5, 30)

ax.set_title("Relación entre Asistencia Ponderada y Tasa de Reprobación (Chile, 2025)", fontsize=13, weight="bold", pad=15)
ax.set_xlabel("Asistencia Promedio Ponderada (%)", fontsize=11)
ax.set_ylabel("Tasa de Reprobación (%)", fontsize=11)
ax.legend(title="Dependencia Administrativa", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)

plt.tight_layout()

# Guardar imagen en alta resolución para el repositorio de GitHub
ruta_grafico = carpeta / "dispersion_asistencia_reprobacion.png"
plt.savefig(ruta_grafico, dpi=300, bbox_inches="tight")
print(f"Gráfico guardado en: {ruta_grafico.name}")
plt.show()

# 5. Cálculo analítico de correlaciones
print("\n--- COEFICIENTES DE CORRELACIÓN DE PEARSON (Asistencia vs. Reprobación) ---")
corr_global = df_plot["PROM_ASIS_POND"].corr(df_plot["TASA_REPROBACION"])
print(f"Global Nacional: {corr_global:.4f}")

for codigo, nombre in dic_depe.items():
    sub = df_plot[df_plot["COD_DEPE2"] == codigo]
    if len(sub) > 1:
        corr_depe = sub["PROM_ASIS_POND"].corr(sub["TASA_REPROBACION"])
        print(f"{nombre} (n={len(sub):,}): r = {corr_depe:.4f}")
        