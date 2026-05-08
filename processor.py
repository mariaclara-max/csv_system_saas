import pandas as pd
import shutil
import os
from datetime import datetime
from config import CHUNK_SIZE
from domain_logger import generar_log_dominios
from internal_logger import generar_internal_log
from error_logger import validar_integridad_archivo, validar_sintaxis_csv
from blacklist_logger import write_blacklist
from storage_manager import StorageManager

def obtener_claves_existentes(path_csv):
    """Carga en memoria los registros que ya existen en el CSV de salida."""
    if not os.path.exists(path_csv) or os.path.getsize(path_csv) == 0:
        return set()
    try:
        df_existente = pd.read_csv(path_csv, usecols=['Email', 'Message', 'Date added'])
        # Creamos una huella única por fila
        return set(df_existente.apply(lambda x: f"{x['Email']}|{x['Message']}|{x['Date added']}", axis=1))
    except:
        return set()

def process_consola(path, consola, conn, log_func):
    entrada = path / "ENTRADA_DIR"
    error_dir = path / "ERROR_DIR"
    logs_dir = path / "LOGS_DIR"
    internal_csv_path = path / "INTERNAL_DIR" / "internal.csv"
    hard_export = path / "HARD_DOMINIO_DIR" / "hard.csv"
    error_log_audit = logs_dir / "Error_log.log"
    lectura_log = logs_dir / "Log_lectura.log"

    # CARGAR MEMORIA (Evita duplicados)
    existentes_internal = obtener_claves_existentes(internal_csv_path)
    existentes_hard = obtener_claves_existentes(hard_export)

    df_internal_total = []
    df_validos_total = []
    blacklist_dup = []
    fechas_csv_hard = set()

    storage = StorageManager(path)
    storage.rotar_backups(dias_maximos=5)

    for file in entrada.glob("*.csv"):
        if file.stat().st_size == 0: continue

        try:
            if not validar_integridad_archivo(file, error_dir, error_log_audit): continue 

            for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE):
                chunk.columns = chunk.columns.str.strip()
                # Generar clave de identidad para el chunk
                chunk['temp_key'] = chunk.apply(lambda x: f"{x['Email']}|{x['Message']}|{x['Date added']}", axis=1)

                # FILTRAR INTERNAL
                internal = chunk[chunk['Bounce type'] == 'Internal'].copy()
                internal_nuevo = internal[~internal['temp_key'].isin(existentes_internal)]
                if not internal_nuevo.empty:
                    internal_nuevo.drop(columns=['temp_key']).to_csv(internal_csv_path, mode='a', index=False, header=not internal_csv_path.exists())
                    df_internal_total.append(internal_nuevo)
                    existentes_internal.update(internal_nuevo['temp_key'])
                
                # FILTRAR HARD
                hard = chunk[chunk['Bounce type'] == 'Hard'].copy()
                hard_nuevo = hard[~hard['temp_key'].isin(existentes_hard)]
                if not hard_nuevo.empty:
                    hard_nuevo.drop(columns=['temp_key']).to_csv(hard_export, mode='a', index=False, header=not hard_export.exists())
                    fechas_csv_hard.update(hard_nuevo['Date added'].astype(str).unique())
                    existentes_hard.update(hard_nuevo['temp_key'])

                    for _, row in hard_nuevo.iterrows():
                        conn.execute("INSERT OR IGNORE INTO hard_emails VALUES (?,?,?,?,?)", 
                                   (row['Email'], row['Message'], row['Date added'], file.name, datetime.now().isoformat()))

                df_validos_total.append(chunk.drop(columns=['temp_key']))

            conn.commit()
            log_func(lectura_log, f"{file.name} | PROCESADO OK (Solo novedades)")

        except Exception as e:
            with open(error_log_audit, "a") as f: f.write(f"ERROR EN {file.name}: {e}\n")
            shutil.move(str(file), str(error_dir / file.name))

    # REPORTES
    if df_internal_total:
        generar_internal_log(pd.concat(df_internal_total), consola, logs_dir / "Internal_Error_log.log")
    if df_validos_total:
        generar_log_dominios(pd.concat(df_validos_total), consola, logs_dir / "Reporte_Dominios.log")