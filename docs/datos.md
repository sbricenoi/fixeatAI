## Contratos de Datos

Este documento define los esquemas de entrada/salida para los endpoints del microservicio.

### Tipos base

```yaml
Cliente:
  id: string
  historial_visitas: string[]  # fechas ISO YYYY-MM-DD

Tecnico:
  id: string
  experiencia_anios: number
  visitas_previas: number

Equipo:
  marca: string
  modelo: string
  fecha_instalacion: string  # YYYY-MM-DD
  historial_fallas: string[]  # códigos o descripciones

ProbableFalla:
  falla: string
  confidence: number  # 0..1
  rationale?: string

Paso:
  orden: number
  descripcion: string
  tipo: string  # diagnostico | reparacion | otro

ValidacionError:
  path: string
  msg: string
```

### Request/Response: POST /predict-fallas

Request
```yaml
PredictFallasRequest:
  cliente: Cliente
  equipo: Equipo
  descripcion_problema: string
  tecnico: Tecnico
```

Response
```yaml
PredictFallasResponse:
  traceId: string
  code: string
  message: string
  data:
    fallas_probables: ProbableFalla[]
    repuestos_sugeridos: string[]
    herramientas_sugeridas: string[]
```

### Request/Response: POST /soporte-tecnico

Request
```yaml
SoporteTecnicoRequest:
  cliente:
    id: string
  equipo:
    marca: string
    modelo: string
  descripcion_problema: string
  contexto:
    nivel_detalle: string  # basico | intermedio | avanzado
```

Response
```yaml
SoporteTecnicoResponse:
  traceId: string
  code: string
  message: string
  data:
    pasos: Paso[]
```

### Request/Response: POST /validar-formulario

Request
```yaml
ValidarFormularioRequest:
  cliente:
    id: string
  equipo:
    marca: string
    modelo: string
    fecha_instalacion: string  # YYYY-MM-DD
  descripcion_problema: string
  campos_formulario:
    fecha_visita: string  # YYYY-MM-DD
    lectura_temperatura: number
    codigo_falla: string
```

Response
```yaml
ValidarFormularioResponse:
  traceId: string
  code: string
  message: string
  data:
    es_valido: boolean
    inconsistencias:
      - campo: string
        tipo: string  # rango | formato | coherencia | requerido
        detalle: string
    correcciones_sugeridas: object
    feedback_coherencia: string
```

### Notas de validación
- `confidence` entre 0 y 1 con dos decimales recomendados.
- Fechas en formato ISO `YYYY-MM-DD`.
- Strings normalizados en UTF-8, sin HTML.


