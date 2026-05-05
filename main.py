import shutil

from config import BASE_PATH, CONSOLAS
from db import init_db
from processor import process_consola
from utils import file_hash
from logger import log


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

            op = menu()

            if op == "1":
                setup()

            elif op == "2":
                detectar_csv()

                for consola in CONSOLAS:

                    path = BASE_PATH / consola
                    db_path = path / "BBDD_DIR" / "data.db"

                    conn = init_db(db_path)

                    for f in path.glob("*.csv"):
                        shutil.move(f, path / "ENTRADA_DIR" / f.name)

                    process_consola(path, consola, conn, log)

                    for f in (path / "ENTRADA_DIR").glob("*.csv"):
                        shutil.move(f, path / "PROCESSED_DIR" / f.name)

                    conn.close()

            elif op == "3":
                break

    except KeyboardInterrupt:
        print("\n\n⚠ Programa detenido por el usuario (Ctrl+C)")

if __name__ == "__main__":
    main()