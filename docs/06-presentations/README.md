# 📊 Presentaciones del Predictor de Fallas

Este directorio contiene tres formatos de presentación para el sistema de Predictor de Fallas de FIXEAT AI.

## 📄 Archivos Disponibles

### 1. **presentacion_visual.html** (Recomendado para Presentaciones)
- ✨ Presentación interactiva y visual con diseño moderno
- 🎨 Colores, iconos y layout profesional
- 📱 Responsive (se adapta a móviles y tablets)
- 🖨️ Optimizada para imprimir
- **Uso:** Abre el archivo en cualquier navegador web

**Cómo usar:**
```bash
# En Mac:
open presentacion_visual.html

# En Windows:
start presentacion_visual.html

# En Linux:
xdg-open presentacion_visual.html
```

---

### 2. **PRESENTACION_PREDICTOR_FALLAS.md** (Documentación Completa)
- 📚 Documento markdown extenso y detallado
- 🔍 Incluye todos los detalles técnicos
- 💻 Ejemplos de código en múltiples lenguajes (curl, JavaScript, Python, Swift)
- 📊 Casos de uso reales y métricas
- **Uso:** Ver en GitHub, VS Code, o cualquier visor de Markdown

**Contenido:**
- Arquitectura del sistema
- Endpoints con ejemplos completos
- Integración en aplicaciones
- Mejores prácticas
- Casos de uso reales
- Roadmap y próximas mejoras

---

### 3. **QUICK_REFERENCE_API.md** (Referencia Rápida)
- ⚡ Cheat sheet compacto
- 🎯 Información esencial en formato conciso
- 📋 Perfecto para tener a mano durante desarrollo
- **Uso:** Referencia rápida para desarrolladores

**Contenido:**
- Servidor y puertos
- Endpoints principales
- Estructura de request/response
- Niveles de confidence
- Tips rápidos

---

## 🎯 ¿Cuál Usar?

| Situación | Archivo Recomendado |
|-----------|---------------------|
| **Presentación a clientes** | `presentacion_visual.html` |
| **Presentación a stakeholders** | `presentacion_visual.html` |
| **Documentación técnica** | `PRESENTACION_PREDICTOR_FALLAS.md` |
| **Onboarding de desarrolladores** | `PRESENTACION_PREDICTOR_FALLAS.md` |
| **Referencia rápida durante desarrollo** | `QUICK_REFERENCE_API.md` |
| **Imprimir para tener en escritorio** | `presentacion_visual.html` (Print to PDF) |

---

## 🌐 Servidor Productivo

**IP:** `18.220.79.28`  
**Puerto:** `8000`  
**URL Base:** `http://18.220.79.28:8000`  
**Estado:** ✅ ACTIVO

---

## 🚀 Quick Start

### Verificar que el servidor está activo:
```bash
curl http://18.220.79.28:8000/health
```

### Hacer una predicción:
```bash
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {"id": "c001"},
    "equipo": {"marca": "Rational", "modelo": "Icombi Pro"},
    "descripcion_problema": "El horno no calienta correctamente",
    "tecnico": {"id": "t001", "experiencia_anios": 5}
  }'
```

---

## 📱 Compartir las Presentaciones

### Para compartir por email:
- Adjunta `presentacion_visual.html` (se puede abrir directamente en el navegador)

### Para compartir en repositorio:
- Sube cualquiera de los archivos `.md` a GitHub/GitLab
- Se renderizarán automáticamente con formato

### Para convertir a PDF:
1. Abre `presentacion_visual.html` en Chrome/Edge
2. Ctrl+P (Cmd+P en Mac)
3. Selecciona "Guardar como PDF"
4. Ajusta márgenes a "Ninguno" para mejor resultado

---

## 📊 Archivos de Pruebas

También están disponibles los resultados de las pruebas del sistema:

- `resumen_pruebas_predict_fallas.md` - Análisis completo de 6 pruebas
- `test1_rational_calentamiento.json` - Prueba 1 (Confidence: 0.45)
- `test2_electrolux_vapor.json` - Prueba 2 (Confidence: 0.65)
- `test3_rational_error.json` - Prueba 3 (Confidence: 0.75)
- `test4_generico.json` - Prueba 4 (Confidence: 0.65)
- `test5_detallado.json` - Prueba 5 (Confidence: 0.85) ⭐ Mejor resultado
- `test6_minimo.json` - Prueba 6 (Confidence: 0.50)

---

## ✅ Checklist para Presentaciones

Antes de presentar, verifica:

- [ ] El servidor está activo (curl health endpoint)
- [ ] Tienes ejemplos preparados según tu audiencia
- [ ] Has abierto `presentacion_visual.html` en el navegador
- [ ] Tienes conexión a internet (para probar en vivo)
- [ ] Conoces los casos de uso relevantes para tu audiencia

---

**Creado:** 2 de febrero de 2026  
**Autor:** Equipo FIXEAT AI  
**Última actualización:** 2 de febrero de 2026
