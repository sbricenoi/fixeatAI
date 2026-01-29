#!/usr/bin/env python3
"""Script para ingestar múltiples PDFs desde URLs con procesamiento por páginas."""

import sys
sys.path.insert(0, '/Users/sbriceno/Documents/projects/fixeatAI')

import tempfile
from pathlib import Path
import requests
import time
import ingestar_pdfs

# URLs de los PDFs a ingestar
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
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.802_iCombi_Pro-iCombi_Classic_TableModification_IM_V01.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.598_iCombiPro-iCombiClassic_IntegrationKit_IM_EU-ost.pdf",
    "https://desa-aibo-wp.s3.us-east-1.amazonaws.com/test/80.51.597_iCombiPro-iCombiClassic_IntegrationKit_IM_EU-west.pdf"
]

def main():
    print("=" * 80)
    print("🚀 Ingesta Masiva de PDFs con Procesamiento por Páginas")
    print("=" * 80)
    print(f"\n📊 Total de URLs: {len(URLS)}")
    print("⏱️  Tiempo estimado: ~1-2 minutos por PDF\n")
    
    exitosos = 0
    fallidos = 0
    total_paginas = 0
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        for i, url in enumerate(URLS, 1):
            filename = url.split("/")[-1]
            print(f"\n[{i}/{len(URLS)}] 📥 {filename}")
            local_path = tmpdir_path / filename
            
            try:
                # Descargar con retry
                print(f"   Descargando...")
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.get(url, timeout=60)
                        response.raise_for_status()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            wait_time = 5 * (attempt + 1)
                            print(f"   ⚠️  Reintentando en {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            raise
                
                local_path.write_bytes(response.content)
                
                # Ingestar con URL original
                print(f"   Procesando por páginas...")
                if ingestar_pdfs.ingestar_pdf_por_paginas(
                    str(local_path),
                    metadata=None,
                    original_url=url
                ):
                    exitosos += 1
                    print(f"   ✅ Completado")
                else:
                    fallidos += 1
                    print(f"   ❌ Error al procesar")
                
                # Delay entre PDFs para evitar rate limiting
                if i < len(URLS):
                    time.sleep(2)
                    
            except Exception as e:
                fallidos += 1
                print(f"   ❌ Error: {str(e)[:150]}")
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Exitosos: {exitosos}/{len(URLS)}")
    print(f"❌ Fallidos: {fallidos}/{len(URLS)}")
    print("=" * 80)

if __name__ == "__main__":
    main()

