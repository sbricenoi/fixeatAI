#!/usr/bin/env python3
"""
Script de ingesta via API del MCP
Ingesta directamente a ChromaDB dentro del contenedor Docker
"""

import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# URLs de los PDFs a procesar
URLS = [
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.195_iCombi_Pro-iCombi_Classic_IFA_CD_IM_Vxx_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.196_iCombi_Pro-iCombi_Classic_IFA_CD_IM_Vxx_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.575_iCombi_Pro-iCombi_Classic_UV_XS_IM_VXX_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.574_iCombi_Pro-iCombi_Classic_UV_XS_IM_VXX_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.571_iCombi_Pro-iCombi_Classic_UV_P_IM_V01_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.570_iCombi_Pro-iCombi_Classic_UV_P_IM_V01_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.558_iCombi_Pro-iCombi_Classic_Adapterkit_UV_IM_V02.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.504_iCombiPro-iCombiClassic_ExtensionHat_UV-UVP_IM.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.501_iCombiPro-iCombiClassic_HS_IM_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.500_iCombiPro-iCombiClassic_HS_IM_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.395_iCombi_Pro-iCombi_Classic_UV_IM_V01_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.394_iCombi_Pro-iCombi_Classic_UV_IM_V01_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.390_iCombi_Pro-iCombi_Classic_DAH_IM_V01_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.387_iCombi_Pro-iCombi_Classic_IFA_TG_IM_V01_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.386_iCombi_Pro-iCombi_Classic_IFA_TG_IM_V01_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.383_iCombi_Pro-iCombi_Classic_IFA_SG_IM_V01_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.382_iCombi_Pro-iCombi_Classic_IFA_SG_IM_V01_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.379_iCombi_Pro-iCombi_Classic_CD_U_IM_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.378_iCombi_Pro-iCombi_Classic_CD_U_IM_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.375_iCombi_Pro-iCombi_Classic_CD_G_IM_EU-Ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.374_iCombi_Pro-iCombi_Classic_CD_G_IM_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.372_iCombi_Pro-iCombi_Classic_CD_E_IM_Asien.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.371_iCombi_Pro-iCombi_Classic_CD_E_IM_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.370_iCombi_Pro-iCombi_Classic_CD_E_IM_EU-west.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.332_ET_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.282_iCombi_TM_v04_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.199_iCombi_Pro-iCombi_Classic_CD_E_LA_V01.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2516_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2515_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2514_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2511_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2510_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2509_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2508_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2506_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2505_en-GB.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2502_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2412_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2411_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2410_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2409_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2408_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2406_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2401_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2324_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TI_2322_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TechnicalReleaseNote_LM200_iCombiClassic_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/TechnicalReleaseNote_LM100_iCombiPro_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2510_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2506_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2505_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2503_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2431_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2318_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2317_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2316_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2315_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2314_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/MI_2312_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.52.052_iCombiPro-iCombiClassic_CD-E_Komp_IM_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.954_iCombiPro-iCombiClassic_FloorTrayMarine_IM.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.936_iCombiPro-iCombiClassic_UV-P-CD-Komp_IM_EU.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.933_iCombiPro-iCombiClassic_DT-CDG_IM.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.907_iCombi_Pro-iCombi_Classic_Adapterkit_UG1_IM.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.906_iCombi_Pro-iCombi_Classic_BlindCover_CD_IM_V01.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.905_iCombi_Pro-iCombi_Classic_MFU_CD_IM.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.887_ServiceReferenz_iCombiClassic_Q_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.874_ServiceReferenz_iCombiPro_Q_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.861_ServiceReferenz_iCombiProiCombiClassic_Gas_Q_es-ES.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.802_iCombi_Pro-iCombi_Classic_TableModification_IM_V01.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.598_iCombiPro-iCombiClassic_IntegrationKit_IM_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.597_iCombiPro-iCombiClassic_IntegrationKit_IM_EU-west.pdf"
]

# Eliminar duplicados
URLS = list(dict.fromkeys(URLS))

MCP_URL = "http://localhost:7070"

def ingestar_pdf_via_api(url, index, total):
    """Ingesta un PDF via API del MCP"""
    filename = url.split("/")[-1]
    print(f"[{index}/{total}] 📄 Ingestionando: {filename}")
    
    try:
        response = requests.post(
            f"{MCP_URL}/tools/kb_ingest",
            json={
                "urls": [url],
                "auto_curate": True,
                "auto_learn_taxonomy": True
            },
            timeout=300  # 5 minutos por PDF
        )
        
        if response.status_code == 200:
            result = response.json()
            ingested = result.get("ingested", 0)
            if ingested > 0:
                print(f"[{index}/{total}] ✅ Éxito: {filename} ({ingested} chunks)")
                return {"status": "success", "url": url, "filename": filename, "chunks": ingested}
            else:
                print(f"[{index}/{total}] ⚠️  Advertencia: {filename} (0 chunks)")
                return {"status": "warning", "url": url, "filename": filename}
        else:
            print(f"[{index}/{total}] ❌ Error HTTP {response.status_code}: {filename}")
            return {"status": "failed", "url": url, "filename": filename}
    
    except Exception as e:
        print(f"[{index}/{total}] ❌ Excepción: {filename} - {str(e)[:100]}")
        return {"status": "failed", "url": url, "filename": filename}

def main():
    """Procesa todos los PDFs"""
    
    print("=" * 80)
    print("🚀 INGESTA VIA API DEL MCP")
    print("=" * 80)
    print(f"📊 Total de PDFs: {len(URLS)}")
    print(f"🔗 MCP URL: {MCP_URL}")
    print(f"⏱️  Tiempo estimado: {len(URLS) * 2} - {len(URLS) * 3} minutos")
    print("=" * 80)
    print()
    
    start_time = time.time()
    exitosos = 0
    advertencias = 0
    fallidos = 0
    total_chunks = 0
    
    # Procesar uno por uno para evitar sobrecarga
    for i, url in enumerate(URLS, 1):
        result = ingestar_pdf_via_api(url, i, len(URLS))
        
        if result["status"] == "success":
            exitosos += 1
            total_chunks += result.get("chunks", 0)
        elif result["status"] == "warning":
            advertencias += 1
        else:
            fallidos += 1
        
        # Checkpoint cada 10 PDFs
        if i % 10 == 0:
            elapsed = time.time() - start_time
            print("\n" + "=" * 80)
            print(f"📊 PROGRESO: {i}/{len(URLS)} PDFs")
            print(f"✅ Exitosos: {exitosos}")
            print(f"⚠️  Advertencias: {advertencias}")
            print(f"❌ Fallidos: {fallidos}")
            print(f"📦 Chunks totales: {total_chunks}")
            print(f"⏱️  Tiempo: {elapsed/60:.1f} min")
            if i > 0:
                eta = (elapsed / i) * (len(URLS) - i)
                print(f"⏰ ETA: {eta/60:.1f} min")
            print("=" * 80)
        
        # Pequeño delay para no saturar
        time.sleep(1)
    
    # Resumen final
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("🏁 INGESTA COMPLETADA")
    print("=" * 80)
    print(f"✅ Exitosos: {exitosos}/{len(URLS)}")
    print(f"⚠️  Advertencias: {advertencias}/{len(URLS)}")
    print(f"❌ Fallidos: {fallidos}/{len(URLS)}")
    print(f"📦 Chunks totales ingresados: {total_chunks}")
    print(f"⏱️  Tiempo total: {elapsed/60:.1f} minutos")
    print("=" * 80)
    
    return 0 if fallidos == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
