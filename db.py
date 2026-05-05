# db.py
import sqlite3
from datetime import datetime

# Esta función crea o abre la base de datos
def init_db(db_path):

    # Conectamos con la base de datos
    conn = sqlite3.connect(db_path)

    # Creamos tabla para emails "hard bounce" (errores graves)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hard_emails (
        email TEXT,
        message TEXT,
        date_added TEXT,
        file_name TEXT,
        processed_at TEXT,
        UNIQUE(email, message, date_added)
    )
    """)

    # Tabla que guarda qué archivos ya fueron procesados
    conn.execute("""
    CREATE TABLE IF NOT EXISTS files_processed (
        filename TEXT,
        filehash TEXT UNIQUE,
        processed_at TEXT
    )
    """)

    return conn