# 🤖 Integración LLM Local con FixeatAI

## 🎯 **Sistema Escalable para LLM Local**

El sistema de auto-taxonomía está **100% preparado** para modelos LLM locales. Te muestro las opciones y configuraciones.

## 🔧 **Opción 1: Ollama (Recomendado)**

### **Instalación Ollama**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Descargar desde https://ollama.ai/download
```

### **Modelos Recomendados para Taxonomía**

```bash
# Modelos optimizados para análisis técnico
ollama pull llama3.1:8b        # Equilibrio rendimiento/calidad
ollama pull mistral:7b         # Más rápido, menor memoria
ollama pull codellama:13b      # Especializado en texto técnico
ollama pull llama3.1:70b       # Máxima calidad (requiere GPU potente)
```

### **Configuración en FixeatAI**

```bash
# .env
LLM_AGENTS='{
  "taxonomy": {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "sk-local",
    "temperature": 0.1,
    "max_tokens": 1000
  },
  "prediction": {
    "model": "mistral:7b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "sk-local",
    "temperature": 0.2,
    "max_tokens": 800
  }
}'
```

### **Iniciar Ollama**

```bash
# Terminal 1: Servidor Ollama
ollama serve

# Terminal 2: Probar modelo
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "¿Qué es una laminadora SINMAG?"}]
  }'
```

## 🔧 **Opción 2: LocalAI**

### **Docker con LocalAI**

```yaml
# docker-compose-local-ai.yml
version: '3.8'
services:
  localai:
    image: quay.io/go-skynet/local-ai:latest
    ports:
      - "8080:8080"
    volumes:
      - ./models:/models
    environment:
      - THREADS=4
      - CONTEXT_SIZE=1024
    command: --models-path /models --address 0.0.0.0:8080
```

```bash
# Iniciar LocalAI
docker-compose -f docker-compose-local-ai.yml up -d

# Configuración en .env
LLM_AGENTS='{
  "taxonomy": {
    "model": "ggml-model-q4_0.bin",
    "base_url": "http://localhost:8080/v1",
    "api_key": "sk-local"
  }
}'
```

## 🔧 **Opción 3: LM Studio**

### **Configuración LM Studio**

1. **Descargar**: https://lmstudio.ai/
2. **Cargar modelo**: Llama 3.1 8B o Mistral 7B
3. **Iniciar servidor local**: Puerto 1234 (default)

```bash
# .env para LM Studio
LLM_AGENTS='{
  "taxonomy": {
    "model": "llama-3.1-8b-instruct",
    "base_url": "http://localhost:1234/v1",
    "api_key": "sk-local"
  }
}'
```

## 🎯 **Puntos de Integración en FixeatAI**

### **1. Auto-Taxonomía (Principal)**

```python
# services/taxonomy/auto_learner.py
def _validate_high_frequency_with_llm(self, candidates, corpus_sample):
    """Aquí se llama al LLM local para validar entidades."""
    
    system_prompt = """
    Eres un experto en equipos industriales de panadería.
    Valida estas entidades extraídas de documentos técnicos...
    """
    
    # Esta línea usa el LLM configurado
    raw_response = self.llm.complete_json(system_prompt, user_prompt)
```

### **2. Habilitación Automática**

```python
# mcp/server_demo.py - Bootstrap
if self.llm is None:
    print("🔧 Usando validación heurística (sin LLM)")
    validated = self._fallback_validation(consolidated)
else:
    print("🤖 Usando validación LLM")
    validated = self._validate_high_frequency_with_llm(consolidated, safe_corpus)
```

### **3. Configuración Dinámica**

```python
# services/llm/client.py - Ya implementado
def __init__(self, agent: Optional[str] = None):
    """Cliente que soporta múltiples agentes con configs diferentes."""
    
    # Busca configuración específica del agente
    cfg = agents_cfg.get(agent or "", {})
    
    # Permite base_url para servidores locales
    base_url = cfg.get("base_url")
    if base_url:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
```

## 🚀 **Prueba Inmediata**

### **1. Instalar Ollama y Modelo**

```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.1:8b

# Iniciar servidor
ollama serve
```

### **2. Configurar FixeatAI**

```bash
# Agregar a .env
echo 'LLM_AGENTS={"taxonomy":{"model":"llama3.1:8b","base_url":"http://localhost:11434/v1","api_key":"sk-local","temperature":0.1}}' >> .env
```

### **3. Probar Bootstrap con LLM**

```bash
# Reiniciar servidor FixeatAI
make mcp

# Probar bootstrap (ahora con LLM local)
curl -X POST http://localhost:7070/tools/taxonomy/bootstrap
```

## 📊 **Comparación de Opciones**

| Opción | Facilidad | Rendimiento | Memoria RAM | GPU | Recomendado |
|--------|-----------|-------------|-------------|-----|-------------|
| **Ollama** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8GB+ | Opcional | ✅ **SÍ** |
| LocalAI | ⭐⭐⭐ | ⭐⭐⭐ | 6GB+ | Opcional | Para Docker |
| LM Studio | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8GB+ | Recomendada | Para GUI |

## 🎯 **Beneficios del LLM Local**

### **Con LLM Local**
- ✅ **Validación inteligente** de entidades candidatas
- ✅ **Detección de sinónimos** automática
- ✅ **Filtrado de falsos positivos** mejorado
- ✅ **Comprensión contextual** avanzada
- ✅ **Cero costos** de API externa
- ✅ **Privacidad total** de datos

### **Solo Heurístico (Actual)**
- ✅ **Rápido y eficiente**
- ✅ **Sin dependencias externas**
- ❌ Menos preciso en casos ambiguos
- ❌ No detecta sinónimos automáticamente

## 🔍 **Casos de Uso Específicos**

### **Detección Mejorada con LLM**

**Entrada:**
```
"Se revisa EQUIPO MARCA_NUEVA MOD. MODELO_RARO con problemas"
```

**Heurístico solo:**
- Puede no detectar "MARCA_NUEVA" si no coincide con patrones

**Con LLM Local:**
- Analiza contexto: "EQUIPO" + "MOD." → Probablemente marca/modelo
- Valida si "MARCA_NUEVA" es fabricante conocido
- Sugiere sinónimos y variaciones

### **Validación Contextual**

**LLM evalúa:**
```json
{
  "candidate": "FABRICANTE_DESCONOCIDO",
  "context": "reparación de laminadora",
  "llm_decision": "rechazar - no es fabricante conocido",
  "confidence": 0.95
}
```

## 🎯 **Configuración Recomendada para Producción**

```bash
# .env - Configuración optimizada
LLM_AGENTS='{
  "taxonomy": {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "sk-local",
    "temperature": 0.1,
    "max_tokens": 1000
  },
  "prediction": {
    "model": "mistral:7b",
    "base_url": "http://localhost:11434/v1", 
    "api_key": "sk-local",
    "temperature": 0.2,
    "max_tokens": 800
  },
  "router": {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "sk-local",
    "temperature": 0.0,
    "max_tokens": 200
  }
}'

# Hardware mínimo recomendado
# - RAM: 16GB (para llama3.1:8b)
# - CPU: 8+ cores
# - GPU: Opcional (acelera procesamiento)
```

**¡El sistema está listo para LLM local sin cambios de código!** 🚀
