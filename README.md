DOCUMENTACIÓN TÉCNICA COMPLETA DEL SISTEMA

Sistema de procesamiento de CSV + clasificación de errores + reporting

1. DESCRIPCIÓN GENERAL

Este sistema es un pipeline automatizado para el procesamiento de archivos CSV de rebotes 

de email. Su objetivo es:


Ingesta de CSV por “consolas”


Validación estructural y sintáctica


Clasificación de errores de email (SMTP y delivery)


Separación de datos (internal / hard bounce)


Persistencia en SQLite


Detección de duplicados y blacklist


Generación de reportes analíticos


Organización automática de archivos



2. ARQUITECTURA GENERAL
   
El sistema está dividido en módulos independientes:

classifier.py

config.py

db.py

domain_logger.py

error_logger.py

internal_logger.py

blacklist_logger.py

processor.py

storage_manager.py (externo)

utils.pymain.py

4. CONFIGURACIÓN (config.py)
   
Objetivo

Define la estructura global del sistema.

Variables principales

BASE_PATH

Ruta raíz donde están las consolas.

CONSOLAS

Lista de entornos de trabajo:


OverQuota


DS


Or_1 → Or_5


Lore_1 → Lore_2


New_1 → New_2


Mistral_01 → Mistral_03



Estructura interna por consola


ENTRADA_DIR → CSV de entrada


BBDD_DIR → base de datos SQLite


LOGS_DIR → logs del sistema


HARD_DOMINIO_DIR → exportación de rebotes críticos


INTERNAL_DIR → rebotes internos


PROCESSED_DIR → archivos procesados


ERROR_DIR → archivos con errores



Parámetros técnicos


CHUNK_SIZE = 100000 → procesamiento de grandes CSV


EXPECTED_COLUMNS → validación de estructura CSV



4. CLASIFICADOR DE ERRORES (classifier.py)
   
Función principal

clasificar_error(msg)

Objetivo

Detectar y categorizar errores SMTP/email.

Categorías soportadas


QUOTA_EXCEEDED → buzón lleno


MAILBOX_NOT_FOUND → email inexistente


CONNECTION_ERROR → fallo de red


BLOCKED_OR_SPAM → filtrado spam


SMTP_ERROR → error genérico SMTP


LOW_REPUTATION_OR_IP_BLOCKED → blacklist IP/dominio


GMAIL_RATE_LIMIT → exceso de envío Gmail


ARUBA_SPECIFIC_BLOCK → bloqueo Aruba.it


UNKNOWN_ERROR → sin clasificación



Funcionamiento


Convierte mensaje a minúsculas


Busca patrones textuales


Devuelve primera coincidencia válida



5. BASE DE DATOS (db.py)
   
Función: init_db(db_path)

Objetivo

Crear y gestionar SQLite.

Tablas

hard_emails

Almacena rebotes críticos.

Campos:


email


message


date_added


file_name


processed_at


Restricción:
UNIQUE(email, message, date_added)

files_processed
Evita reprocesamiento.
Campos:


filename


filehash


processed_at



6. DOMAIN LOGGER (domain_logger.py)
Función: generar_log_dominios(df, consola, output_path)
Objetivo
Analizar dominios de email.

Funcionalidades


Extrae dominio desde email


Clasifica proveedores


Genera estadísticas


Exporta reporte estructurado



Clasificación de dominios


ITALIAONLINE_GROUP


WIND_TRE


TIM_ALICE_TIN


ARUBA_HOSTING


TISCALI


GMAIL


MICROSOFT


OTROS_DOMINIOS



Output


total emails analizados


porcentaje por proveedor


top dominios por grupo



7. ERROR LOGGER (error_logger.py)
Objetivo
Validación de archivos CSV + auditoría.

1. validar_integridad_archivo()
Regla:
bounce-stats-ID-FECHA.csv
Si falla:


mueve archivo a ERROR_DIR


escribe en audit log



2. validar_sintaxis_csv()
Valida:


columnas obligatorias


email válido (@)


Bounce type válido


fecha válida


Si falla:


registra errores detallados


mueve archivo a ERROR_DIR



3. generar_error_log()
Agrupa errores usando classifier.py y genera resumen.

8. INTERNAL LOGGER (internal_logger.py)
Función: generar_internal_log()
Objetivo
Agrupar errores internos por fecha.

Proceso


Limpieza de columnas


Normalización de fechas


Clasificación de errores


Agrupación por día



Output
CONSOLA: XFECHA CREACION CSV: XX/XX/XXXXMENSAJE: ERROR TYPENUM_TOTAL_MENSAJE: N

9. BLACKLIST LOGGER (blacklist_logger.py)
Función: write_blacklist()
Objetivo
Registrar duplicados entre ejecuciones.

Condición
Solo escribe si hay duplicados.

Contenido


nombre consola


fecha descarga


fecha CSV


lista emails duplicados


total duplicados



10. PROCESSOR (processor.py) — NÚCLEO DEL SISTEMA
Objetivo
Orquestar todo el pipeline.

Flujo general
1. BACKUP


Base de datos


logs


resultados anteriores



2. VALIDACIÓN


nombre archivo


estructura CSV


sintaxis interna



3. PROCESAMIENTO
Separación:
INTERNAL


guardado incremental


logging


HARD BOUNCE


persistencia CSV


detección duplicados


inserción SQLite



4. DETECCIÓN DE DUPLICADOS
Si:


email existe


mensaje coincide


fecha cambia


→ se añade a blacklist

5. PERSISTENCIA


commit en SQLite



6. REPORTING
Genera:


internal logs


dominios


blacklist



11. UTILIDADES (utils.py)
Función: file_hash(path)
Objetivo
Generar hash MD5 de archivo.
Uso


detectar archivos duplicados


evitar reprocesamiento



12. FLUJO COMPLETO DEL SISTEMA
CSV ENTRADA

  ↓VALIDACIÓN (nombre + estructura + sintaxis)  
  
  ↓CHUNK PROCESSING   
  
  ↓SEPARACIÓN:  
  
  ├── INTERNAL 
  
  └── HARD BOUNCE  
  
  ↓SQLite + CSV logs  
  
  ↓CLASIFICACIÓN DE ERRORES 
  
  ↓REPORTES:  
  
  ├── dominios  
  
  ├── internal logs  
  
  ├── blacklist   └── auditoría

14. PUNTOS CRÍTICOS
Problemas detectados


lógica duplicada en classifier.py


inconsistencias en rutas de base de datos


errores de scope en error_logger.py


regex desalineados en internal_logger


mezcla de responsabilidades en algunos módulos



14. FORTALEZAS DEL SISTEMA
    
✔ Procesamiento por chunks (escala grande)

✔ Arquitectura modular

✔ Persistencia en SQLite

✔ Sistema de auditoría completo

✔ Detección de duplicados inteligente

✔ Logging detallado por niveles

✔ Separación de tipos de rebote

16. CONCLUSIÓN
Este sistema implementa un pipeline completo de procesamiento de rebotes de email con:


análisis de datos a gran escala


clasificación heurística de errores


persistencia estructurada


generación de reportes avanzados


control de duplicados y auditoría


Es una arquitectura funcional tipo “ETL + Email Intelligence Engine”.

