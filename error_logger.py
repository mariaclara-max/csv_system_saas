# error_logger.py
import os
import re
import shutil
import pandas as pd
from classifier import clasificar_error

def validar_integridad_archivo(file_path, error_dir, audit_log_path):
    """Regla 1: El nombre debe ser bounce-stats-ID-FECHA.csv"""
    filename = file_path.name
    pattern = r"^bounce-stats-[a-z0-9]+-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.csv$"
    
    if not re.match(pattern, filename):
        with open(audit_log_path, "a", encoding="utf-8") as f:
            f.write(f"--- ERROR NOMBRE --- {pd.Timestamp.now()}\n")
            f.write(f"ARCHIVO: {filename} \n\n    | MOTIVO: El nombre no cumple con el formato requerido.\n\n")
        
        if not os.path.exists(error_dir): os.makedirs(error_dir)
        shutil.move(str(file_path), os.path.join(error_dir, filename))
        return False
    return True

def validar_sintaxis_csv(file_path, chunk, error_dir, audit_log_path):
    """Regla 2: Cada línea debe tener Email con @, Bounce type válido y Fecha real."""
    columnas_esperadas = ['Email', 'Bounce type', 'Message', 'Date added']
    
    # Validar encabezados
    if not all(col in chunk.columns for col in columnas_esperadas):
        with open(audit_log_path, "a", encoding="utf-8") as f:
            f.write(f"--- ERROR ESTRUCTURA --- {pd.Timestamp.now()}\n")
            f.write(f"ARCHIVO: {file_path.name} \n\n     | MOTIVO: Columnas faltantes o corruptas.\n\n")
        if not os.path.exists(error_dir): os.makedirs(error_dir)
        shutil.move(str(file_path), os.path.join(error_dir, file_path.name))
        return False

    lineas_con_fallo = []
    for idx, row in chunk.iterrows():
        errores_fila = []
        email = str(row.get('Email', ''))
        b_type = str(row.get('Bounce type', ''))
        fecha = str(row.get('Date added', ''))

        if "@" not in email:
            errores_fila.append(f"Email inválido ({email})")
        if b_type not in ['Soft', 'Hard', 'Internal']:
            errores_fila.append(f"Tipo desconocido ({b_type})")
        if pd.to_datetime(fecha, errors='coerce') is pd.NaT:
            errores_fila.append(f"Fecha corrupta ({fecha})")

        if errores_fila:
            linea_str = ",".join([str(v) for v in row.values])
            lineas_con_fallo.append(f"ARCHIVO: {file_path.name} \n\n  | LINEA: [{linea_str}] \n\n  | FALLOS: {'; '.join(errores_fila)}")
            f.write("\n\n ")
    if lineas_con_fallo:
        with open(audit_log_path, "a", encoding="utf-8") as f:
            f.write(f"--- ERROR SINTAXIS --- {pd.Timestamp.now()}\n")
            f.write("\n".join(lineas_con_fallo) + "\n\n")
        
        if not os.path.exists(error_dir): os.makedirs(error_dir)
        shutil.move(str(file_path), os.path.join(error_dir, file_path.name))
        return False
        
    return True

def generar_error_log(df, consola, output_path, titulo="REPORTE DE MENSAJES"):
    """Genera el log de mensajes clasificados (solo para archivos sanos)"""
    if df is None or df.empty: return
    df = df.copy()
    df['error_limpio'] = df['Message'].fillna("").map(clasificar_error)
    
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"CONSOLA: {consola} \n\n  | TOTAL: {len(df)} registros\n")
        resumen = df['error_limpio'].value_counts()
        for err, cant in resumen.items():
            f.write(f"{err.upper()}: {cant}\n")
        f.write("-" * 30 + "\n")