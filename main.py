import shutil
import os
from config import BASE_PATH, CONSOLAS
from db import init_db
from processor import process_consola
from logger import log
from utils import barra_progreso

def setup():
    """Crea la estructura de carpetas para las consolas activas."""
    print("\n--- Configurando Directorios ---")
    for consola in CONSOLAS:
        base = BASE_PATH / consola
        folders = ["ENTRADA_DIR","BBDD_DIR","LOGS_DIR","HARD_DOMINIO_DIR",
                   "INTERNAL_DIR","PROCESSED_DIR","ERROR_DIR","BACKUPS_DIR","ARCHIVE_HISTORIC"]
        for folder in folders:
            (base / folder).mkdir(parents=True, exist_ok=True)
    print("✔ Estructura de carpetas actualizada.")

def main():
    try:
        while True:
        # Interfaz visual del menú principal
            print("\n" + "="*25)
            print("      PANEL DE CONTROL")
            print("="*25)
            print(" [1] Crear estructura de carpetas")
            print(" [2] Procesar CSVs")
            print(" [3] Salir")
            print("-" * 25)

            op = input("Seleccione una opción: ")

            if op == "1":
                setup()

            elif op == "2":
                total_c = len(CONSOLAS)
                if total_c == 0:
                    print("⚠ Error: No hay consolas en config.py")
                    continue

                print(f"\n🚀 Iniciando análisis de registros...")
                
                for i, consola in enumerate(CONSOLAS, 1):
                    # Aquí es donde daba el error: ahora utils.py ya acepta 'consola'
                    barra_progreso(i, total_c, consola=consola)
                    
                    path = BASE_PATH / consola
                    db_path = path / "BBDD_DIR" / "data.db"
                    
                    # Mover archivos de la raíz a ENTRADA antes de procesar
                    for f in path.glob("*.csv"):
                        shutil.move(str(f), str(path / "ENTRADA_DIR" / f.name))

                    conn = init_db(db_path)
                    process_consola(path, consola, conn, log)
                    
                    # Mover a PROCESSED tras terminar
                    for f in (path / "ENTRADA_DIR").glob("*.csv"):
                        shutil.move(str(f), str(path / "PROCESSED_DIR" / f.name))
                    
                    conn.close()
                
                print(f"\n\n✔ ¡Proceso completado con éxito!")

            elif op == "3":
                print("\nSaliendo... ¡Buen día!")
                break
            else:
                print("\n⚠ Opción no válida.")

    except KeyboardInterrupt:
        print("\n\n⚠ Programa detenido manualmente.")

if __name__ == "__main__":
    main()