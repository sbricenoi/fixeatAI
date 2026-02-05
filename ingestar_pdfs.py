#!/usr/bin/env python3
"""Script para ingestar múltiples PDFs a la KB de FixeatAI.

Uso:
    python ingestar_pdfs.py archivo1.pdf archivo2.pdf ...
    python ingestar_pdfs.py ./manuales/*.pdf
    python ingestar_pdfs.py --by-page archivo1.pdf  # Procesar por páginas
"""

import base64
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests

# Intentar importar PyMuPDF para procesamiento por páginas
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️  PyMuPDF no disponible. Instalar con: pip install pymupdf")
    print("   Procesamiento por páginas deshabilitado.\n")


MCP_URL = "http://localhost:7070"


def ingestar_pdf(archivo_path: str, metadata: dict = None, original_url: str = None):
    """Ingesta un archivo PDF a la KB.
    
    Args:
        archivo_path: Ruta al archivo PDF
        metadata: Metadatos opcionales (brand, model, category, etc)
        original_url: URL original si el archivo fue descargado (para metadata correcto)
    """
    archivo = Path(archivo_path)
    
    if not archivo.exists():
        print(f"❌ Archivo no encontrado: {archivo}")
        return False
    
    # Leer y convertir a base64
    with open(archivo, "rb") as f:
        contenido_base64 = base64.b64encode(f.read()).decode()
    
    # Metadatos por defecto
    if metadata is None:
        metadata = {}
    
    # Inferir metadatos del nombre del archivo si es posible
    # Ejemplo: "SINMAG_SM520_manual.pdf"
    nombre_sin_ext = archivo.stem
    partes = nombre_sin_ext.split("_")
    
    if len(partes) >= 2 and not metadata.get("brand"):
        metadata["brand"] = partes[0]
    if len(partes) >= 2 and not metadata.get("model"):
        metadata["model"] = partes[1]
    if "manual" in nombre_sin_ext.lower() and not metadata.get("doc_type"):
        metadata["doc_type"] = "manual"
    
    # Forzar URL original si está disponible (prioridad sobre ruta local)
    if original_url:
        metadata["source"] = original_url
    else:
        metadata.setdefault("source", str(archivo))
    metadata.setdefault("language", "es")
    
    # Preparar payload
    payload = {
        "docs": [
            {
                "filename": archivo.name,
                "file_base64": contenido_base64,
                "mime_type": "application/pdf",
                "metadata": metadata
            }
        ],
        "auto_curate": True,
        "auto_learn_taxonomy": True
    }
    
    # Enviar a MCP
    print(f"📤 Ingresando: {archivo.name}...")
    try:
        response = requests.post(
            f"{MCP_URL}/tools/kb_ingest",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ingresado exitosamente:")
            print(f"   - Documentos curados: {result.get('stats', {}).get('curated', 0)}")
            print(f"   - En cuarentena: {result.get('stats', {}).get('quarantine', 0)}")
            
            # Mostrar aprendizaje de taxonomía
            if 'auto_learning' in result.get('stats', {}):
                learning = result['stats']['auto_learning']
                print(f"   - Nuevas entidades aprendidas:")
                print(f"     • Marcas: {learning.get('new_brands', 0)}")
                print(f"     • Modelos: {learning.get('new_models', 0)}")
                print(f"     • Categorías: {learning.get('new_categories', 0)}")
            
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al ingestar: {e}")
        return False


def ingestar_pdf_por_paginas(archivo_path: str, metadata: dict = None, original_url: str = None) -> bool:
    """Ingesta un PDF procesando cada página como documento separado.
    
    Args:
        archivo_path: Ruta al archivo PDF
        metadata: Metadatos base (brand, model, category, etc)
        original_url: URL original si el archivo fue descargado
    
    Returns:
        True si la ingesta fue exitosa
    """
    if not PYMUPDF_AVAILABLE:
        print("❌ PyMuPDF no está instalado. Usa: pip install pymupdf")
        return False
    
    archivo = Path(archivo_path)
    
    if not archivo.exists():
        print(f"❌ Archivo no encontrado: {archivo}")
        return False
    
    # Metadatos base
    if metadata is None:
        metadata = {}
    
    # Inferir metadatos del nombre del archivo
    nombre_sin_ext = archivo.stem
    partes = nombre_sin_ext.split("_")
    
    if len(partes) >= 2 and not metadata.get("brand"):
        metadata["brand"] = partes[0]
    if len(partes) >= 2 and not metadata.get("model"):
        metadata["model"] = partes[1]
    if "manual" in nombre_sin_ext.lower() and not metadata.get("doc_type"):
        metadata["doc_type"] = "manual"
    
    # Forzar URL original si está disponible (prioridad sobre ruta local)
    if original_url:
        metadata["source"] = original_url
    else:
        metadata.setdefault("source", str(archivo))
    metadata.setdefault("language", "es")
    
    print(f"📄 Procesando PDF por páginas: {archivo.name}...")
    
    try:
        # Abrir PDF con PyMuPDF
        doc = fitz.open(archivo_path)
        total_paginas = len(doc)
        print(f"   Total de páginas: {total_paginas}")
        
        documentos = []
        
        # Procesar cada página
        for num_pagina in range(total_paginas):
            pagina = doc[num_pagina]
            texto = pagina.get_text("text")
            
            # Saltar páginas vacías
            if not texto.strip():
                continue
            
            # Crear metadata específica de página
            metadata_pagina = metadata.copy()
            metadata_pagina["page"] = num_pagina + 1  # Páginas empiezan en 1
            metadata_pagina["total_pages"] = total_paginas
            metadata_pagina["chunk_type"] = "page"
            
            # Crear documento para esta página
            doc_id = f"{archivo.stem}_page_{num_pagina + 1}"
            
            documentos.append({
                "id": doc_id,
                "text": texto,
                "metadata": metadata_pagina
            })
        
        doc.close()
        
        print(f"   Páginas procesadas: {len(documentos)}")
        
        # Enviar documentos en lotes (para no sobrecargar el endpoint)
        BATCH_SIZE = 10
        total_ingresados = 0
        
        for i in range(0, len(documentos), BATCH_SIZE):
            batch = documentos[i:i + BATCH_SIZE]
            
            payload = {
                "docs": batch
            }
            
            response = requests.post(
                f"{MCP_URL}/tools/kb_ingest",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                total_ingresados += len(batch)
                print(f"   ✅ Lote {i//BATCH_SIZE + 1}: {len(batch)} páginas ingresadas")
            else:
                print(f"   ❌ Error en lote {i//BATCH_SIZE + 1}: {response.status_code}")
                return False
        
        print(f"✅ Ingesta completada: {total_ingresados}/{total_paginas} páginas")
        return True
        
    except Exception as e:
        print(f"❌ Error procesando PDF: {e}")
        return False


def ingestar_url(url: str):
    """Ingesta un PDF desde una URL."""
    print(f"📤 Descargando e ingresando: {url}...")
    
    payload = {
        "urls": [url],
        "auto_curate": True,
        "auto_learn_taxonomy": True
    }
    
    try:
        response = requests.post(
            f"{MCP_URL}/tools/kb_ingest",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ingresado exitosamente desde URL")
            print(f"   - Documentos: {result.get('ingested', 0)}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Uso: python ingestar_pdfs.py [--by-page] archivo1.pdf archivo2.pdf ...")
        print("     python ingestar_pdfs.py https://ejemplo.com/manual.pdf")
        print("")
        print("Opciones:")
        print("  --by-page    Procesar cada página como documento separado (requiere pymupdf)")
        print("")
        print("Ejemplos:")
        print("  python ingestar_pdfs.py manual_sinmag.pdf")
        print("  python ingestar_pdfs.py --by-page manual_sinmag.pdf")
        print("  python ingestar_pdfs.py ./manuales/*.pdf")
        print("  python ingestar_pdfs.py https://ejemplo.com/manual.pdf")
        sys.exit(1)
    
    # Verificar que MCP esté corriendo
    try:
        response = requests.get(f"{MCP_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ MCP no está respondiendo en {MCP_URL}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ No se puede conectar a MCP en {MCP_URL}")
        print(f"   Asegúrate de que el servidor esté corriendo")
        sys.exit(1)
    
    print(f"✅ MCP conectado en {MCP_URL}\n")
    
    # Detectar modo de procesamiento
    by_page = False
    args = sys.argv[1:]
    
    if "--by-page" in args:
        by_page = True
        args = [a for a in args if a != "--by-page"]
        print("📄 Modo: Procesamiento por páginas\n")
    else:
        print("📦 Modo: Documento completo\n")
    
    exitosos = 0
    fallidos = 0
    
    for item in args:
        # Determinar si es URL o archivo
        if item.startswith("http://") or item.startswith("https://"):
            if ingestar_url(item):
                exitosos += 1
            else:
                fallidos += 1
        else:
            # Expandir glob si es necesario
            archivos = list(Path(".").glob(item)) if "*" in item else [Path(item)]
            
            for archivo in archivos:
                if archivo.suffix.lower() == ".pdf":
                    # Elegir método según flag
                    if by_page:
                        if ingestar_pdf_por_paginas(str(archivo)):
                            exitosos += 1
                        else:
                            fallidos += 1
                    else:
                        if ingestar_pdf(str(archivo)):
                            exitosos += 1
                        else:
                            fallidos += 1
                else:
                    print(f"⚠️  Saltando archivo no-PDF: {archivo}")
        
        print()  # Línea en blanco entre archivos
    
    # Resumen final
    print("=" * 50)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print("=" * 50)
    
    # Mostrar estadísticas de taxonomía
    try:
        response = requests.get(f"{MCP_URL}/tools/taxonomy/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("\n📊 Taxonomía actual:")
            print(f"   - Marcas: {stats.get('brands_count', 0)}")
            print(f"   - Modelos: {stats.get('models_count', 0)}")
            print(f"   - Categorías: {stats.get('categories_count', 0)}")
            print(f"   - Total entidades: {stats.get('total_entities', 0)}")
    except:
        pass


if __name__ == "__main__":
    main()


