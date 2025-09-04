## Flujo Operativo y de Desarrollo

Este documento explica, de forma clara y no técnica, cómo fluye la información y cómo trabajar con el repositorio.

### 1) ¿Qué servicios hay?
- **API (app/)**: recibe solicitudes y devuelve respuestas claras.
- **MCP (mcp/)**: ayuda a la API buscando información en la biblioteca.
- **Biblioteca (services/kb/)**: guarda y busca conocimiento (manuales, tips, etc.).

### 2) ¿Cómo fluye una solicitud?
1. Un usuario llama a la API (por ejemplo, `/api/v1/predict-fallas`).
2. La API valida los datos y mantiene un `traceId` para rastrear todo.
3. La API le pide al MCP que busque en la biblioteca (`kb_search`).
4. El MCP consulta la biblioteca y devuelve “pistas” relevantes.
5. La API arma la respuesta final con formato estándar: `traceId`, `code`, `message`, `data`.

### 3) ¿Cómo se ejecuta?
Opción A: Docker (recomendada)
```bash
docker compose build
docker compose up -d
```
Opción B: Local (desarrollo)
```bash
make venv && make kb && make mcp
make run
```

### 4) ¿Dónde está todo?
- `app/`: API y endpoints.
- `mcp/`: servidor con la herramienta `kb_search`.
- `services/kb/`: funciones para ingresar y buscar conocimiento.
- `docs/`: manuales del sistema (API, arquitectura, quickstart, docker, etc.).
- `Dockerfile` y `docker-compose.yml`: levantan API y MCP juntos.
- `Makefile` y `pyproject.toml`: facilitan instalación y calidad de código.

### 5) ¿Cómo agregar conocimiento?
- Editar `services/kb/demo_kb.py` para cargar documentos (ingesta).
- En Docker, la biblioteca persiste en el volumen `chroma_data`.

### 6) Calidad y trazabilidad
- Todas las respuestas incluyen `traceId`, `code`, `message`, `data`.
- Ver estándares en `docs/estandares-codigo.md` y pruebas en `docs/testing.md`.


 es cada carpeta y cómo se conectan entre si, explicalo cómo si fuese una persona no técnica

Visión general (en palabras simples)
Piensa en el proyecto como dos “servicios” que trabajan juntos:
API: recibe preguntas y devuelve respuestas ordenadas.
Ayudante de conocimiento (MCP): busca información en una “biblioteca” y le pasa pistas a la API.
Todo queda documentado y listo para ejecutarse con un solo comando usando Docker.
Carpetas y para qué sirve cada una
app/: la “recepción” del servicio.
Contiene la API hecha con FastAPI.
Archivo clave: app/main.py. Define los endpoints:
POST /predict-fallas
POST /soporte-tecnico
POST /validar-formulario
Estandariza todas las respuestas con traceId, code, message, data (así siempre sabes qué pasó y puedes rastrearlo).
mcp/: el “ayudante de conocimiento”.
Archivo clave: mcp/server_demo.py. Expone una herramienta llamada kb_search.
Cuando la API necesita contexto (manuales, tips, etc.), llama a este ayudante para que busque en la biblioteca.
services/: la “biblioteca” y otros servicios internos.
Subcarpeta clave: services/kb/.
Archivo clave: services/kb/demo_kb.py.
Permite “ingresar documentos” a la biblioteca (ingesta) y “buscar” (kb_search).
Usa un motor de búsqueda semántica (Chroma + embeddings) para encontrar textos relevantes, no solo palabras exactas.
Guarda la biblioteca en disco si existe la variable CHROMA_PATH (en Docker ya queda persistente).
docs/: el “manual del sistema”.
arquitectura.md: cómo está diseñado todo.
api.md: qué endpoints existen y ejemplos.
datos.md: formatos de entrada/salida.
mcp-orquestacion.md: cómo se conectan la API, el ayudante MCP y la biblioteca.
quickstart.md: pasos rápidos para correrlo en tu máquina.
docker.md: cómo correrlo con Docker.
Otros: estándares, testing, seguridad, MLOps, etc.
Raíz del repo (archivos de soporte)
Dockerfile: construye una imagen que sirve tanto para la API como para el MCP (controlado por la variable ROLE).
docker-compose.yml: levanta los dos servicios juntos:
mcp en el puerto 7000.
api en el puerto 8000.
Comparte un “volumen” para que la biblioteca quede guardada.
.dockerignore: evita copiar archivos innecesarios a la imagen.
pyproject.toml: lista dependencias y configuraciones de calidad de código.
Makefile: atajos para desarrollar localmente (crear entorno, correr API, etc.).
README.md: índice y roadmap.
CONTRIBUTING.md y .github/PULL_REQUEST_TEMPLATE.md: cómo colaborar y revisar cambios.


Cómo se conectan entre sí (flujo paso a paso)
Un usuario o sistema llama a la API: por ejemplo, POST /api/v1/predict-fallas.
La API (en app/main.py) recibe los datos, genera o reutiliza un traceId y valida el formato.
La API pide ayuda al MCP llamando su herramienta kb_search:
Le pasa la descripción del problema.
El MCP (mcp/server_demo.py) consulta la biblioteca:
Llama a services/kb/demo_kb.py para buscar textos relevantes usando búsquedas semánticas.
La biblioteca (Chroma) devuelve “pistas” (fragmentos y fuentes).
El MCP devuelve esas pistas a la API.
La API arma una respuesta clara:
“Posibles fallas”, “repuestos y herramientas”, “pasos recomendados” o “validaciones”.
Siempre con el formato estándar: traceId, code, message, data.
Gracias al traceId, es fácil seguir todo el camino de una consulta (ver logs/diagnósticos).

