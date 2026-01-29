"""Chunking semántico inteligente para documentos técnicos.

Este módulo implementa estrategias avanzadas de chunking que:
1. Respetan límites naturales del documento (párrafos, secciones)
2. Evitan cortar en medio de información crítica
3. Mantienen contexto semántico coherente
4. Optimizan tamaño para embeddings y LLMs

Estrategias implementadas:
- Chunking por párrafos con overlap inteligente
- Detección de secciones (títulos, códigos de error)
- Preservación de listas y tablas
- Chunking adaptativo según tipo de contenido
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import re


class SemanticChunker:
    """Chunker semántico para documentos técnicos."""
    
    def __init__(
        self,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        min_chunk_size: int = 300,
        respect_boundaries: bool = True
    ):
        """Inicializa el chunker semántico.
        
        Args:
            chunk_size: Tamaño objetivo de cada chunk en caracteres
            chunk_overlap: Overlap entre chunks consecutivos
            min_chunk_size: Tamaño mínimo de un chunk (evita chunks muy pequeños)
            respect_boundaries: Si respetar límites naturales del texto
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.respect_boundaries = respect_boundaries
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Divide texto en chunks semánticamente coherentes.
        
        Args:
            text: Texto a dividir
            metadata: Metadata base para heredar en chunks
            
        Returns:
            Lista de chunks con texto y metadata enriquecida
        """
        if not text:
            return []
        
        if metadata is None:
            metadata = {}
        
        # Detectar tipo de contenido
        content_type = self._detect_content_type(text)
        
        # Aplicar estrategia según tipo
        if content_type == "error_codes":
            chunks = self._chunk_error_codes(text)
        elif content_type == "procedures":
            chunks = self._chunk_procedures(text)
        elif content_type == "tables":
            chunks = self._chunk_tables(text)
        else:
            chunks = self._chunk_paragraphs(text)
        
        # Enriquecer metadata
        result = []
        for idx, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": idx,
                "chunk_size": len(chunk_text),
                "chunk_type": content_type,
                "total_chunks": len(chunks),
            }
            
            result.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        return result
    
    def _detect_content_type(self, text: str) -> str:
        """Detecta el tipo de contenido predominante.
        
        Returns:
            Tipo: "error_codes", "procedures", "tables", "general"
        """
        # Detectar códigos de error (E55, S_55, Error 123, etc.)
        error_pattern = r'(?:error|código|code|fallo)[:\s]+[A-Z0-9_\-]+'
        error_matches = len(re.findall(error_pattern, text, re.IGNORECASE))
        
        # Detectar procedimientos (pasos numerados)
        procedure_pattern = r'(?:^|\n)\s*\d+[\.\)]\s+'
        procedure_matches = len(re.findall(procedure_pattern, text))
        
        # Detectar tablas (múltiples pipes o tabs)
        table_pattern = r'(?:\|.*\||\t.*\t)'
        table_matches = len(re.findall(table_pattern, text))
        
        # Clasificar según detecciones
        if error_matches >= 3:
            return "error_codes"
        elif procedure_matches >= 5:
            return "procedures"
        elif table_matches >= 5:
            return "tables"
        else:
            return "general"
    
    def _chunk_paragraphs(self, text: str) -> List[str]:
        """Chunking respetando párrafos.
        
        Estrategia:
        1. Dividir por párrafos (doble newline)
        2. Agrupar párrafos hasta alcanzar chunk_size
        3. Agregar overlap con párrafos del chunk anterior
        """
        # Dividir en párrafos
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            return [text]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            # Si el párrafo solo excede el límite, agregarlo directamente
            if para_size > self.chunk_size:
                # Guardar chunk actual si existe
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Agregar párrafo largo como chunk independiente
                chunks.append(para)
                continue
            
            # Si agregar este párrafo excede chunk_size, cerrar chunk actual
            if current_size + para_size > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                
                # Overlap: mantener último párrafo si no es muy largo
                if current_chunk and len(current_chunk[-1]) < self.chunk_overlap:
                    current_chunk = [current_chunk[-1], para]
                    current_size = len(current_chunk[-1]) + para_size
                else:
                    current_chunk = [para]
                    current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Agregar último chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def _chunk_error_codes(self, text: str) -> List[str]:
        """Chunking especializado para secciones de códigos de error.
        
        Estrategia:
        - Cada código de error con su descripción es un chunk
        - Mantener contexto de causa/solución junto
        """
        # Patrón para detectar inicio de código de error
        pattern = r'(?:^|\n)\s*(?:Error|Code|Código|S_|E)\s*[:\-]?\s*[A-Z0-9_\-]+'
        
        # Dividir en secciones de error
        sections = re.split(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        headers = re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        
        chunks = []
        
        for i, section in enumerate(sections[1:], start=0):  # Saltar primera sección (antes del primer error)
            if i < len(headers):
                chunk = headers[i].strip() + "\n" + section.strip()
                
                # Si el chunk es muy grande, dividirlo por párrafos
                if len(chunk) > self.chunk_size * 1.5:
                    sub_chunks = self._chunk_paragraphs(chunk)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def _chunk_procedures(self, text: str) -> List[str]:
        """Chunking para procedimientos paso a paso.
        
        Estrategia:
        - Agrupar pasos relacionados
        - Mantener continuidad de procedimiento
        """
        # Dividir por pasos numerados
        pattern = r'(?:^|\n)\s*\d+[\.\)]\s+'
        sections = re.split(pattern, text, flags=re.MULTILINE)
        headers = re.findall(pattern, text, flags=re.MULTILINE)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, section in enumerate(sections[1:], start=0):
            if i < len(headers):
                step = headers[i].strip() + section.strip()
                step_size = len(step)
                
                if current_size + step_size > self.chunk_size and current_chunk:
                    chunks.append("\n".join(current_chunk))
                    
                    # Overlap: mantener último paso
                    if current_chunk:
                        current_chunk = [current_chunk[-1], step]
                        current_size = len(current_chunk[-1]) + step_size
                    else:
                        current_chunk = [step]
                        current_size = step_size
                else:
                    current_chunk.append(step)
                    current_size += step_size
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        return chunks if chunks else [text]
    
    def _chunk_tables(self, text: str) -> List[str]:
        """Chunking para tablas y contenido tabulado.
        
        Estrategia:
        - Mantener tablas completas cuando sea posible
        - Dividir por grupos de filas si es muy grande
        """
        # Por ahora, tratamiento simple: dividir por párrafos
        # En producción, implementar parser de tablas específico
        return self._chunk_paragraphs(text)


def chunk_document(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 1200,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """Función de conveniencia para chunking rápido.
    
    Args:
        text: Texto a dividir
        metadata: Metadata base
        chunk_size: Tamaño objetivo de chunks
        chunk_overlap: Overlap entre chunks
        
    Returns:
        Lista de chunks con texto y metadata
    """
    chunker = SemanticChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return chunker.chunk_text(text, metadata)


if __name__ == "__main__":
    # Test básico
    test_text = """
Error S_55 iCombi Pro / Servicio 55 iCombi Classic / S_55_1 iHexagon - Error de funcionamiento en el motor del ventilador

Descripción: Funcionamiento incorrecto del motor del ventilador

Causa: Las revoluciones del motor del ventilador no están en el rango esperado.

Solución:
1. Comprobar si hay bloqueos en la turbina
2. Verificar el estado del motor del ventilador
3. Revisar las conexiones eléctricas
4. Sustituir el motor si es necesario

Error S_56 iCombi Pro / Servicio 56 iCombi Classic - Error en bomba de agua

Descripción: La bomba de agua no funciona correctamente

Causa: Bomba bloqueada o dañada

Solución:
1. Verificar alimentación eléctrica
2. Comprobar bomba por bloqueos
3. Reemplazar bomba si necesario
    """
    
    chunks = chunk_document(test_text, {"source": "test_manual.pdf"})
    print(f"Chunks generados: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ({chunk['metadata']['chunk_type']}) ---")
        print(f"Tamaño: {chunk['metadata']['chunk_size']} chars")
        print(chunk['text'][:200] + "...")


