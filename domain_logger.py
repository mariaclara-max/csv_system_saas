# domain_logger.py

import pandas as pd
import os

def generar_log_dominios(df, consola, output_path):
    # Si el archivo está vacío, no hacemos nada para evitar errores
    if df.empty:
        return

    # Trabajamos con una copia para no alterar los datos originales
    df = df.copy()
    
    # --- EXTRACCIÓN DEL DOMINIO ---
    df['dominio'] = df['Email'].str.split('@').str[1].str.lower().str.strip()

    # --- ESCRITURA DEL GLOSARIO (Solo si el archivo es nuevo o está vacío) ---
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("============================================================\n")
            f.write("          GLOSARIO DE PROVEEDORES Y DOMINIOS\n")
            f.write("============================================================\n")
            f.write("• ITALIAONLINE_GROUP: Incluye Libero, Virgilio, IOL, Blu y Giallo.\n")
            f.write("• TIM_ALICE_TIN: Dominios del grupo Telecom Italia (Alice, Tim, Tin).\n")
            f.write("• WIND_TRE: Dominios de la red Wind e Inwind.\n")
            f.write("• ARUBA_HOSTING: Correos gestionados por la infraestructura de Aruba.it.\n")
            f.write("• TISCALI: Incluye Tiscali.it y Tiscalinet.it.\n")
            f.write("• MICROSOFT: Cuentas de Outlook, Hotmail, Live y MSN.\n")
            f.write("• GMAIL: Cuentas personales de Google y Googlemail.\n")
            f.write("• POSTE_ITALIANE: Cuentas de correos de servicios postales italianos.\n")
            f.write("• OTROS_DOMINIOS: Dominios corporativos o proveedores minoritarios.\n")
            f.write("============================================================\n\n")
    
    # --- LA FUNCIÓN "CLASIFICADORA" ---
    def agrupar_dominios(dom):
        if not dom: return "DESCONOCIDO"
        if any(x in dom for x in ['libero.it', 'virgilio.it', 'giallo.it', 'blu.it', 'iol.it']):
            return 'ITALIAONLINE_GROUP'
        if any(x in dom for x in ['wind.it', 'inwind.it']):
            return 'WIND_TRE'
        if 'tiscali' in dom:
            return 'TISCALI'
        if any(x in dom for x in ['alice.it', 'aliceposta.it', 'tim.it', 'tin.it']):
            return 'TIM_ALICE_TIN'
        if 'aruba.it' in dom or 'technet.it' in dom:
            return 'ARUBA_HOSTING'
        if 'teletu.it' in dom:
            return 'TELETU_VODAFONE'
        if 'postecert.it' in dom or 'poste.it' in dom:
            return 'POSTE_ITALIANE'
        if any(x in dom for x in ['gmail', 'googlemail']): return 'GMAIL'
        if any(x in dom for x in ['outlook', 'hotmail', 'live', 'msn']): return 'MICROSOFT'
        return 'OTROS_DOMINIOS'

    df['categoria_dominio'] = df['dominio'].apply(agrupar_dominios)

    # --- CÁLCULOS PARA EL REPORTE ---
    conteo = df['categoria_dominio'].value_counts()
    total_emails = len(df)
    
    # --- ESCRITURA DEL ARCHIVO (Modo "a" para no borrar el glosario) ---
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("==========================================\n")
        f.write(f"REPORTE POR DOMINIO - {consola}\n")
        f.write("==========================================\n")
        f.write(f"Total registros analizados: {total_emails}\n")
        f.write("------------------------------------------\n\n")

        for cat, total in conteo.items():
            porcentaje = (total / total_emails) * 100
            f.write(f"PROVEEDOR: {cat}\n")
            f.write(f"REBOTES: {total} ({porcentaje:.2f}%)\n")
            f.write("  Top dominios reales en este grupo:\n")
            top_reales = df[df['categoria_dominio'] == cat]['dominio'].value_counts().head(3)
            for d_real, t_real in top_reales.items():
                f.write(f"  - {d_real}: {t_real}\n")
            f.write("-" * 30 + "\n")
        f.write("\n") # Espacio extra al final de cada reporte