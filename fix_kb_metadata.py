#!/usr/bin/env python3
"""Script para agregar metadata faltante a documentos existentes en KB.

Este script actualiza documentos que fueron ingresados sin metadata completo,
agregando información de fuente y mejorando las URLs navegables.

Uso:
    python fix_kb_metadata.py --dry-run  # Ver qué se actualizaría
    python fix_kb_metadata.py --apply    # Aplicar cambios
"""

import argparse
import sys
from typing import Any, Dict, List
import chromadb
import os
import re


def analyze_kb_metadata(collection: chromadb.Collection) -> Dict[str, Any]:
    """Analiza el estado actual de metadata en la KB.
    
    Returns:
        Diccionario con estadísticas de metadata
    """
    total = collection.count()
    
    # Obtener muestra representativa
    sample_size = min(1000, total)
    results = collection.get(limit=sample_size, include=["metadatas"])
    
    stats = {
        "total_docs": total,
        "analyzed_docs": len(results["ids"]),
        "with_page": 0,
        "with_source": 0,
        "with_brand": 0,
        "with_model": 0,
        "sources": {},  # Counter de fuentes
        "missing_metadata": [],
    }
    
    for i, doc_id in enumerate(results["ids"]):
        meta = results["metadatas"][i]
        
        # Contar metadata presente
        if meta.get("page"):
            stats["with_page"] += 1
        if meta.get("source"):
            stats["with_source"] += 1
            source = meta["source"]
            stats["sources"][source] = stats["sources"].get(source, 0) + 1
        if meta.get("brand"):
            stats["with_brand"] += 1
        if meta.get("model"):
            stats["with_model"] += 1
        
        # Documentos sin metadata crítico
        if not meta.get("page") and not meta.get("source"):
            stats["missing_metadata"].append(doc_id)
    
    return stats


def extract_source_from_doc_id(doc_id: str) -> tuple[str | None, int | None]:
    """Extrae información de fuente desde el doc_id.
    
    Ejemplos:
    - "https://example.com/manual.pdf#c5" → ("https://example.com/manual.pdf", None)
    - "manual_rational_page_12" → ("manual_rational.pdf", 12)
    - "default_services_xxx" → ("default.services", None)
    
    Returns:
        Tupla de (source, page)
    """
    # Caso 1: URL en doc_id
    if doc_id.startswith(("http://", "https://", "s3://")):
        if "#c" in doc_id:
            base_url = doc_id.split("#c")[0]
            return (base_url, None)
        return (doc_id, None)
    
    # Caso 2: Formato "archivo_page_N"
    page_match = re.search(r'_page_(\d+)', doc_id)
    if page_match:
        page_num = int(page_match.group(1))
        # Extraer nombre base del archivo
        base_name = doc_id.split("_page_")[0]
        source_file = f"{base_name}.pdf"
        return (source_file, page_num)
    
    # Caso 3: Formato "default_tipo_uuid"
    if doc_id.startswith("default_"):
        parts = doc_id.split("_")
        if len(parts) >= 2:
            source_type = parts[1]  # "services", "activities", etc.
            return (f"default.{source_type}", None)
    
    return (None, None)


def enrich_document_metadata(
    doc_id: str, 
    current_meta: Dict[str, Any]
) -> Dict[str, Any]:
    """Enriquece metadata de un documento.
    
    Args:
        doc_id: ID del documento
        current_meta: Metadata actual
        
    Returns:
        Metadata enriquecido (solo con campos nuevos/modificados)
    """
    enriched = {}
    
    # Si ya tiene source y page, no hacer nada
    if current_meta.get("source") and current_meta.get("page"):
        return enriched
    
    # Extraer información del doc_id
    inferred_source, inferred_page = extract_source_from_doc_id(doc_id)
    
    # Agregar source si no existe
    if not current_meta.get("source") and inferred_source:
        enriched["source"] = inferred_source
    
    # Agregar page si no existe
    if not current_meta.get("page") and inferred_page:
        enriched["page"] = inferred_page
    
    # Agregar source_file (nombre del archivo) si es extraíble
    if not current_meta.get("source_file"):
        if inferred_source and not inferred_source.startswith(("http", "default.")):
            enriched["source_file"] = inferred_source
        elif doc_id.startswith(("http://", "https://", "s3://")):
            # Extraer nombre del archivo de la URL
            if "#c" in doc_id:
                url_base = doc_id.split("#c")[0]
            else:
                url_base = doc_id
            filename = url_base.split("/")[-1]
            if filename:
                enriched["source_file"] = filename
    
    # Agregar metadata descriptivo para sources "default.*"
    if inferred_source and inferred_source.startswith("default."):
        source_type = inferred_source.split(".")[-1]
        enriched["source_type"] = source_type
        enriched["source_category"] = "imported_data"
    
    return enriched


def update_kb_metadata(
    collection: chromadb.Collection,
    batch_size: int = 100,
    dry_run: bool = True
) -> Dict[str, int]:
    """Actualiza metadata de documentos en la KB.
    
    Args:
        collection: Colección de ChromaDB
        batch_size: Tamaño de lote para procesar
        dry_run: Si True, solo muestra qué se actualizaría sin aplicar cambios
        
    Returns:
        Estadísticas de actualización
    """
    total_docs = collection.count()
    print(f"📊 Total documentos en KB: {total_docs:,}")
    
    stats = {
        "processed": 0,
        "enriched": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    # Procesar en lotes
    offset = 0
    
    while offset < total_docs:
        print(f"\n🔄 Procesando lote {offset//batch_size + 1} (offset: {offset})...")
        
        try:
            # Obtener lote de documentos
            results = collection.get(
                limit=batch_size,
                offset=offset,
                include=["metadatas"]
            )
            
            if not results["ids"]:
                break
            
            # Procesar cada documento
            updates_to_apply = []
            
            for i, doc_id in enumerate(results["ids"]):
                current_meta = results["metadatas"][i] or {}
                
                # Enriquecer metadata
                enriched_meta = enrich_document_metadata(doc_id, current_meta)
                
                stats["processed"] += 1
                
                if enriched_meta:
                    # Merge con metadata existente
                    updated_meta = {**current_meta, **enriched_meta}
                    
                    if dry_run:
                        print(f"  ✏️  {doc_id[:70]}")
                        print(f"     Agregar: {enriched_meta}")
                    else:
                        updates_to_apply.append((doc_id, updated_meta))
                    
                    stats["enriched"] += 1
                else:
                    stats["skipped"] += 1
            
            # Aplicar updates si no es dry-run
            if not dry_run and updates_to_apply:
                for doc_id, updated_meta in updates_to_apply:
                    try:
                        collection.update(
                            ids=[doc_id],
                            metadatas=[updated_meta]
                        )
                    except Exception as e:
                        print(f"  ❌ Error actualizando {doc_id}: {e}")
                        stats["errors"] += 1
                
                print(f"  ✅ Actualizados {len(updates_to_apply)} documentos en este lote")
            
            offset += batch_size
            
        except Exception as e:
            print(f"❌ Error procesando lote: {e}")
            stats["errors"] += batch_size
            offset += batch_size
            continue
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Actualizar metadata faltante en KB"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplicar cambios (por defecto solo muestra qué se haría)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Solo mostrar cambios sin aplicarlos (default)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Tamaño de lote para procesar (default: 100)"
    )
    parser.add_argument(
        "--chroma-path",
        type=str,
        default=None,
        help="Path a ChromaDB (default: CHROMA_PATH env o /data/chroma)"
    )
    
    args = parser.parse_args()
    
    # Determinar si es dry-run
    dry_run = not args.apply
    
    print("=" * 80)
    print("🔧 FIX KB METADATA - FIXEAT AI")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 Modo: DRY RUN (solo análisis, sin cambios)")
        print("   Para aplicar cambios, ejecuta con: --apply")
    else:
        print("⚠️  Modo: APLICAR CAMBIOS")
        response = input("¿Estás seguro? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelado por el usuario")
            sys.exit(0)
    
    print()
    
    # Conectar a ChromaDB
    chroma_path = args.chroma_path or os.getenv("CHROMA_PATH", "/data/chroma")
    print(f"📂 Conectando a ChromaDB: {chroma_path}")
    
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_or_create_collection("kb_tech")
        print(f"✅ Conectado a colección 'kb_tech'")
    except Exception as e:
        print(f"❌ Error conectando a ChromaDB: {e}")
        sys.exit(1)
    
    print()
    
    # Análisis de metadata actual
    print("📊 Analizando metadata actual...")
    stats = analyze_kb_metadata(collection)
    
    print()
    print("=" * 80)
    print("📊 ANÁLISIS DE METADATA")
    print("=" * 80)
    print(f"Total documentos: {stats['total_docs']:,}")
    print(f"Analizados: {stats['analyzed_docs']:,}")
    print()
    print(f"Con página:  {stats['with_page']:,} ({stats['with_page']/stats['analyzed_docs']*100:.1f}%)")
    print(f"Con source:  {stats['with_source']:,} ({stats['with_source']/stats['analyzed_docs']*100:.1f}%)")
    print(f"Con brand:   {stats['with_brand']:,} ({stats['with_brand']/stats['analyzed_docs']*100:.1f}%)")
    print(f"Con model:   {stats['with_model']:,} ({stats['with_model']/stats['analyzed_docs']*100:.1f}%)")
    print()
    print("Fuentes encontradas:")
    for source, count in sorted(stats['sources'].items(), key=lambda x: -x[1])[:10]:
        print(f"  • {source}: {count:,} docs")
    print()
    
    # Actualizar metadata
    print("=" * 80)
    print("🔧 ACTUALIZANDO METADATA")
    print("=" * 80)
    print()
    
    update_stats = update_kb_metadata(
        collection=collection,
        batch_size=args.batch_size,
        dry_run=dry_run
    )
    
    print()
    print("=" * 80)
    print("✅ RESUMEN")
    print("=" * 80)
    print(f"Documentos procesados: {update_stats['processed']:,}")
    print(f"Documentos enriquecidos: {update_stats['enriched']:,}")
    print(f"Documentos sin cambios: {update_stats['skipped']:,}")
    print(f"Errores: {update_stats['errors']:,}")
    print()
    
    if dry_run:
        print("🔍 Este fue un DRY RUN. Para aplicar cambios ejecuta:")
        print("   python fix_kb_metadata.py --apply")
    else:
        print("✅ Metadata actualizado exitosamente!")
        print()
        print("🔄 Reinicia el servicio MCP para que tome los cambios:")
        print("   docker-compose restart mcp")


if __name__ == "__main__":
    main()
