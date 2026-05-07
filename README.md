Documentación Técnica: Sistema de Gestión de Consolas SaaS

Este sistema está diseñado para automatizar el procesamiento, clasificación y auditoría 

de reportes de rebotes de correo electrónico (CSV), organizando la información por 

"consolas" (clientes o proyectos) y manteniendo una base de datos histórica para detectar 

recurrencias.

🏗️ 1. Arquitectura de Archivos (Estructura de Carpetas)

El sistema utiliza una estructura jerárquica basada en una ruta raíz (BASE_PATH). Por 

cada consola en config.py, se crean las siguientes subcarpetas:

ENTRADA_DIR: Punto de recepción de archivos CSV nuevos.

PROCESSED_DIR: Histórico de archivos procesados con éxito.

ERROR_DIR: Archivos que fallaron las reglas de integridad o sintaxis.

BBDD_DIR: Almacena la base de datos SQLite (data.db).

LOGS_DIR: Reportes de errores, auditoría, dominios y blacklist.

INTERNAL_DIR: Almacena el archivo internal.csv con rebotes de tipo interno.

HARD_DOMINIO_DIR: Almacena el archivo hard.csv con rebotes permanentes.

BACKUPS_DIR: Copias de seguridad automáticas de la DB y resultados.

⚙️ 2. Módulos del Sistema

📂 config.py (Configuración Global)

Define las constantes del sistema:

BASE_PATH: Ruta absoluta de trabajo.

CONSOLAS: Lista de nombres de las carpetas de proyectos (ej. "OverQuota", "Mistral_01").

CHUNK_SIZE: 100,000 líneas (optimización de memoria para archivos grandes).

EXPECTED_COLUMNS: Columnas requeridas (Email, Bounce type, Message, Date added).

🧠 classifier.py (Motor de Clasificación)

Contiene la función clasificar_error(msg). Utiliza lógica de coincidencia de palabras

clave para categorizar los errores de SMTP.

Categorías principales:
QUOTA_EXCEEDED,

MAILBOX_NOT_FOUND, 

CONNECTION_ERROR, 

GMAIL_RATE_LIMIT,

LOW_REPUTATION_OR_IP_BLOCKED (específico para IPs bloqueadas y Cloudmark), 

y ARUBA_SPECIFIC_BLOCK.

🗄️ db.py (Gestión de Persistencia)

Gestiona la base de datos SQLite:

Tabla hard_emails: Almacena el email, el mensaje de error y la fecha. Tiene una 

restricción UNIQUE para evitar duplicidad exacta de registros.

Tabla files_processed: Registra el hash de los archivos procesados para evitar re-

procesamiento.

🔍 error_logger.py (Auditoría e Integridad)


Es el filtro de calidad antes de procesar los datos:

Validación de Nombre: El archivo debe seguir el patrón bounce-stats-ID-YYYY-MM-DD-HH-MM-

SS.csv.

Validación de Sintaxis: Comprueba que las columnas existan, los emails tengan @, el tipo 

de rebote sea válido y las fechas no estén corruptas.

Generación de Log: Si hay errores, mueve el archivo a ERROR_DIR y escribe el motivo 

detallado en Error_log.log.

📈 domain_logger.py (Reporte de Proveedores)

Agrupa los rebotes por proveedor (Gmail, Microsoft, Aruba, ItaliaOnline, etc.) basándose 

en el dominio del email. Genera un glosario y estadísticas porcentuales para identificar 

si un bloqueo es generalizado en un proveedor específico.

📝 internal_logger.py (Reporte de Errores Internos)

Agrupa y contabiliza los errores de tipo 'Internal' por fecha de creación del CSV. 

Incluye un glosario de categorías para facilitar la lectura del reporte final.

🚫 blacklist_logger.py (Detección de Recurrencias)

Escribe en blacklist.log aquellos emails que aparecen como Hard Bounce en fechas 

distintas. Esto permite identificar correos que deben ser eliminados definitivamente de 

las listas de envío.

💾 storage_manager.py (Mantenimiento de Almacenamiento)

Encargado de la higiene del sistema:

Rotación: Elimina backups con más de X días de antigüedad.

Compresión: Comprime logs antiguos en archivos .zip mensualmente.

Archivado: Mueve archivos procesados a carpetas históricas organizadas por mes.

🚀 3. Flujo de Ejecución (main.py y processor.py)

Inicio: El usuario elige entre "Crear estructura" (Setup) o "Procesar CSV".

Preparación: El sistema mueve los CSV detectados en la raíz de cada consola a su 

respectiva carpeta ENTRADA_DIR.

Backup: Se realiza una copia de seguridad de la base de datos y archivos CSV actuales 

antes de cualquier cambio.

Auditoría: Se valida el nombre y la estructura de cada CSV.

Procesamiento por Chunks:

Los rebotes Internal se añaden a internal.csv.

Los rebotes Hard se comparan con la DB:

Si el email + mensaje ya existen pero con fecha distinta, se marca para la Blacklist.

Si no existen, se insertan como nuevos registros.

Finalización: Se generan los reportes de dominios, errores internos y blacklist. Los 

archivos procesados se mueven a la carpeta de salida definitiva.

🛠️ 4. Funciones de Utilidad (utils.py / logger.py)

file_hash(path): Genera un hash MD5 único por archivo para control de integridad.

log(path, text): Función genérica de escritura para seguimiento de procesos en tiempo 

real.
