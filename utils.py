import hashlib

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