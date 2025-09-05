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

from services.kb.demo_kb import kb_search, ingest_docs


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
    # Datos mínimos para pruebas
    ingest_docs(
        [
            {"id": "m1", "text": "Manual modelo X: revisar filtro y bomba", "metadata": {"source": "seed"}},
            {"id": "t1", "text": "Tip técnico: sensor T900 falla con humedad", "metadata": {"source": "seed"}},
        ]
    )


@app.post("/tools/kb_search")
def tool_kb_search(req: KBSearchRequest) -> dict:
    hits = kb_search(req.query, req.top_k, req.where)
    return {"hits": hits}


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


class CanonicalDoc(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any]


class KBCurateRequest(BaseModel):
    docs: Optional[List[IngestDoc]] = None
    urls: Optional[List[str]] = None
    url_headers: Optional[dict[str, str]] = None


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(s for s in soup.stripped_strings)
    return text


def _extract_text_from_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""
    buff = io.BytesIO(data)
    reader = PdfReader(buff)
    texts: list[str] = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(t.strip() for t in texts if t)


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
    """Heurística simple: busca ocurrencias de marcas/modelos/categorías usando taxonomía.

    - Coincidencias por alias con límites de palabra
    - Patrones básicos tipo "marca:" / "modelo:" / "categoría:"
    """
    result: dict[str, str] = {}
    if not text:
        return result
    low = text.lower()

    brand_map = _build_alias_map(_TAXONOMY.get("brands", {}))
    model_map = _build_alias_map(_TAXONOMY.get("models", {}))
    cat_map = _build_alias_map(_TAXONOMY.get("categories", {}))

    # Patrones explícitos
    import re

    def find_after(label: str) -> Optional[str]:
        # e.g., "marca: acme" o "modelo t900"
        pat = re.compile(rf"{label}\s*[:\-]?\s*([\w\-]+)")
        m = pat.search(low)
        if m:
            return m.group(1)
        return None

    explicit_brand = find_after("marca|brand")
    explicit_model = find_after("modelo|model")
    explicit_cat = find_after("categor(ía|ia)|category")

    # Resolver explícitos contra taxonomía
    if explicit_brand:
        result["brand"] = brand_map.get(explicit_brand, explicit_brand)
    if explicit_model:
        result["model"] = model_map.get(explicit_model, explicit_model)
    if explicit_cat:
        result["category"] = cat_map.get(explicit_cat, explicit_cat)

    # Si faltan, buscar por alias directo (word boundary)
    def scan_map(a2c: dict[str, str], key: str):
        if key in result:
            return
        for alias, canonical in a2c.items():
            # evitar alias muy cortos que generen falsos positivos
            if len(alias) < 2:
                continue
            if re.search(rf"\b{re.escape(alias)}\b", low):
                result[key] = canonical
                break

    scan_map(brand_map, "brand")
    scan_map(model_map, "model")
    scan_map(cat_map, "category")

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


@app.post("/tools/kb_curate")
def tool_kb_curate(req: KBCurateRequest) -> dict:
    raw = _prepare_ingest_docs_from_inputs(req.docs, req.urls, req.url_headers)
    curated: List[dict[str, Any]] = []
    quarantine: List[dict[str, Any]] = []
    taxonomy_changed = False
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
    return {"docs": curated, "quarantine": quarantine, "stats": stats, "taxonomy_updated": taxonomy_changed}


@app.post("/tools/kb_ingest")
def tool_kb_ingest(req: KBIngestRequest) -> dict:
    prepared: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    url_count = 0

    if req.auto_curate:
        # Curación previa y luego ingesta del resultado
        curate_result = tool_kb_curate(KBCurateRequest(docs=req.docs, urls=req.urls, url_headers=req.url_headers))
        curated_docs = curate_result.get("docs", [])
        url_count = len(req.urls or [])
        if curated_docs:
            ingest_docs(curated_docs)
        return {"ingested": len(curated_docs), "from_urls": url_count, "errors": errors, "curated": True, "stats": curate_result.get("stats")}

    # Camino anterior: preparar e ingerir directamente
    prepared = _prepare_ingest_docs_from_inputs(req.docs, req.urls, req.url_headers)
    url_count = len(req.urls or [])
    if prepared:
        ingest_docs(prepared)
    return {"ingested": len(prepared), "from_urls": url_count, "errors": errors, "curated": False}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


