# processor.py
import pandas as pd
import shutil
import os
from datetime import datetime
from config import CHUNK_SIZE
from domain_logger import generar_log_dominios
from internal_logger import generar_internal_log
from error_logger import generar_error_log, validar_integridad_archivo, validar_sintaxis_csv
from blacklist_logger import write_blacklist
from storage_manager import StorageManager



def realizar_backups(path, db_path):
    """Crea una copia de seguridad de la DB y resultados antes de procesar."""
    backup_dir = path / "BACKUPS_DIR"
    if not backup_dir.exists(): 
        os.makedirs(backup_dir)
    
    fecha_str = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Backup de Base de Datos
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_dir / f"database_backup_{fecha_str}.db")
    
    # Backup de archivos de salida actuales
    hard_csv = path / "HARD_DOMINIO_DIR" / "hard.csv"
    internal_csv = path / "INTERNAL_DIR" / "internal.csv"
    
    if hard_csv.exists():
        shutil.copy2(hard_csv, backup_dir / f"hard_backup_{fecha_str}.csv")
    if internal_csv.exists():
        shutil.copy2(internal_csv, backup_dir / f"internal_backup_{fecha_str}.csv")

def process_consola(path, consola, conn, log_func):
    # --- Configuración de Rutas ---
    entrada = path / "ENTRADA_DIR"
    error_dir = path / "ERROR_DIR"
    logs_dir = path / "LOGS_DIR"
    internal_csv_path = path / "INTERNAL_DIR" / "internal.csv"
    hard_export = path / "HARD_DOMINIO_DIR" / "hard.csv"
    
    db_path = "hard_emails.db" # Ruta de tu base de datos SQLite
    error_log_audit = logs_dir / "Error_log.log"
    lectura_log = logs_dir / "Log_lectura.log"

    # --- 1. EJECUCIÓN DE BACKUP PREVENTIVO ---
    try:
        realizar_backups(path, db_path)
    except Exception as e:
        with open(error_log_audit, "a") as f:
            f.write(f"ALERTA BACKUP: No se pudo realizar el backup: {e}\n")

    # --- 2. ACUMULADORES PARA REPORTES ---
    df_internal_total = []
    df_mensajes_total = []
    df_validos_total = []
    blacklist_dup = []
    fechas_csv_hard = set()

        # Inicializamos el gestor de almacenamiento
    storage = StorageManager(path)

    # --- 1. Mantenimiento al iniciar ---
    storage.rotar_backups(dias_maximos=5) # Solo guardamos 5 días de backups

    for file in entrada.glob("*.csv"):
        if file.stat().st_size == 0: continue

        try:
            # --- 3. FASE DE AUDITORÍA (Nombre y Sintaxis) ---
            if not validar_integridad_archivo(file, error_dir, error_log_audit):
                continue 

            es_valido = True
            for chunk_val in pd.read_csv(file, chunksize=CHUNK_SIZE):
                chunk_val.columns = chunk_val.columns.str.strip()
                if not validar_sintaxis_csv(file, chunk_val, error_dir, error_log_audit):
                    es_valido = False
                    break
            if not es_valido: continue

            # --- 4. FASE DE PROCESAMIENTO (Datos Sanos) ---
            for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE):
                chunk.columns = chunk.columns.str.strip()
                
                # Separación por tipo de rebote
                internal = chunk[chunk['Bounce type'] == 'Internal']
                hard = chunk[chunk['Bounce type'] == 'Hard'].copy()

                # A. Gestión de INTERNAL
                if not internal.empty:
                    internal.to_csv(internal_csv_path, mode='a', index=False, header=not internal_csv_path.exists())
                    df_internal_total.append(internal)
                
                # B. Gestión de HARD (Con Lógica de Duplicados Inteligente)
                if not hard.empty:
                    # Guardamos en el CSV histórico de dominios
                    hard.to_csv(hard_export, mode='a', index=False, header=not hard_export.exists())
                    fechas_csv_hard.update(hard['Date added'].astype(str).unique())

                    for _, row in hard.iterrows():
                        email = row['Email']
                        msg = row['Message']
                        fecha_rebote = row['Date added']

                        # Comprobar si ya existe este email con este mensaje exacto
                        registro_previo = conn.execute(
                            "SELECT date_added FROM hard_emails WHERE email=? AND message=?", 
                            (email, msg)
                        ).fetchone()

                        if registro_previo:
                            fecha_existente = registro_previo[0]
                            
                            # Si la fecha es distinta, es una recurrencia (Blacklist)
                            if fecha_existente != fecha_rebote:
                                blacklist_dup.append(email)
                            
                            # Si la fecha es igual, es el mismo dato (Archivo actualizado), se ignora
                            continue
                        else:
                            # Es un registro totalmente nuevo, lo guardamos
                            conn.execute("""
                                INSERT INTO hard_emails (email, message, date_added, file_name, processed_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (email, msg, fecha_rebote, file.name, datetime.now().isoformat()))

                df_mensajes_total.append(chunk)
                df_validos_total.append(chunk)

            conn.commit() # Guardamos cambios en SQLite por cada archivo procesado
            log_func(lectura_log, f"{file.name} | PROCESADO OK")

        except Exception as e:
            with open(error_log_audit, "a", encoding="utf-8") as f:
                f.write(f"ARCHIVO: {file.name} | ERROR CRÍTICO: {str(e)}\n")
            if not error_dir.exists(): os.makedirs(error_dir)
            shutil.move(str(file), str(error_dir / file.name))

    # --- 5. GENERACIÓN DE LOGS Y REPORTES FINALES ---
    if df_internal_total:
        generar_internal_log(pd.concat(df_internal_total), consola, logs_dir / "Internal_Error_log.log")

    if df_validos_total:
        generar_log_dominios(pd.concat(df_validos_total), consola, logs_dir / "Reporte_Dominios.log")

    if blacklist_dup:
        rango_fechas = f"{min(fechas_csv_hard)} a {max(fechas_csv_hard)}" if fechas_csv_hard else "N/A"
        write_blacklist(logs_dir / "blacklist.log", consola, blacklist_dup, fecha_csv=rango_fechas)