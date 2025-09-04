## Despliegue y CI/CD

### Contenedores
- Docker base Python 3.11 slim, usuario no root, cachés de dependencias.

### CI
- Jobs: lint → test → build → scan → artifacts.
- Caché de dependencias y reporte de cobertura.

### CD
- Entornos: dev → staging → prod con gates (pruebas y métricas).
- Estrategia de rollback, migraciones de esquemas/índices.


