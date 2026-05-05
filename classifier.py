# Esta función analiza un mensaje de error y lo clasifica
# classifier.py
def clasificar_error(msg):
    # Convertimos el texto a minúsculas para evitar errores de comparación
    msg = str(msg).lower()

    # Si el correo está lleno o sin espacio
    if any(x in msg for x in ["quota exceeded", "mailbox full", "over quota"]):
        return "QUOTA_EXCEEDED"

    # Si el correo no existe
    elif any(x in msg for x in ["user unknown", "no such user", "mailbox unavailable"]):
        return "MAILBOX_NOT_FOUND"

    # Código típico de error de correo no encontrado
    elif "550" in msg:
        return "MAILBOX_NOT_FOUND"

    # Problemas de conexión a internet o servidor
    elif any(x in msg for x in ["timeout", "connection", "refused", "network"]):
        return "CONNECTION_ERROR"

    # Correos bloqueados o marcados como spam
    elif any(x in msg for x in ["blocked", "spam", "rejected", "5.7"]):
        return "BLOCKED_OR_SPAM"

    # Error genérico de servidor de correo
    elif "smtp" in msg:
        return "SMTP_ERROR"
#Nuevos errores detectados en los últimos meses, especialmente con Gmail y algunos proveedores italianos
# 1. IP / DOMAIN REPUTATION (NUEVO - CRÍTICO)
    # Detecta bloqueos por listas negras (Cloudmark, Aruba, etc.)
    if any(x in msg for x in ["cloudmark", "reputation", "unsolicited mail", "blocked", "35.205.6.117"]):
        return "LOW_REPUTATION_OR_IP_BLOCKED"

    # 2. GMAIL SPECIFIC (NUEVO)
    # Gmail es muy estricto con el volumen
    if "gmail has detected an unusual rate" in msg:
        return "GMAIL_RATE_LIMIT"

    # 3. QUOTA EXCEEDED (Mantenemos y ampliamos)
    if any(x in msg for x in ["quota exceeded", "mailbox full", "over quota", "452", "space"]):
        return "QUOTA_EXCEEDED"

    # 4. MAILBOX NOT FOUND (Mantenemos)
    if any(x in msg for x in ["user unknown", "no such user", "mailbox unavailable", "550", "frozen", "recipient rejected"]):
        return "MAILBOX_NOT_FOUND"

    # 5. CONNECTION / TIMEOUT (Ampliamos con errores de Host)
    if any(x in msg for x in ["timeout", "connection refused", "network", "suspended", "lost", "connect to host"]):
        return "CONNECTION_ERROR"

    # 6. ARUBA / ITALIA SPECIFIC (NUEVO)
    # Tienes muchos errores específicos de pepi1mx-mfe...
    if "aruba.it" in msg and "bizsmtp" in msg:
        return "ARUBA_SPECIFIC_BLOCK"

    # 7. SPAM FILTERS GENERAL
    if any(x in msg for x in ["spam", "rejected", "5.7.1", "content denied"]):
        return "SPAM_FILTER_REJECTION"

    return "UNKNOWN_ERROR"