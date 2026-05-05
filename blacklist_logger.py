# csv_system/blacklist_logger.py
from datetime import datetime


def write_blacklist(path, consola, dup_list, fecha_csv="N/A"):
    """
    Escribe un bloque en la blacklist solo si hay duplicados detectados.
    dup_list: lista de tuplas o strings con los emails duplicados.
    """
    if not dup_list:
        return # No escribimos nada si no hubo duplicados en este proceso

    fecha_descarga = datetime.now().strftime("%d/%m/%Y")

    with open(path, "a", encoding="utf-8") as f:
        f.write("\n# ==========================================\n")
        f.write(f"NOMBRE_CONSOLA: {consola}\n")
        f.write(f"FECHA DESCARGA: {fecha_descarga}\n")
        f.write(f"FECHA CREACION CSV: {fecha_csv}\n")
        f.write("# ==========================================\n")
        f.write("             BLACKLIST - DUPLICADOS         \n")
        f.write("# ==========================================\n")

        for email in dup_list:
            f.write(f"{email}\n")
        
        f.write(f"# TOTAL DUPLICADOS DETECTADOS: {len(dup_list)}\n")
