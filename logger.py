# Esta función escribe mensajes en un archivo de log

def log(path, text):

    # Abrimos el archivo en modo "añadir"
    with open(path, "a") as f:

        # Escribimos el mensaje
        f.write(text + "\n")