"""Servidor MCP demo que expone la tool kb_search.

No implementa auth ni rate limiting; usar solo en desarrollo.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, List, Optional
import hashlib
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import base64
import io
import mimetypes

from services.kb.demo_kb import kb_search, ingest_docs, get_all_documents
from services.taxonomy.auto_learner import TaxonomyAutoLearner
from services.llm.client import LLMClient


app = FastAPI(title="MCP Demo Server")
@app.get("/tools/taxonomy")
def get_taxonomy() -> dict:
    return _TAXONOMY


class UpsertTaxonomyRequest(BaseModel):
    domain: str  # brands|models|categories|synonyms
    canonical: str
    alias: str | None = None


@app.post("/tools/taxonomy/upsert")
def upsert_taxonomy(req: UpsertTaxonomyRequest) -> dict:
    changed = _update_taxonomy(req.domain, req.canonical, req.alias)
    if changed:
        _save_taxonomy()
    return {"ok": True, "changed": changed}


class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    where: Optional[dict[str, Any]] = None


@app.on_event("startup")
def _seed_data() -> None:
    # Solo para desarrollo - deshabilitar en producción
    if os.getenv("ENVIRONMENT") == "development":
        ingest_docs(
            [
                {"id": "dev_seed", "text": "Documento de desarrollo - NO usar en producción", "metadata": {"source": "dev_seed", "environment": "development"}},
            ]
        )


@app.post("/tools/kb_search")
def tool_kb_search(req: KBSearchRequest) -> dict:
    hits = kb_search(req.query, req.top_k, req.where)
    return {"hits": hits}


class DBQueryRequest(BaseModel):
    sql: str
    params: Optional[list[Any]] = None


@app.post("/tools/db_query")
def tool_db_query(req: DBQueryRequest) -> dict:
    """Tool de ejemplo para consultas de solo lectura.

    Esta demo no se conecta a una BD real; devuelve resultados simulados
    para queries select comunes. En producción, aquí se integraría un
    pool de conexiones read-only y validación de consultas.
    """
    sql_low = (req.sql or "").strip().lower()
    if not sql_low.startswith("select"):
        return {"error": "solo se permiten SELECT en este endpoint"}
    # Respuestas simuladas
    if "from inventario" in sql_low:
        rows = [
            {"sku": "PUMP-ACME-01", "stock": 3, "bodega": "SCL"},
            {"sku": "FILTRO-UNI-02", "stock": 12, "bodega": "SCL"},
        ]
    elif "from visitas" in sql_low:
        rows = [
            {"ticket_id": 1001, "equipo_model": "T900", "issue": "falla bomba"},
            {"ticket_id": 1002, "equipo_model": "T900", "issue": "sensor humedad"},
        ]
    else:
        rows = []
    return {"rows": rows, "count": len(rows)}


class IngestDoc(BaseModel):
    id: Optional[str] = None
    text: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    # archivo en base64 y su tipo opcional
    file_base64: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None


class KBIngestRequest(BaseModel):
    docs: Optional[List[IngestDoc]] = None
    urls: Optional[List[str]] = None
    url_headers: Optional[dict[str, str]] = None  # cabeceras opcionales para descargas
    auto_curate: Optional[bool] = False
    auto_learn_taxonomy: Optional[bool] = False  # NUEVO: auto-aprendizaje de taxonomía


class CanonicalDoc(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any]


class KBCurateRequest(BaseModel):
    docs: Optional[List[IngestDoc]] = None
    urls: Optional[List[str]] = None
    url_headers: Optional[dict[str, str]] = None
    auto_learn_taxonomy: Optional[bool] = False  # NUEVO: auto-aprendizaje de taxonomía


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(s for s in soup.stripped_strings)
    return text


def _extract_text_from_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        buff = io.BytesIO(data)
        reader = PdfReader(buff)
        texts: list[str] = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        if any(texts): # Si pypdf extrajo algo, usarlo
            return "\n".join(t.strip() for t in texts if t)
    except Exception:
        pass # Fallback a pdfminer.six si pypdf falla o no está instalado

    try:
        from pdfminer.high_level import extract_text as pdfminer_extract_text
        return pdfminer_extract_text(io.BytesIO(data))
    except Exception:
        return ""


def _extract_text_from_docx(data: bytes) -> str:
    try:
        import docx  # python-docx
    except Exception:
        return ""
    buff = io.BytesIO(data)
    doc = docx.Document(buff)
    paras = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paras)


def _extract_text_from_xlsx(data: bytes) -> str:
    try:
        import pandas as pd
    except Exception:
        return ""
    buff = io.BytesIO(data)
    try:
        dfs = pd.read_excel(buff, sheet_name=None, engine="openpyxl")
    except Exception:
        return ""
    texts: list[str] = []
    for name, df in dfs.items():
        try:
            texts.append(f"# Hoja: {name}\n" + df.to_csv(index=False))
        except Exception:
            continue
    return "\n".join(texts)


def _infer_mime_from_name(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    mt, _ = mimetypes.guess_type(filename)
    return mt


def _extract_text_from_binary(data: bytes, filename: Optional[str], mime_type: Optional[str]) -> str:
    inferred = mime_type or _infer_mime_from_name(filename) or ""
    inferred = inferred.lower()
    if "pdf" in inferred or (filename or "").lower().endswith(".pdf"):
        return _extract_text_from_pdf(data)
    if "word" in inferred or "docx" in inferred or (filename or "").lower().endswith(".docx"):
        return _extract_text_from_docx(data)
    if "excel" in inferred or "spreadsheet" in inferred or (filename or "").lower().endswith(".xlsx"):
        return _extract_text_from_xlsx(data)
    # Fallback: intentar decodificar como texto plano
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""
def _chunk_text(text: str, size: int = 1200, overlap: int = 200) -> List[str]:
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= n:
            break
        start = end - overlap
    return chunks


def _quality_score(text: str) -> float:
    length = len(text)
    if length >= 4000:
        return 0.95
    if length >= 1500:
        return 0.9
    if length >= 600:
        return 0.75
    if length >= 200:
        return 0.6
    return 0.25


def _fingerprint(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _build_canonical_items(base_id: str, text: str, base_metadata: dict[str, Any]) -> List[CanonicalDoc]:
    canonical: List[CanonicalDoc] = []
    chunks = _chunk_text(text)
    now_iso = datetime.utcnow().isoformat() + "Z"
    for idx, chunk in enumerate(chunks):
        md = {
            **(base_metadata or {}),
            "source_type": base_metadata.get("source_type", "unknown"),
            "source_ref": base_metadata.get("source_ref", base_id),
            "chunk_index": idx,
            "fingerprint": _fingerprint(chunk),
            "quality_score": _quality_score(chunk),
            "updated_at": base_metadata.get("updated_at", now_iso),
        }
        if not md.get("source"):
            md["source"] = base_metadata.get("source", "unspecified")
        canonical.append(CanonicalDoc(id=f"{base_id}#c{idx}", text=chunk, metadata=md))
    return canonical


def _load_taxonomy() -> dict[str, Any]:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "taxonomy.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_TAXONOMY = _load_taxonomy()


def _normalize_entity(value: Optional[str], mapping: dict[str, list[str]]) -> Optional[str]:
    if not value:
        return None
    val = value.strip().lower()
    for canonical, aliases in (mapping or {}).items():
        if val == canonical.lower() or val in [a.lower() for a in aliases]:
            return canonical
    return value


def _save_taxonomy() -> None:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "taxonomy.json")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_TAXONOMY, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _update_taxonomy(domain: str, canonical: Optional[str], alias: Optional[str]) -> bool:
    if not canonical:
        return False
    mapping = _TAXONOMY.setdefault(domain, {})
    aliases = mapping.setdefault(canonical, [])
    changed = False
    if alias:
        al = alias.strip()
        if al and al.lower() != canonical.lower() and al not in aliases:
            aliases.append(al)
            changed = True
    if canonical not in mapping:
        mapping[canonical] = aliases
        changed = True
    return changed


def _build_alias_map(mapping: dict[str, list[str]]) -> dict[str, str]:
    alias_to_canonical: dict[str, str] = {}
    for canonical, aliases in (mapping or {}).items():
        alias_to_canonical[canonical.lower()] = canonical
        for al in aliases:
            alias_to_canonical[al.lower()] = canonical
    return alias_to_canonical


def _extract_entities_from_text(text: str) -> dict[str, str]:
    """Extracción inteligente de entidades usando análisis contextual mejorado.

    - Busca patrones contextuales más sofisticados
    - Considera variaciones ortográficas y abreviaciones
    - Utiliza proximidad de palabras para mayor precisión
    """
    result: dict[str, str] = {}
    if not text:
        return result
    
    import re
    low = text.lower()

    brand_map = _build_alias_map(_TAXONOMY.get("brands", {}))
    model_map = _build_alias_map(_TAXONOMY.get("models", {}))
    cat_map = _build_alias_map(_TAXONOMY.get("categories", {}))

    # Patrones contextuales mejorados
    def find_contextual_brand() -> Optional[str]:
        """Busca marca en contextos típicos de documentos técnicos."""
        patterns = [
            r"marca[:\s]+([A-Z][A-Z0-9\-\s]*?)(?:\s|$|,|\.|;)",
            r"brand[:\s]+([A-Z][A-Z0-9\-\s]*?)(?:\s|$|,|\.|;)",
            r"fabricante[:\s]+([A-Z][A-Z0-9\-\s]*?)(?:\s|$|,|\.|;)",
            r"manufacturer[:\s]+([A-Z][A-Z0-9\-\s]*?)(?:\s|$|,|\.|;)",
            r"equipo\s+([A-Z][A-Z0-9\-\s]*?)(?:\s+mod\.|\s+modelo|\s+n°|\s+serie)",
            r"(?:horno|laminadora|amasadora|divisora)\s+([A-Z][A-Z0-9\-\s]*?)(?:\s+mod\.|\s+modelo)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Verificar contra taxonomía
                for alias, canonical in brand_map.items():
                    if alias.lower() in candidate.lower() or candidate.lower() in alias.lower():
                        return canonical
                return candidate
        return None

    def find_contextual_model() -> Optional[str]:
        """Busca modelo en contextos típicos."""
        patterns = [
            r"modelo[:\s]+([A-Z0-9\-]+)",
            r"model[:\s]+([A-Z0-9\-]+)",
            r"mod\.?\s*[:\s]*([A-Z0-9\-]+)",
            r"serie[:\s]+([A-Z0-9\-]+)",
            r"n°[:\s]*([A-Z0-9\-]+)",
            r"ref\.?\s*[:\s]*([A-Z0-9\-]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Verificar contra taxonomía
                for alias, canonical in model_map.items():
                    if alias.lower() == candidate.lower():
                        return canonical
                return candidate
        return None

    def find_contextual_category() -> Optional[str]:
        """Busca categoría de equipo."""
        # Buscar palabras clave de equipos
        equipment_keywords = [
            (r"\b(laminadora|rolling\s+machine|laminator)\b", "laminadora"),
            (r"\b(horno|oven|forno)\b", "horno"),
            (r"\b(amasadora|mixer|batidora\s+planetaria)\b", "amasadora"),
            (r"\b(divisora|divider)\b", "divisora"),
            (r"\b(ovilladora|rounder)\b", "ovilladora"),
            (r"\b(freidora|fryer)\b", "freidora"),
            (r"\b(refrigerador|armario\s+refrigerado|congelador|freezer)\b", "refrigerador"),
            (r"\b(c[aá]mara|chamber|fermentadora)\b", "camara"),
            (r"\b(vitrina|display\s+case|showcase)\b", "vitrina"),
            (r"\b(plancha|griddle|sarten\s+basculante)\b", "plancha"),
            (r"\b(lavavajillas|lavavajilas|dishwasher)\b", "lavavajillas"),
            (r"\b(cocina|stove|anafe)\b", "cocina"),
            (r"\b(bomba|pump)\b", "bomba"),
            (r"\b(abatidor|blast\s+chiller)\b", "abatidor"),
            (r"\b(rostizador|rotisserie|roller)\b", "rostizador"),
            (r"\b(rebanadora|slicer)\b", "rebanadora"),
            (r"\b(formadora|moulder)\b", "formadora"),
            (r"\b(envasadora|vacuum\s+packer)\b", "envasadora"),
            (r"\b(inyectadora|injector)\b", "inyectadora"),
            (r"\b(secadora|dryer)\b", "secadora"),
            (r"\b(balanza|scale|b[aá]scula)\b", "balanza"),
            (r"\b([oó]smosis|sistema\s+osmosis)\b", "osmosis")
        ]
        
        for pattern, category in equipment_keywords:
            if re.search(pattern, low):
                return category
        return None

    # Extracción contextual
    contextual_brand = find_contextual_brand()
    contextual_model = find_contextual_model()
    contextual_category = find_contextual_category()

    if contextual_brand:
        result["brand"] = contextual_brand
    if contextual_model:
        result["model"] = contextual_model
    if contextual_category:
        result["category"] = contextual_category

    # Fallback: buscar por alias directo si no se encontró nada
    if not result:
        def scan_map_fallback(a2c: dict[str, str], key: str):
            for alias, canonical in a2c.items():
                if len(alias) >= 3 and re.search(rf"\b{re.escape(alias)}\b", low):
                    result[key] = canonical
                    break

        scan_map_fallback(brand_map, "brand")
        scan_map_fallback(model_map, "model")
        scan_map_fallback(cat_map, "category")

    return result


def _prepare_ingest_docs_from_inputs(
    docs: Optional[List[IngestDoc]], urls: Optional[List[str]], url_headers: Optional[dict[str, str]]
) -> List[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    # desde docs/archivos
    if docs:
        for d in docs:
            text_content = d.text or ""
            if d.file_base64:
                try:
                    binary = base64.b64decode(d.file_base64)
                    extracted = _extract_text_from_binary(binary, d.filename, d.mime_type)
                    text_content = (text_content + "\n" + extracted).strip() if text_content else extracted
                except Exception:
                    pass
            if not text_content:
                continue
            prepared.append(
                {
                    "id": d.id or (d.filename or (text_content[:40] if text_content else "doc")),
                    "text": text_content,
                    "metadata": d.metadata or {},
                }
            )
    # desde URLs
    if urls:
        for url in urls:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (compatible; FixeatAI/0.1; +https://fixeat.ai)", "Accept": "*/*"}
                if url_headers:
                    headers.update(url_headers)
                resp = requests.get(url, timeout=15, headers=headers)
                if resp.status_code >= 400:
                    continue
                content_type = resp.headers.get("Content-Type", "").lower()
                if "text/html" in content_type or url.lower().endswith((".html", ".htm")):
                    text = _extract_text_from_html(resp.text)
                elif "pdf" in content_type or url.lower().endswith(".pdf"):
                    text = _extract_text_from_pdf(resp.content)
                elif "word" in content_type or url.lower().endswith(".docx"):
                    text = _extract_text_from_docx(resp.content)
                elif "excel" in content_type or url.lower().endswith(".xlsx"):
                    text = _extract_text_from_xlsx(resp.content)
                else:
                    try:
                        text = resp.content.decode("utf-8", errors="ignore")
                    except Exception:
                        text = ""
                if text:
                    prepared.append({"id": url, "text": text, "metadata": {"source": url, "source_type": "url", "source_ref": url}})
            except Exception:
                continue
    return prepared


@app.post("/tools/taxonomy/bootstrap")
def bootstrap_taxonomy_from_kb() -> dict:
    """Análisis masivo inicial del KB para extraer taxonomía automáticamente."""
    
    global _TAXONOMY  # Declarar global al inicio
    
    try:
        print("🔄 Iniciando bootstrap de taxonomía...")
        
        # Obtener todo el contenido del KB
        all_docs = get_all_documents()
        if not all_docs:
            print("❌ No hay documentos en el KB")
            return {
                "bootstrap_completed": False,
                "error": "No hay documentos en el KB para analizar",
                "new_brands": 0,
                "new_models": 0,
                "new_categories": 0
            }
        
        print(f"📄 Analizando {len(all_docs)} documentos...")
        
        # Concatenar texto de todos los documentos (limitar tamaño para evitar problemas)
        corpus_parts = []
        total_length = 0
        max_corpus_length = 50000  # Limitar a 50K caracteres para evitar timeouts
        
        for doc in all_docs:
            text = doc.get("text", "")
            if total_length + len(text) > max_corpus_length:
                break
            corpus_parts.append(text)
            total_length += len(text)
        
        corpus = "\n".join(corpus_parts)
        print(f"📊 Corpus construido: {len(corpus)} caracteres")
        
        # Auto-learner sin LLM para evitar timeouts inicialmente
        learner = TaxonomyAutoLearner(llm_client=None)
        
        # Solo extracción heurística por ahora (más rápida)
        print("🔍 Extrayendo entidades heurísticamente...")
        candidates = learner.extract_comprehensive_entities(corpus)
        
        # Procesar candidatos directamente
        original_counts = {k: len(v) for k, v in _TAXONOMY.items()}
        new_entities_count = {"brands": 0, "models": 0, "categories": 0}
        
        for category in ["brands", "models", "categories"]:
            if category not in _TAXONOMY:
                _TAXONOMY[category] = {}
            
            for candidate in candidates.get(category, []):
                if (candidate.confidence >= 0.8 and 
                    candidate.frequency >= 2 and 
                    candidate.value not in _TAXONOMY[category]):
                    
                    _TAXONOMY[category][candidate.value] = []
                    new_entities_count[category] += 1
                    print(f"✅ Nueva {category[:-1]}: {candidate.value}")
        
        # Guardar taxonomía actualizada
        _save_taxonomy()
        print("💾 Taxonomía guardada")
        
        # Estadísticas simplificadas
        stats = {
            "bootstrap_completed": True,
            "new_brands": new_entities_count["brands"],
            "new_models": new_entities_count["models"],
            "new_categories": new_entities_count["categories"],
            "total_docs_analyzed": len(all_docs),
            "corpus_length": len(corpus),
            "processing_method": "heuristic_only",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"🎉 Bootstrap completado: {sum(new_entities_count.values())} nuevas entidades")
        return stats
        
    except Exception as e:
        print(f"❌ Error durante bootstrap: {e}")
        return {
            "bootstrap_completed": False,
            "error": f"Error durante bootstrap: {str(e)}",
            "new_brands": 0,
            "new_models": 0,
            "new_categories": 0
        }


@app.get("/tools/taxonomy/stats")
def get_taxonomy_stats() -> dict:
    """Estadísticas actuales de la taxonomía."""
    
    try:
        print("📊 Generando estadísticas de taxonomía...")
        
        brands = _TAXONOMY.get("brands", {})
        models = _TAXONOMY.get("models", {})
        categories = _TAXONOMY.get("categories", {})
        synonyms = _TAXONOMY.get("synonyms", {})
        
        stats = {
            "brands_count": len(brands),
            "models_count": len(models),
            "categories_count": len(categories),
            "synonyms_count": len(synonyms),
            "total_entities": len(brands) + len(models) + len(categories) + len(synonyms),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Top entidades por categoría (máximo 5)
        if brands:
            stats["top_brands"] = list(brands.keys())[:5]
        else:
            stats["top_brands"] = []
            
        if models:
            stats["top_models"] = list(models.keys())[:5]
        else:
            stats["top_models"] = []
            
        if categories:
            stats["top_categories"] = list(categories.keys())[:5]
        else:
            stats["top_categories"] = []
        
        # Detalles adicionales
        stats["taxonomy_file_exists"] = os.path.exists("configs/taxonomy.json")
        
        print(f"📋 Stats generadas: {stats['total_entities']} entidades totales")
        return stats
        
    except Exception as e:
        print(f"❌ Error generando stats: {e}")
        return {
            "error": f"Error generando estadísticas: {str(e)}",
            "brands_count": 0,
            "models_count": 0,
            "categories_count": 0,
            "total_entities": 0,
            "timestamp": datetime.utcnow().isoformat()
        }


@app.post("/tools/kb_curate")
def tool_kb_curate(req: KBCurateRequest) -> dict:
    global _TAXONOMY  # Declarar global al inicio
    
    raw = _prepare_ingest_docs_from_inputs(req.docs, req.urls, req.url_headers)
    curated: List[dict[str, Any]] = []
    quarantine: List[dict[str, Any]] = []
    taxonomy_changed = False
    learning_stats = {}
    
    # NUEVO: Auto-aprendizaje de taxonomía si está habilitado
    if req.auto_learn_taxonomy:
        try:
            llm_client = LLMClient(agent="taxonomy")
        except Exception as e:
            print(f"Warning: No se pudo inicializar LLM client: {e}")
            llm_client = None
        
        learner = TaxonomyAutoLearner(llm_client)
        
        # Extraer texto de todos los documentos nuevos
        new_text = "\n".join(item.get("text", "") for item in raw)
        
        if new_text:
            # Aprendizaje incremental
            learned_entities = learner.learn_incrementally(new_text, _TAXONOMY)
            
            if learned_entities and any(learned_entities.values()):
                # Merge con taxonomía existente
                for category in ["brands", "models", "categories"]:
                    if category in learned_entities:
                        if category not in _TAXONOMY:
                            _TAXONOMY[category] = {}
                        
                        for entity, aliases in learned_entities[category].items():
                            if entity not in _TAXONOMY[category]:
                                _TAXONOMY[category][entity] = aliases
                                taxonomy_changed = True
                                print(f"🔍 Auto-aprendida {category[:-1]}: {entity}")
                
                # Generar estadísticas de aprendizaje
                learning_stats = learner.get_learning_stats(learned_entities)
    
    # Procesamiento normal de curación
    for item in raw:
        meta = item.get("metadata") or {}
        # Extracción automática si faltan entidades
        if not meta.get("brand") or not meta.get("model") or not meta.get("category"):
            auto = _extract_entities_from_text(item.get("text", ""))
            for k, v in auto.items():
                meta.setdefault(k, v)
        # Normalización básica de entidades con taxonomía
        brand = _normalize_entity(meta.get("brand"), _TAXONOMY.get("brands", {}))
        model = _normalize_entity(meta.get("model"), _TAXONOMY.get("models", {}))
        category = _normalize_entity(meta.get("category"), _TAXONOMY.get("categories", {}))
        if brand:
            meta["brand"] = brand
            taxonomy_changed |= _update_taxonomy("brands", brand, item.get("metadata", {}).get("brand"))
        if model:
            meta["model"] = model
            taxonomy_changed |= _update_taxonomy("models", model, item.get("metadata", {}).get("model"))
        if category:
            meta["category"] = category
            taxonomy_changed |= _update_taxonomy("categories", category, item.get("metadata", {}).get("category"))
        meta.setdefault("source_type", meta.get("source_type", "doc"))
        meta.setdefault("source_ref", meta.get("source_ref", item.get("id")))
        items = _build_canonical_items(item.get("id", "doc"), item.get("text", ""), meta)
        for cd in items:
            if cd.metadata.get("quality_score", 0) < 0.5 or len(cd.text) < 200:
                quarantine.append({"id": cd.id, "reason": "low_quality_or_too_short"})
            else:
                curated.append(cd.model_dump())
    
    if taxonomy_changed:
        _save_taxonomy()
    
    stats = {"input": len(raw), "curated": len(curated), "quarantine": len(quarantine)}
    
    # Agregar estadísticas de aprendizaje si aplica
    if learning_stats:
        stats["auto_learning"] = learning_stats
    
    return {"docs": curated, "quarantine": quarantine, "stats": stats, "taxonomy_updated": taxonomy_changed}


@app.post("/tools/kb_ingest")
def tool_kb_ingest(req: KBIngestRequest) -> dict:
    prepared: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    url_count = 0

    if req.auto_curate:
        # Curación previa y luego ingesta del resultado con auto-aprendizaje opcional
        curate_result = tool_kb_curate(KBCurateRequest(
            docs=req.docs, 
            urls=req.urls, 
            url_headers=req.url_headers,
            auto_learn_taxonomy=req.auto_learn_taxonomy  # NUEVO: pasar flag de auto-aprendizaje
        ))
        curated_docs = curate_result.get("docs", [])
        url_count = len(req.urls or [])
        if curated_docs:
            ingest_docs(curated_docs)
        
        # Incluir estadísticas de aprendizaje si están disponibles
        result = {
            "ingested": len(curated_docs), 
            "from_urls": url_count, 
            "errors": errors, 
            "curated": True, 
            "stats": curate_result.get("stats")
        }
        
        if "auto_learning" in curate_result.get("stats", {}):
            result["auto_learning"] = curate_result["stats"]["auto_learning"]
            
        return result

    # Camino anterior: preparar e ingerir directamente
    prepared = _prepare_ingest_docs_from_inputs(req.docs, req.urls, req.url_headers)
    url_count = len(req.urls or [])
    if prepared:
        ingest_docs(prepared)
    return {"ingested": len(prepared), "from_urls": url_count, "errors": errors, "curated": False}


@app.get("/tools/taxonomy/test")
def test_taxonomy_system() -> dict:
    """Test rápido del sistema de taxonomía con datos de muestra."""
    
    try:
        print("🧪 Probando sistema de taxonomía...")
        
        # Texto de prueba basado en tu archivo data.txt
        test_text = """
        LAMINADORA SOBREMESÓN SINMAG, MOD. SM-520, RODILLO 50[cm], MONOFASICA
        HORNO ROTATORIO 1 CARR. 60X40 18 NIV. GAS-PETROLEO TRIFASICO ZUCCHELLI, MOD. MINIFANTON 60X40G
        DIVISORA OVILLADORA 4 SALIDAS 30-150[gr] 6000 PIEZAS-HORA FUTURE TRIMA, MOD. PRIMA EVO KE 4
        Horno de Piso U-HP3 ECO
        """
        
        # Crear auto-learner sin LLM
        learner = TaxonomyAutoLearner(llm_client=None)
        
        # Extraer entidades
        candidates = learner.extract_comprehensive_entities(test_text)
        
        # Contar resultados
        results = {}
        for category in ["brands", "models", "categories"]:
            results[category] = []
            for candidate in candidates.get(category, []):
                if candidate.confidence >= 0.7:
                    results[category].append({
                        "value": candidate.value,
                        "confidence": candidate.confidence,
                        "frequency": candidate.frequency
                    })
        
        return {
            "test_completed": True,
            "results": results,
            "total_candidates": sum(len(v) for v in results.values()),
            "message": "Sistema funcionando correctamente"
        }
        
    except Exception as e:
        return {
            "test_completed": False,
            "error": str(e),
            "message": "Error en el sistema"
        }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


