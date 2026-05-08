import sqlite3

def init_db(db_path):
    """Inicializa la DB y crea la tabla única con restricción de duplicados."""
    conn = sqlite3.connect(db_path)
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
    return conn