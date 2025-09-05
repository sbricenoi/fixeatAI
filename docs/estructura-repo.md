## Guía de estructura del repositorio (no técnica)

Esta guía explica, con palabras simples, qué hace cada carpeta y archivo del proyecto y cómo se conectan.

### Raíz del proyecto
- `README.md`: portada del proyecto, enlaces a toda la documentación.
- `pyproject.toml`: lista las dependencias de Python y configuración del proyecto.
- `Makefile`: atajos para ejecutar tareas comunes (levantar API, MCP, instalar, etc.).
- `docker-compose.yml` y `Dockerfile`: archivos para ejecutar en contenedores Docker.
- `configs/`: configuraciones del proyecto usadas por la curaduría (por ejemplo, taxonomías aprendidas).
  - `taxonomy.json`: diccionario de nombres estandarizados (marcas, modelos, categorías) que se va actualizando automáticamente.
- `docs/`: documentación funcional y técnica (endpoints, estándares, guías y manuales).

### Aplicación (API)
- `app/main.py`: la aplicación principal con FastAPI. Aquí viven los endpoints que consumen los clientes:
  - `/api/v1/predict-fallas`: devuelve diagnóstico y sugerencias.
  - `/api/v1/soporte-tecnico`: pasos recomendados.
  - `/api/v1/validar-formulario`: valida la coherencia de un formulario.
  - `/api/v1/qa`: preguntas y respuestas libres con ayuda de la base de conocimiento.

### Servicios (lógica de negocio y orquestación)
- `services/`: contiene piezas independientes que la API va combinando.
  - `kb/` (Knowledge Base): cómo guardamos y buscamos conocimiento.
    - `demo_kb.py`: conecta con el motor de búsqueda semántica y gestiona la ingesta de textos.
  - `llm/`: conexión con el modelo de lenguaje (IA) externo.
    - `client.py`: maneja la llamada al proveedor (por ejemplo, OpenAI) y los parámetros del modelo.
  - `orch/` (Orquestación): coordina varias piezas para responder con contexto.
    - `rag.py`: realiza el flujo RAG (buscar en la KB, construir contexto y preguntar al LLM) y agrega señales de evidencia.
  - `predictor/` (Heurística): reglas simples para tener resultados incluso sin IA generativa.
    - `heuristic.py`: calcula predicciones usando coincidencias básicas en la KB.
  - `rules/` (Reglas de negocio): recetas de soporte y diagnóstico.
    - `diagnostico.py` y `soporte.py`: devuelven pasos sugeridos.
  - `validation/` (Validaciones): verifica y corrige formularios.
    - `formulario.py`: chequeos de coherencia y sugerencias de corrección.

### MCP (servidor de herramientas)
- `mcp/server_demo.py`: servicio auxiliar que ofrece “herramientas” a la API u orquestadores:
  - `/tools/kb_ingest`: ingesta documentos, URLs o archivos. Puede auto‑curar (limpiar, fragmentar, etiquetar) antes de guardar.
  - `/tools/kb_curate`: prueba la curación sin guardar (útil para revisar cómo quedarán los datos).
  - `/tools/kb_search`: busca en la base de conocimiento (con filtros por marca/modelo/categoría).
  - `/tools/taxonomy` y `/tools/taxonomy/upsert`: ver y actualizar el diccionario de nombres estandarizados.

### Documentación clave (directorio `docs/`)
- `arquitectura.md`: visión general del sistema y componentes.
- `api.md`: contratos de los endpoints (qué reciben y devuelven).
- `entorno-configuracion.md`: variables de entorno y cómo configurar.
- `llm.md`: cómo usamos la IA y el flujo RAG.
- `mcp-tools.md`: documentación de las herramientas del MCP.
- `quickstart.md`: guía rápida para levantar todo en local.
- `docker.md`: cómo usar Docker/Compose.
- `runbook-local.md`: manual paso a paso para operar y probar.
- Además: seguridad, observabilidad, pruebas, CI/CD, MLOps, roadmap, etc.

### Cómo se conectan
1) MCP ingesta y cura la información (archivos/URLs/BD) → guarda “chunks” con metadatos útiles.
2) La API recibe una consulta (por ejemplo, “predecir fallas”) → pide contexto al MCP.
3) Orquestación (RAG) arma un mensaje claro con fragmentos de la KB → pregunta al LLM.
4) La respuesta vuelve a la API con formato estándar y trazabilidad (`traceId`, `code`, `message`, `data`).

### Para personas no técnicas: ¿qué debo saber?
- Piensa en la KB como una “biblioteca” digital donde metemos manuales y procedimientos. Cuanto mejor los metadatos (marca/modelo/categoría), mejor busca.
- La IA no “adivina”: primero busca en la biblioteca (RAG) y luego redacta una respuesta. Si hay poca evidencia, lo indica en `signals`.
- Puedes cargar información desde links o archivos; el sistema limpia y ordena todo automáticamente.


