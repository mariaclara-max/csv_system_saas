# utils.py
import hashlib
import sys

# Esta función crea una "huella digital" del archivo
# Sirve para saber si un archivo ya fue procesado antes

def file_hash(path):

    # Creamos el generador de hash
    h = hashlib.md5()

    # Abrimos el archivo en modo lectura binaria
    with open(path, "rb") as f:

        # Leemos el archivo por partes (para archivos grandes)
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    # Devolvemos la huella única del archivo
    return h.hexdigest()

def barra_progreso(actual, total, consola='', largo=40):
    """
    Dibuja una barra de carga profesional. 
    Asegúrate de que el argumento 'consola' esté definido aquí.
    """
    progreso = int((actual / total) * largo)
    porcentaje = int((actual / total) * 100)
    barra = "█" * progreso + "-" * (largo - progreso)
    
    # Escribe la línea y usa \r para volver al inicio sin saltar de línea
    sys.stdout.write(f"\rProcesando {consola:12} |[{barra}]| {porcentaje}%")
    sys.stdout.flush()
    
    if actual == total:
        print() # Salto de línea final al terminar todas las consolas