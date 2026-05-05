# csv_system/internal_logger.py

import pandas as pd
import os
import re 
from classifier import clasificar_error

# CAMBIO AQUÍ: Se cambió el nombre de 'generar_error_log' a 'generar_internal_log'
def generar_internal_log(df, consola, output_path, overwrite=False):
    """
    Genera un log de errores agrupado por día.
    """
    if df is None or df.empty:
        print(f"Aviso: No hay datos para procesar en la consola {consola}. Saltando log.")
        return

    if 'Date added' not in df.columns or 'Message' not in df.columns:
        print(f"Error: El archivo para {consola} no tiene las columnas necesarias.")
        return
    
    df = df.copy()

    # LIMPIEZA DE COLUMNAS
    df.columns = (df.columns.str.strip().str.replace('\ufeff', '', regex=False))

    # VALIDACIÓN DE COLUMNAS
    required_cols = ['Date added', 'Message']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}.")

    # LIMPIEZA Y CONVERSIÓN DE FECHAS
    df['Date added'] = df['Date added'].astype(str).str.strip().str.replace(r"[^\x00-\x7F]+", "", regex=True)
    df['dt_temp'] = pd.to_datetime(df['Date added'], errors='coerce')
    df['fecha_grupo'] = df['dt_temp'].dt.strftime("%d / %m / %Y")
    df.loc[df['dt_temp'].isna(), 'fecha_grupo'] = "FECHA NO RECONOCIDA"

    # CLASIFICACIÓN DE ERRORES
    df['error_limpio'] = df['Message'].fillna("").map(clasificar_error)

    # CONTROL DE ESCRITURA
    if overwrite and os.path.exists(output_path):
        os.remove(output_path)

    # ESCRIBIR GLOSARIO (solo si archivo nuevo)
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("============================================================\n")
            f.write("             GLOSARIO DE CATEGORÍAS DE ERROR\n")
            f.write("============================================================\n")
            f.write("• LOW_REPUTATION_OR_IP_BLOCKED: Bloqueo por IP en listas negras.\n")
            f.write("• GMAIL_RATE_LIMIT: Gmail detectó demasiados envíos.\n")
            f.write("• QUOTA_EXCEEDED: El buzón del destinatario está lleno.\n")
            f.write("• MAILBOX_NOT_FOUND: El correo no existe.\n")
            f.write("• CONNECTION_ERROR: Fallo técnico de red.\n")
            f.write("• ARUBA_SPECIFIC_BLOCK: Bloqueo específico de Aruba.it.\n")
            f.write("• SPAM_FILTER_REJECTION: Marcado como spam.\n")
            f.write("• BLOCKED_OR_SPAM: Bloqueo por spam.\n")
            f.write("• UNKNOWN_ERROR: Errores no clasificados.\n")
            f.write("============================================================\n\n")
    
    # Comprobacion de fechas ya escritas
    fechas_ya_escritas = []
    if os.path.exists(output_path) and not overwrite:
        with open(output_path, "r", encoding="utf-8") as f_leido:
            contenido = f_leido.read()
            fechas_ya_escritas = re.findall(r"FECHA DATA CSV: (\d{2} / \d{2} / \d{4})", contenido)
    
    mode = "w" if overwrite else "a"
    with open(output_path, mode, encoding="utf-8") as f:
        f.write(f"CONSOLA: {consola}\n")
        for fecha, grupo in df.groupby('fecha_grupo', sort=True):
            if fecha in fechas_ya_escritas:
                continue

            f.write("==========================================\n")
            f.write(f"FECHA CREACION CSV: {fecha}\n")
            f.write("==========================================\n")

            conteo = grupo['error_limpio'].value_counts()
            for error_tipo, total in conteo.items():
                nombre_visual = error_tipo.replace("_", " ").upper()
                f.write(f"MENSAJE: {nombre_visual}\n")
                f.write(f"NUM_TOTAL_MENSAJE: {total}\n")
                f.write("-" * 30 + "\n")
            f.write("\n")