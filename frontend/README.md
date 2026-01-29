# FixeatAI - Frontend de Chat

Frontend simple para interactuar con el sistema de diagnóstico de FixeatAI.

## 🚀 Inicio Rápido

### 1. Asegúrate de que el backend esté corriendo

```bash
cd /Users/sbriceno/Documents/projects/fixeatAI
docker-compose up -d
```

Verifica que el API esté disponible:
```bash
curl http://localhost:8000/health
```

### 2. Abre el frontend

Simplemente abre el archivo en tu navegador:

```bash
open frontend/chat.html
```

O haz doble clic en el archivo `chat.html` desde Finder.

## 💬 Cómo Usar

1. **Escribe el problema** en el cuadro de texto:
   - Ejemplo: "Por qué me arroja un service 25"
   - Ejemplo: "Error 55 en el ventilador"
   - Ejemplo: "Falla en la bomba de agua"

2. **Presiona Enter** o haz clic en **"Enviar"**

3. **Revisa el diagnóstico** que incluye:
   - ✅ Fallas probables con nivel de confianza
   - 🔧 Repuestos sugeridos
   - 🛠️ Herramientas necesarias
   - 📋 Pasos detallados a seguir
   - 📚 Enlaces a documentación (con páginas específicas)

## 🎨 Características

- ✨ **Interfaz tipo chat** moderna y amigable
- 🤖 **Diagnóstico en tiempo real** con IA
- 📄 **Enlaces navegables** a páginas específicas de manuales
- 🎯 **Confianza del diagnóstico** (Alta/Media/Baja)
- 📱 **Responsive** - funciona en desktop y móvil
- ⚡ **Sin instalación** - solo abre el HTML

## 🔧 Configuración

El frontend se conecta por defecto a:
```
http://localhost:8000/api/v1/predict-fallas
```

Si necesitas cambiar la URL del backend, edita la línea 423 en `chat.html`:

```javascript
const API_URL = 'http://localhost:8000/api/v1/predict-fallas';
```

## 📸 Capturas

### Pantalla Principal
- Vista limpia tipo chat
- Entrada de texto con autocompletado
- Indicador de "escribiendo..."

### Respuesta del Diagnóstico
- Cards con información estructurada
- Badges de confianza (colores según nivel)
- Pasos numerados por tipo (seguridad/diagnóstico/reparación)
- Enlaces directos a páginas de manuales

## 🐛 Resolución de Problemas

### Error: "Error al conectar con el servidor"

**Solución:**
1. Verifica que el backend esté corriendo:
   ```bash
   docker ps | grep fixeatai-api
   ```

2. Verifica la salud del API:
   ```bash
   curl http://localhost:8000/health
   ```

3. Si no está corriendo, inícialo:
   ```bash
   cd /Users/sbriceno/Documents/projects/fixeatAI
   docker-compose up -d
   ```

### Los enlaces a PDFs no funcionan

**Causa:** Las URLs son de S3 y requieren acceso a internet.

**Solución:** Asegúrate de tener conexión a internet para ver los PDFs.

### El navegador bloquea las peticiones (CORS)

**Causa:** Algunos navegadores bloquean peticiones desde archivos locales.

**Solución:**
1. Usa Chrome o Firefox (más permisivos)
2. O sirve el archivo con un servidor simple:
   ```bash
   cd frontend
   python3 -m http.server 3000
   # Luego abre: http://localhost:3000/chat.html
   ```

## 🔄 Próximas Mejoras

- [ ] Selector de marca/modelo antes de consultar
- [ ] Historial de conversaciones
- [ ] Exportar diagnóstico a PDF
- [ ] Modo oscuro
- [ ] Búsqueda en historial
- [ ] Compartir diagnóstico por link

## 📝 Notas Técnicas

- **Framework:** Vanilla JavaScript (sin dependencias)
- **Estilo:** CSS puro con gradientes y animaciones
- **API:** REST con JSON
- **Tamaño:** ~18KB (HTML + CSS + JS en un solo archivo)
- **Compatible con:** Chrome, Firefox, Safari, Edge

---

**Desarrollado para FixeatAI** 🔧


