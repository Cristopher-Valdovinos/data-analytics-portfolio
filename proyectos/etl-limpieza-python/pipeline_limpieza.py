"""
====================================================================
PROYECTO: ETL, LIMPIEZA DE DATOS Y AUTOMATIZACIÓN DE REPORTES (EDA)
AUTOR: Cristopher Valdovinos (Ingeniero Comercial & Data Analyst)
HERRAMIENTAS: Python (Pandas, NumPy)
====================================================================
"""

import pandas as pd
import numpy as np

def ejecutar_pipeline():
    print("--- 1. INICIANDO EXTRACCIÓN Y CARGA DE DATOS CRUDOS ---")
    
    # Simulación de datos desordenados típicos de sistemas transaccionales
    data_cruda = {
        'id_transaccion': [101, 102, 103, 104, 105, 106, 107, 107], # Contiene un duplicado
        'fecha': ['2026-01-15', '2026-01-16', '2026-02-01', 'fecha_invalida', '2026-02-15', '2026-03-01', '2026-03-05', '2026-03-05'],
        'cliente': [' EMPRESA ALFA ', 'Servicios Beta', 'Comercial Gamma', 'Distribuidora Delta', np.nan, 'Inversiones Epsilon', 'Empresa Alfa', 'Empresa Alfa'],
        'monto': ['$1,200.50', '$450.00', np.nan, '$3,100.00', '$850.20', '-$200.00', '$1,200.50', '$1,200.50'], # Formatos sucios y valores negativos
        'categoria': ['tecnologia', 'Accesorios', 'TECNOLOGIA', 'Mobiliario', 'accesorios', 'Tecnologia', 'tecnologia', 'tecnologia']
    }
    
    df = pd.DataFrame(data_cruda)
    print(f"Dimensiones iniciales: {df.shape[0]} filas, {df.shape[1]} columnas.\n")

    print("--- 2. FASE DE TRANSFORMACIÓN Y LIMPIEZA DE DATOS ---")
    
    # 2.1 Eliminación de duplicados exactos
    df = df.drop_duplicates(subset=['id_transaccion']).copy()
    
    # 2.2 Estandarización de texto (quitar espacios en blanco y mayúsculas/minúsculas)
    df['cliente'] = df['cliente'].fillna('Sin Registrar').str.strip().str.title()
    df['categoria'] = df['categoria'].str.strip().str.capitalize()
    
    # 2.3 Corrección de tipos de fecha (coerción de errores a NaT)
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    # Imputación de fechas faltantes con la mediana o descarte controlado
    df = df.dropna(subset=['fecha']).copy()
    
    # 2.4 Limpieza de variables numéricas (remoción de símbolos monetarios y strings)
    df['monto'] = (
        df['monto']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.replace(',', '', regex=False)
    )
    df['monto'] = pd.to_numeric(df['monto'], errors='coerce')
    
    # Tratar inconsistencias de negocio: montos nulos imputados por la media y corrección de negativos
    monto_promedio = df.loc[df['monto'] > 0, 'monto'].median()
    df['monto'] = df['monto'].fillna(monto_promedio)
    df['monto'] = df['monto'].apply(lambda x: abs(x)) # Corrección de registros erróneos negativos
    
    print("Transformaciones completadas con éxito.")
    print(df.info())
    print("\n--- 3. RESUMEN EJECUTIVO (CONTROL DE GESTIÓN) ---")
    
    # Resumen analítico por categoría
    resumen = df.groupby('categoria').agg(
        transacciones=('id_transaccion', 'count'),
        ingreso_total=('monto', 'sum'),
        ticket_promedio=('monto', 'mean')
    ).reset_index()
    
    resumen['ticket_promedio'] = resumen['ticket_promedio'].round(2)
    print(resumen.to_string(index=False))

    return df, resumen

if __name__ == "__main__":
    df_limpio, resumen_ejecutivo = ejecutar_pipeline()
