"""Servidor MCP demo que expone la tool kb_search.

No implementa auth ni rate limiting; usar solo en desarrollo.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, List, Optional
import requests
from bs4 import BeautifulSoup
import base64
import io
import mimetypes

from services.kb.demo_kb import kb_search, ingest_docs


app = FastAPI(title="MCP Demo Server")


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


@app.post("/tools/kb_ingest")
def tool_kb_ingest(req: KBIngestRequest) -> dict:
    prepared: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    if req.docs:
        for d in req.docs:
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
            prepared.append({
                "id": d.id or (d.filename or (text_content[:40] if text_content else "doc")),
                "text": text_content,
                "metadata": d.metadata or {},
            })

    url_count = 0
    if req.urls:
        for url in req.urls:
            try:
                # User-Agent por defecto para evitar bloqueos simples
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; FixeatAI/0.1; +https://fixeat.ai)",
                    "Accept": "*/*",
                }
                if req.url_headers:
                    headers.update(req.url_headers)
                resp = requests.get(url, timeout=15, headers=headers)
                if resp.status_code >= 400:
                    errors.append({
                        "url": url,
                        "status": resp.status_code,
                        "reason": resp.reason,
                    })
                    continue
                content_type = resp.headers.get("Content-Type", "").lower()
                # detectar por cabecera o por extensión
                if "text/html" in content_type or url.lower().endswith((".html", ".htm")):
                    text = _extract_text_from_html(resp.text)
                elif "pdf" in content_type or url.lower().endswith(".pdf"):
                    text = _extract_text_from_pdf(resp.content)
                elif "word" in content_type or url.lower().endswith(".docx"):
                    text = _extract_text_from_docx(resp.content)
                elif "excel" in content_type or url.lower().endswith(".xlsx"):
                    text = _extract_text_from_xlsx(resp.content)
                else:
                    # fallback: intentar como texto
                    try:
                        text = resp.content.decode("utf-8", errors="ignore")
                    except Exception:
                        text = ""
                if text:
                    prepared.append({
                        "id": url,
                        "text": text,
                        "metadata": {"source": url},
                    })
                    url_count += 1
            except Exception as ex:
                errors.append({"url": url, "error": str(ex)[:200]})
                continue

    if prepared:
        ingest_docs(prepared)

    return {"ingested": len(prepared), "from_urls": url_count, "errors": errors}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


