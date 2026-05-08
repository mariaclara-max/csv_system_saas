import pandas as pd
import shutil
import os
from datetime import datetime
from config import CHUNK_SIZE
from domain_logger import generar_log_dominios
from internal_logger import generar_internal_log
from error_logger import validar_integridad_archivo, validar_sintaxis_csv
from storage_manager import StorageManager

def obtener_claves_existentes(path_csv):
    """Lee el CSV histórico y devuelve un set de 'Emails|Mensaje|Fecha'."""
    if not os.path.exists(path_csv) or os.path.getsize(path_csv) == 0:
        return set()
    try:
        # Cargamos solo las columnas de identidad para no saturar la RAM
        df_existente = pd.read_csv(path_csv, usecols=['Email', 'Message', 'Date added'])
        return set(df_existente.apply(lambda x: f"{x['Email']}|{x['Message']}|{x['Date added']}", axis=1))
    except Exception:
        return set()

def process_consola(path, consola, conn, log_func):
    entrada = path / "ENTRADA_DIR"
    error_dir = path / "ERROR_DIR"
    logs_dir = path / "LOGS_DIR"
    internal_csv_path = path / "INTERNAL_DIR" / f"internal.csv"
    hard_export = path / "HARD_DOMINIO_DIR" / f"hard.csv"
    error_log_audit = logs_dir / "Error_log.log"
    
    # 1. CARGAR MEMORIA DE DUPLICADOS
    # Leemos lo que ya hay en los CSV para no volver a escribirlo
    existentes_internal = obtener_claves_existentes(internal_csv_path)
    existentes_hard = obtener_claves_existentes(hard_export)

    df_internal_total = []
    df_validos_total = []

    storage = StorageManager(path)
    storage.rotar_backups(dias_maximos=5)

    for file in entrada.glob("*.csv"):
        if file.stat().st_size == 0: continue
        try:
            if not validar_integridad_archivo(file, error_dir, error_log_audit): continue 

            for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE):
                chunk.columns = chunk.columns.str.strip()
                # Creamos la 'llave de identidad' para este bloque de datos
                chunk['temp_key'] = chunk.apply(lambda x: f"{x['Email']}|{x['Message']}|{x['Date added']}", axis=1)

                # --- FILTRAR INTERNAL ---
                internal = chunk[chunk['Bounce type'] == 'Internal'].copy()
                # Solo filas que NO estén en nuestro set de memoria
                internal_nuevo = internal[~internal['temp_key'].isin(existentes_internal)]
                if not internal_nuevo.empty:
                    internal_nuevo.drop(columns=['temp_key']).to_csv(
                        internal_csv_path, mode='a', index=False, header=not internal_csv_path.exists()
                    )
                    df_internal_total.append(internal_nuevo)
                    existentes_internal.update(internal_nuevo['temp_key'])
                
                # --- FILTRAR HARD ---
                hard = chunk[chunk['Bounce type'] == 'Hard'].copy()
                hard_nuevo = hard[~hard['temp_key'].isin(existentes_hard)]
                if not hard_nuevo.empty:
                    hard_nuevo.drop(columns=['temp_key']).to_csv(
                        hard_export, mode='a', index=False, header=not hard_export.exists()
                    )
                    existentes_hard.update(hard_nuevo['temp_key'])

                    # Insertar en SQLite (Ignora si ya existe por fecha)
                    for _, row in hard_nuevo.iterrows():
                        conn.execute("INSERT OR IGNORE INTO hard_emails VALUES (?,?,?,?,?)", 
                                   (row['Email'], row['Message'], row['Date added'], file.name, datetime.now().isoformat()))

                df_validos_total.append(chunk.drop(columns=['temp_key']))

            conn.commit()
        except Exception as e:
            with open(error_log_audit, "a", encoding="utf-8") as f:
                f.write(f"ERROR CRÍTICO EN {file.name}: {str(e)}\n")
            shutil.move(str(file), str(error_dir / file.name))

    # REPORTES FINALES (Solo con los datos nuevos encontrados)
    if df_internal_total:
        generar_internal_log(pd.concat(df_internal_total), consola, logs_dir / f"Internal_Error.log")
    if df_validos_total:
        generar_log_dominios(pd.concat(df_validos_total), consola, logs_dir / f"Reporte_Dominios.log")