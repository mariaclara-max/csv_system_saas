# main.py 
import shutil
from config import BASE_PATH, CONSOLAS
from db import init_db
from processor import process_consola
from utils import file_hash
from logger import log
from utils import barra_progreso

def setup():

    for consola in CONSOLAS:
        base = BASE_PATH / consola

        for folder in [
            "ENTRADA_DIR","BBDD_DIR","LOGS_DIR",
            "HARD_DOMINIO_DIR","INTERNAL_DIR",
            "PROCESSED_DIR","ERROR_DIR"
        ]:
            (base / folder).mkdir(parents=True, exist_ok=True)

def detectar_csv():
    for consola in CONSOLAS:
        path = BASE_PATH / consola
        csvs = list(path.glob("*.csv"))

        if csvs:
            print(f"✔ {consola} → {len(csvs)} CSV")
        else:
            print(f"⚠ {consola} → vacío")


def menu():
    print("\n1. Crear estructura")
    print("2. Procesar CSV")
    print("3. Salir")
    return input("Opción: ")


def main():
    try:
        while True:
            print("\n1. Crear estructura\n2. Procesar CSV\n3. Salir")
            op = input("Opción: ")

            if op == "1":
                setup()
                print("✔ Estructura creada.")

            elif op == "2":
                total = len(CONSOLAS)
                print(f"\nIniciando procesamiento de {total} consolas...")
                
                for i, consola in enumerate(CONSOLAS, 1):
                    # 1. Llamamos a la barra ANTES de empezar la consola
                    barra_progreso(i, total, prefijo=f'{consola[:10]:10}', sufijo='Completado')
                    
                    path = BASE_PATH / consola
                    db_path = path / "BBDD_DIR" / "data.db"
                    
                    # Movimiento de archivos
                    for f in path.glob("*.csv"):
                        shutil.move(str(f), str(path / "ENTRADA_DIR" / f.name))

                    conn = init_db(db_path)
                    process_consola(path, consola, conn, log)
                    
                    for f in (path / "ENTRADA_DIR").glob("*.csv"):
                        shutil.move(str(f), str(path / "PROCESSED_DIR" / f.name))
                    
                    conn.close()

                print("✔ ¡Todo el trabajo ha terminado con éxito!")

            elif op == "3":
                break
    except KeyboardInterrupt:
        print("\n\n⚠ Detenido por el usuario.")


if __name__ == "__main__":
    main()