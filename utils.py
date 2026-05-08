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

def barra_progreso(actual, total, prefijo='', sufijo='', decimales=1, largo=50, relleno='█', sin_relleno='-'):
    """
    Imprime una barra de progreso en la consola.
    """
    porcentaje = ("{0:." + str(decimales) + "f}").format(100 * (actual / float(total)))
    llenado = int(largo * actual // total)
    barra = relleno * llenado + sin_relleno * (largo - llenado)
    
    # \r vuelve al inicio de la línea sin saltar
    sys.stdout.write(f'\r{prefijo} |{barra}| {porcentaje}% {sufijo}')
    sys.stdout.flush()
    
    # Salto de línea al terminar
    if actual == total:
        print()