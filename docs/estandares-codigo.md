## Estándares de Código (Python)

### Principios
- Claridad y legibilidad primero. Tipado estático cuando aporte valor.
- Funciones cortas, nombres descriptivos, early returns, manejo explícito de errores.

### Formato y herramientas
- Formateo: Black (`line-length=100`).
- Imports: isort (perfil black).
- Linter: Ruff (reglas base + pep8-naming).
- Tipos: MyPy (`python_version=3.11`, modo estricto gradual en `app/` y `services/`).

### Convenciones
- Nombres: snake_case para funciones/variables, PascalCase para clases.
- Estructura carpetas: `app/`, `services/`, `mcp/`, `tests/`.
- Docstrings: estilo Google o reST en funciones públicas.
- Logging: JSON estructurado, nunca `print()` en producción.

### Manejo de errores
- No atrapar excepciones genéricas sin procesar. Incluir contexto.
- Respuestas API siempre con `traceId`, `code`, `message`, `data`.

### Revisiones
- Commits atómicos (Conventional Commits). PRs pequeños y con pruebas.


