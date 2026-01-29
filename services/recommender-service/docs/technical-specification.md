# 🔧 Recommender Service - Especificaciones Técnicas

## 🏗️ **Arquitectura Técnica Detallada**

### **📦 Estructura del Servicio**

```
services/recommender-service/
├── main.py                         # FastAPI application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Service orchestration
├── env.example                     # Environment template
├── 
├── core/                           # Core business logic
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database connections
│   ├── cache.py                    # Redis cache layer
│   └── exceptions.py               # Custom exceptions
│
├── engines/                        # Recommendation engines
│   ├── __init__.py
│   ├── questionnaire_engine.py     # Dynamic questionnaire generation
│   ├── requirements_analyzer.py    # Client requirements analysis
│   ├── product_matcher.py          # Product matching algorithms
│   ├── ranking_engine.py           # Product ranking and scoring
│   └── llm_integration.py          # LLM service integration
│
├── models/                         # Data models
│   ├── __init__.py
│   ├── session.py                  # Recommendation session models
│   ├── questionnaire.py            # Question and answer models
│   ├── client.py                   # Client profile models
│   ├── product.py                  # Product and recommendation models
│   ├── analytics.py                # Analytics and metrics models
│   └── requests.py                 # API request models
│   └── responses.py                # API response models
│
├── services/                       # External service integrations
│   ├── __init__.py
│   ├── kb_service.py               # Knowledge Base integration
│   ├── llm_service.py              # LLM API client
│   ├── product_service.py          # Product database service
│   ├── vendor_service.py           # Vendor API integrations
│   └── analytics_service.py        # Analytics collection
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── scoring.py                  # Scoring algorithms
│   ├── matching.py                 # Matching utilities
│   ├── validation.py               # Input validation
│   ├── formatting.py               # Data formatting
│   └── business_rules.py           # Business logic rules
│
├── config/                         # Configuration files
│   ├── business_types/             # Business type configurations
│   │   ├── bakery.json
│   │   ├── restaurant.json
│   │   ├── cafe.json
│   │   └── pizzeria.json
│   ├── questionnaire_templates/    # Question templates
│   ├── scoring_weights.json        # Scoring configuration
│   └── llm_prompts.json            # LLM prompt templates
│
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── fixtures/                   # Test data
│   └── conftest.py                 # Test configuration
│
├── docs/                           # Documentation
│   ├── api-reference.md
│   ├── recommendation-algorithms.md
│   ├── business-type-configs.md
│   ├── llm-integration.md
│   └── deployment.md
│
└── scripts/                        # Utility scripts
    ├── setup_database.py
    ├── seed_data.py
    ├── migrate_data.py
    └── performance_test.py
```

---

## 🗄️ **Esquema de Base de Datos**

### **📊 Tablas Principales**

```sql
-- Sesiones de recomendación
CREATE TABLE recommendation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    anonymous_id VARCHAR(255),
    business_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    current_step VARCHAR(50),
    completion_percentage INTEGER DEFAULT 0,
    client_profile JSONB,
    requirements JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    session_duration_minutes INTEGER
);

-- Progreso del cuestionario
CREATE TABLE questionnaire_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES recommendation_sessions(id),
    current_question_id VARCHAR(100),
    questions_answered JSONB DEFAULT '[]',
    questions_remaining JSONB DEFAULT '[]',
    completion_percentage INTEGER DEFAULT 0,
    estimated_time_remaining INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Preguntas y respuestas
CREATE TABLE questions (
    id VARCHAR(100) PRIMARY KEY,
    business_type VARCHAR(50),
    category VARCHAR(50),
    type VARCHAR(30),
    text TEXT NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 0,
    validation_rules JSONB,
    answer_options JSONB,
    input_config JSONB,
    dependencies JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE question_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES recommendation_sessions(id),
    question_id VARCHAR(100) REFERENCES questions(id),
    answer JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    time_spent_seconds INTEGER,
    answered_at TIMESTAMP DEFAULT NOW()
);

-- Productos y especificaciones
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(100),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    description TEXT,
    specifications JSONB,
    features JSONB DEFAULT '[]',
    images JSONB DEFAULT '[]',
    documents JSONB DEFAULT '[]',
    manufacturer_info JSONB,
    certifications JSONB DEFAULT '[]',
    warranty_info JSONB,
    rating DECIMAL(2,1),
    review_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Información de precios
CREATE TABLE product_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    base_price DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'MXN',
    price_includes JSONB DEFAULT '[]',
    additional_costs JSONB DEFAULT '[]',
    financing_options JSONB DEFAULT '[]',
    price_valid_until DATE,
    vendor_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Recomendaciones generadas
CREATE TABLE product_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES recommendation_sessions(id),
    product_id UUID REFERENCES products(id),
    rank INTEGER,
    relevance_score DECIMAL(5,2),
    confidence_score DECIMAL(5,2),
    requirement_matches JSONB,
    pros JSONB DEFAULT '[]',
    cons JSONB DEFAULT '[]',
    reasoning JSONB,
    business_impact JSONB,
    recommendation_source VARCHAR(50),
    recommended_at TIMESTAMP DEFAULT NOW()
);

-- Feedback de usuarios
CREATE TABLE recommendation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES recommendation_sessions(id),
    product_id UUID REFERENCES products(id),
    feedback_type VARCHAR(30),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    specific_concerns JSONB DEFAULT '[]',
    likely_to_purchase VARCHAR(20),
    purchase_timeline VARCHAR(30),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics y métricas
CREATE TABLE session_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES recommendation_sessions(id),
    event_type VARCHAR(50),
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Configuraciones por tipo de negocio
CREATE TABLE business_type_configs (
    business_type VARCHAR(50) PRIMARY KEY,
    questionnaire_template JSONB,
    equipment_categories JSONB,
    success_metrics JSONB,
    industry_benchmarks JSONB,
    scoring_weights JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **🔍 Índices para Performance**

```sql
-- Índices para consultas frecuentes
CREATE INDEX idx_sessions_user_id ON recommendation_sessions(user_id);
CREATE INDEX idx_sessions_status ON recommendation_sessions(status);
CREATE INDEX idx_sessions_business_type ON recommendation_sessions(business_type);
CREATE INDEX idx_sessions_created_at ON recommendation_sessions(created_at);

CREATE INDEX idx_questions_business_type ON questions(business_type);
CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_priority ON questions(priority);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_rating ON products(rating);

CREATE INDEX idx_recommendations_session_id ON product_recommendations(session_id);
CREATE INDEX idx_recommendations_product_id ON product_recommendations(product_id);
CREATE INDEX idx_recommendations_rank ON product_recommendations(rank);

-- Índices GIN para búsquedas en JSONB
CREATE INDEX idx_sessions_client_profile_gin ON recommendation_sessions USING GIN(client_profile);
CREATE INDEX idx_sessions_requirements_gin ON recommendation_sessions USING GIN(requirements);
CREATE INDEX idx_products_specifications_gin ON products USING GIN(specifications);
CREATE INDEX idx_products_features_gin ON products USING GIN(features);
```

---

## 🤖 **Integración con LLM**

### **📝 Prompts Especializados**

```python
# config/llm_prompts.json
{
  "questionnaire_generation": {
    "system_prompt": """
Eres un experto consultor en equipamiento industrial especializado en {business_type}.
Tu tarea es generar preguntas inteligentes y específicas para entender las necesidades del cliente.

Contexto del negocio:
- Tipo: {business_type}
- Sector: {industry_sector}
- Información previa: {previous_answers}

Genera la siguiente pregunta más relevante considerando:
1. Información crítica que aún falta
2. Especificidad del sector
3. Impacto en las recomendaciones de equipos
4. Facilidad de respuesta para el cliente

Formato de respuesta:
{
  "question": {
    "text": "Pregunta clara y específica",
    "type": "single_choice|multiple_choice|numeric_input|text_input",
    "options": ["opción1", "opción2"] // si aplica
    "help_text": "Explicación breve de por qué es importante",
    "validation": {...} // reglas de validación
  },
  "reasoning": "Por qué esta pregunta es la más importante ahora",
  "expected_impact": "Cómo afectará las recomendaciones"
}
""",
    
    "user_prompt": """
Información actual del cliente:
{client_profile}

Respuestas previas:
{previous_answers}

Genera la siguiente pregunta más importante para completar el perfil.
"""
  },
  
  "requirements_analysis": {
    "system_prompt": """
Eres un analista experto en requerimientos de equipamiento industrial.
Analiza las respuestas del cliente para extraer requerimientos técnicos y funcionales específicos.

Tu análisis debe incluir:
1. Requerimientos funcionales (qué debe hacer el equipo)
2. Restricciones técnicas (especificaciones mínimas/máximas)
3. Limitaciones operativas (espacio, presupuesto, tiempo)
4. Prioridades del negocio

Formato de respuesta:
{
  "functional_requirements": [
    {
      "category": "production|storage|preparation|cooking",
      "description": "Descripción específica",
      "importance": "critical|high|medium|low",
      "quantitative_target": "valor específico si aplica"
    }
  ],
  "technical_requirements": [
    {
      "specification": "capacidad|potencia|dimensiones|temperatura",
      "min_value": number,
      "max_value": number,
      "unit": "kg|kw|cm|celsius",
      "is_mandatory": true|false
    }
  ],
  "constraints": [
    {
      "type": "budget|space|power|time",
      "description": "Descripción de la limitación",
      "hard_constraint": true|false
    }
  ],
  "priorities": [
    {
      "factor": "cost|efficiency|quality|speed|reliability",
      "weight": 1-5,
      "reasoning": "Por qué es importante"
    }
  ]
}
""",
    
    "user_prompt": """
Perfil del cliente:
{client_profile}

Respuestas del cuestionario:
{questionnaire_answers}

Analiza y extrae los requerimientos específicos para recomendar equipamiento.
"""
  },
  
  "product_matching": {
    "system_prompt": """
Eres un experto en equipamiento industrial que evalúa qué tan bien un producto específico
satisface los requerimientos de un cliente.

Evalúa considerando:
1. Cumplimiento de requerimientos funcionales
2. Compatibilidad técnica
3. Adecuación al presupuesto
4. Facilidad de implementación
5. Retorno de inversión

Formato de respuesta:
{
  "overall_match_score": 0-100,
  "functional_match": 0-100,
  "technical_compatibility": 0-100,
  "budget_fit": 0-100,
  "implementation_ease": 0-100,
  
  "pros": [
    {
      "point": "Ventaja específica",
      "impact": "high|medium|low",
      "category": "functionality|cost|efficiency|reliability"
    }
  ],
  "cons": [
    {
      "point": "Desventaja o limitación",
      "impact": "high|medium|low",
      "mitigation": "Cómo se puede mitigar si es posible"
    }
  ],
  "requirement_satisfaction": [
    {
      "requirement_id": "ID del requerimiento",
      "satisfaction_level": 0-100,
      "explanation": "Cómo y qué tan bien lo cumple"
    }
  ]
}
""",
    
    "user_prompt": """
Requerimientos del cliente:
{client_requirements}

Producto a evaluar:
{product_details}

Evalúa qué tan bien este producto satisface las necesidades del cliente.
"""
  },
  
  "reasoning_generation": {
    "system_prompt": """
Eres un consultor experto que explica de manera clara y convincente por qué
un producto específico es recomendado para un cliente.

Tu explicación debe:
1. Ser clara y fácil de entender
2. Conectar características del producto con necesidades del cliente
3. Incluir beneficios cuantificables cuando sea posible
4. Ser honesta sobre limitaciones
5. Justificar la inversión

Formato de respuesta:
{
  "primary_reasons": [
    "Razón principal 1",
    "Razón principal 2",
    "Razón principal 3"
  ],
  "detailed_explanation": "Explicación detallada de por qué es la mejor opción",
  "business_benefits": [
    {
      "benefit": "Beneficio específico",
      "quantification": "Valor cuantificado si es posible",
      "timeline": "Cuándo se verá el beneficio"
    }
  ],
  "implementation_notes": "Consideraciones importantes para la implementación",
  "roi_summary": "Resumen del retorno de inversión esperado"
}
""",
    
    "user_prompt": """
Cliente:
{client_profile}

Requerimientos:
{client_requirements}

Producto recomendado:
{recommended_product}

Puntuación de match:
{match_scores}

Genera una explicación convincente de por qué este producto es ideal para este cliente.
"""
  }
}
```

### **🔧 Cliente LLM**

```python
# engines/llm_integration.py
import asyncio
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from core.config import RecommenderConfig

class LLMService:
    def __init__(self, config: RecommenderConfig):
        self.config = config
        self.client = AsyncOpenAI(api_key=config.llm_api_key)
        self.prompts = self._load_prompts()
    
    async def generate_next_question(
        self,
        business_type: str,
        client_profile: Dict[str, Any],
        previous_answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generar siguiente pregunta adaptativa"""
        
        system_prompt = self.prompts["questionnaire_generation"]["system_prompt"].format(
            business_type=business_type,
            industry_sector=client_profile.get("industry_sector", ""),
            previous_answers=json.dumps(previous_answers, indent=2)
        )
        
        user_prompt = self.prompts["questionnaire_generation"]["user_prompt"].format(
            client_profile=json.dumps(client_profile, indent=2),
            previous_answers=json.dumps(previous_answers, indent=2)
        )
        
        response = await self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def analyze_requirements(
        self,
        client_profile: Dict[str, Any],
        questionnaire_answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analizar requerimientos del cliente"""
        
        system_prompt = self.prompts["requirements_analysis"]["system_prompt"]
        user_prompt = self.prompts["requirements_analysis"]["user_prompt"].format(
            client_profile=json.dumps(client_profile, indent=2),
            questionnaire_answers=json.dumps(questionnaire_answers, indent=2)
        )
        
        response = await self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def evaluate_product_match(
        self,
        client_requirements: Dict[str, Any],
        product_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluar qué tan bien un producto satisface los requerimientos"""
        
        system_prompt = self.prompts["product_matching"]["system_prompt"]
        user_prompt = self.prompts["product_matching"]["user_prompt"].format(
            client_requirements=json.dumps(client_requirements, indent=2),
            product_details=json.dumps(product_details, indent=2)
        )
        
        response = await self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def generate_recommendation_reasoning(
        self,
        client_profile: Dict[str, Any],
        client_requirements: Dict[str, Any],
        recommended_product: Dict[str, Any],
        match_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generar explicación de por qué se recomienda un producto"""
        
        system_prompt = self.prompts["reasoning_generation"]["system_prompt"]
        user_prompt = self.prompts["reasoning_generation"]["user_prompt"].format(
            client_profile=json.dumps(client_profile, indent=2),
            client_requirements=json.dumps(client_requirements, indent=2),
            recommended_product=json.dumps(recommended_product, indent=2),
            match_scores=json.dumps(match_scores, indent=2)
        )
        
        response = await self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Cargar prompts desde archivo de configuración"""
        with open("config/llm_prompts.json", "r", encoding="utf-8") as f:
            return json.load(f)
```

---

## 🎯 **Algoritmos de Scoring**

### **📊 Motor de Puntuación Multi-dimensional**

```python
# utils/scoring.py
from typing import Dict, List, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class ScoringWeights:
    functional_match: float = 0.30
    technical_compatibility: float = 0.25
    budget_fit: float = 0.20
    vendor_reliability: float = 0.10
    user_reviews: float = 0.10
    market_position: float = 0.05

class ProductScorer:
    def __init__(self, weights: ScoringWeights = None):
        self.weights = weights or ScoringWeights()
    
    def calculate_overall_score(
        self,
        functional_score: float,
        technical_score: float,
        budget_score: float,
        vendor_score: float,
        review_score: float,
        market_score: float
    ) -> float:
        """Calcular puntuación general ponderada"""
        
        scores = {
            'functional': functional_score,
            'technical': technical_score,
            'budget': budget_score,
            'vendor': vendor_score,
            'reviews': review_score,
            'market': market_score
        }
        
        # Normalizar scores a 0-100
        normalized_scores = {k: max(0, min(100, v)) for k, v in scores.items()}
        
        overall_score = (
            normalized_scores['functional'] * self.weights.functional_match +
            normalized_scores['technical'] * self.weights.technical_compatibility +
            normalized_scores['budget'] * self.weights.budget_fit +
            normalized_scores['vendor'] * self.weights.vendor_reliability +
            normalized_scores['reviews'] * self.weights.user_reviews +
            normalized_scores['market'] * self.weights.market_position
        )
        
        return round(overall_score, 2)
    
    def calculate_functional_score(
        self,
        requirements: List[Dict[str, Any]],
        product_capabilities: Dict[str, Any]
    ) -> float:
        """Calcular score de cumplimiento funcional"""
        
        total_weight = 0
        weighted_score = 0
        
        for req in requirements:
            importance_weight = self._get_importance_weight(req['importance'])
            satisfaction = self._evaluate_requirement_satisfaction(req, product_capabilities)
            
            weighted_score += satisfaction * importance_weight
            total_weight += importance_weight
        
        return (weighted_score / total_weight * 100) if total_weight > 0 else 0
    
    def calculate_technical_score(
        self,
        technical_requirements: List[Dict[str, Any]],
        product_specs: Dict[str, Any]
    ) -> float:
        """Calcular score de compatibilidad técnica"""
        
        compatibility_scores = []
        
        for tech_req in technical_requirements:
            spec_name = tech_req['specification']
            
            if spec_name not in product_specs:
                # Especificación no disponible
                score = 0 if tech_req['is_mandatory'] else 50
            else:
                score = self._evaluate_technical_compatibility(tech_req, product_specs[spec_name])
            
            compatibility_scores.append(score)
        
        return np.mean(compatibility_scores) if compatibility_scores else 0
    
    def calculate_budget_score(
        self,
        budget_range: Dict[str, float],
        product_pricing: Dict[str, Any]
    ) -> float:
        """Calcular score de ajuste presupuestal"""
        
        total_cost = self._calculate_total_cost_of_ownership(product_pricing)
        min_budget = budget_range['min_budget']
        max_budget = budget_range['max_budget']
        
        if total_cost <= max_budget:
            # Dentro del presupuesto
            if total_cost <= min_budget:
                return 100  # Muy económico
            else:
                # Escala lineal entre min y max
                ratio = (max_budget - total_cost) / (max_budget - min_budget)
                return 60 + (ratio * 40)  # 60-100 range
        else:
            # Fuera del presupuesto
            excess_ratio = (total_cost - max_budget) / max_budget
            penalty = min(60, excess_ratio * 100)  # Máximo 60 puntos de penalización
            return max(0, 60 - penalty)
    
    def _get_importance_weight(self, importance: str) -> float:
        """Convertir importancia a peso numérico"""
        weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        return weights.get(importance, 0.6)
    
    def _evaluate_requirement_satisfaction(
        self,
        requirement: Dict[str, Any],
        capabilities: Dict[str, Any]
    ) -> float:
        """Evaluar qué tan bien se satisface un requerimiento"""
        
        req_category = requirement['category']
        req_description = requirement['description']
        
        # Lógica específica por categoría
        if req_category == 'production':
            return self._evaluate_production_requirement(requirement, capabilities)
        elif req_category == 'storage':
            return self._evaluate_storage_requirement(requirement, capabilities)
        # ... más categorías
        
        # Evaluación genérica basada en descripción
        return self._generic_requirement_evaluation(req_description, capabilities)
    
    def _evaluate_technical_compatibility(
        self,
        tech_req: Dict[str, Any],
        product_value: Any
    ) -> float:
        """Evaluar compatibilidad técnica específica"""
        
        min_val = tech_req.get('min_value')
        max_val = tech_req.get('max_value')
        preferred_val = tech_req.get('preferred_value')
        
        if isinstance(product_value, (int, float)):
            # Valor numérico
            if min_val is not None and product_value < min_val:
                return 0  # No cumple mínimo
            
            if max_val is not None and product_value > max_val:
                return 0  # Excede máximo
            
            if preferred_val is not None:
                # Calcular qué tan cerca está del valor preferido
                if min_val is not None and max_val is not None:
                    range_size = max_val - min_val
                    distance = abs(product_value - preferred_val)
                    normalized_distance = distance / range_size
                    return max(0, 100 - (normalized_distance * 100))
                else:
                    return 100  # Cumple y no hay rango definido
            
            return 100  # Cumple los rangos
        
        # Valor no numérico, evaluación booleana
        return 100 if product_value else 0
    
    def _calculate_total_cost_of_ownership(self, pricing: Dict[str, Any]) -> float:
        """Calcular costo total de propiedad"""
        
        base_cost = pricing.get('base_price', 0)
        
        # Costos adicionales
        additional_costs = pricing.get('additional_costs', [])
        total_additional = sum(cost.get('cost', 0) for cost in additional_costs)
        
        # Costos recurrentes (estimados a 3 años)
        recurring_costs = sum(
            cost.get('cost', 0) * 3 
            for cost in additional_costs 
            if cost.get('is_recurring', False)
        )
        
        return base_cost + total_additional + recurring_costs
```

---

## 🔄 **Sistema de Cache**

### **⚡ Redis Cache Layer**

```python
# core/cache.py
import json
import asyncio
from typing import Any, Optional, Dict
import redis.asyncio as redis
from core.config import RecommenderConfig

class CacheService:
    def __init__(self, config: RecommenderConfig):
        self.redis = redis.from_url(config.redis_url)
        self.default_ttl = config.cache_ttl_seconds
    
    async def get_session_cache(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtener cache de sesión"""
        key = f"session:{session_id}"
        cached_data = await self.redis.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_session_cache(
        self, 
        session_id: str, 
        data: Dict[str, Any], 
        ttl: int = None
    ) -> None:
        """Guardar cache de sesión"""
        key = f"session:{session_id}"
        ttl = ttl or self.default_ttl
        
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(data, default=str)
        )
    
    async def get_product_cache(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Obtener cache de producto"""
        key = f"product:{product_id}"
        cached_data = await self.redis.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_product_cache(
        self, 
        product_id: str, 
        data: Dict[str, Any], 
        ttl: int = 86400  # 24 horas
    ) -> None:
        """Guardar cache de producto"""
        key = f"product:{product_id}"
        
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(data, default=str)
        )
    
    async def get_recommendations_cache(
        self, 
        requirements_hash: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Obtener recomendaciones cacheadas por hash de requerimientos"""
        key = f"recommendations:{requirements_hash}"
        cached_data = await self.redis.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_recommendations_cache(
        self, 
        requirements_hash: str, 
        recommendations: List[Dict[str, Any]], 
        ttl: int = 3600  # 1 hora
    ) -> None:
        """Guardar recomendaciones en cache"""
        key = f"recommendations:{requirements_hash}"
        
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(recommendations, default=str)
        )
    
    async def invalidate_session(self, session_id: str) -> None:
        """Invalidar cache de sesión"""
        key = f"session:{session_id}"
        await self.redis.delete(key)
    
    async def get_business_config_cache(self, business_type: str) -> Optional[Dict[str, Any]]:
        """Obtener configuración de tipo de negocio desde cache"""
        key = f"business_config:{business_type}"
        cached_data = await self.redis.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_business_config_cache(
        self, 
        business_type: str, 
        config: Dict[str, Any]
    ) -> None:
        """Guardar configuración de tipo de negocio en cache"""
        key = f"business_config:{business_type}"
        
        # Cache por 24 horas
        await self.redis.setex(
            key, 
            86400, 
            json.dumps(config, default=str)
        )
```

---

## 📊 **Sistema de Analytics**

### **📈 Recolección de Métricas**

```python
# services/analytics_service.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import text
from core.database import get_database

class AnalyticsService:
    def __init__(self):
        self.db = get_database()
    
    async def track_session_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Registrar evento de sesión"""
        
        query = """
        INSERT INTO session_analytics (session_id, event_type, event_data)
        VALUES (:session_id, :event_type, :event_data)
        """
        
        await self.db.execute(
            text(query),
            {
                "session_id": session_id,
                "event_type": event_type,
                "event_data": event_data
            }
        )
    
    async def get_session_metrics(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas de sesiones"""
        
        query = """
        SELECT 
            COUNT(*) as total_sessions,
            COUNT(*) FILTER (WHERE status = 'completed') as completed_sessions,
            COUNT(*) FILTER (WHERE status = 'abandoned') as abandoned_sessions,
            AVG(session_duration_minutes) as avg_duration,
            AVG(completion_percentage) as avg_completion_rate
        FROM recommendation_sessions
        WHERE created_at BETWEEN :date_from AND :date_to
        """
        
        result = await self.db.fetch_one(
            text(query),
            {"date_from": date_from, "date_to": date_to}
        )
        
        return dict(result) if result else {}
    
    async def get_questionnaire_metrics(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas del cuestionario"""
        
        # Promedio de preguntas por sesión
        avg_questions_query = """
        SELECT AVG(question_count) as avg_questions_per_session
        FROM (
            SELECT session_id, COUNT(*) as question_count
            FROM question_answers qa
            JOIN recommendation_sessions rs ON qa.session_id = rs.id
            WHERE rs.created_at BETWEEN :date_from AND :date_to
            GROUP BY session_id
        ) subq
        """
        
        # Tiempo promedio por pregunta
        avg_time_query = """
        SELECT AVG(time_spent_seconds) as avg_time_per_question
        FROM question_answers qa
        JOIN recommendation_sessions rs ON qa.session_id = rs.id
        WHERE rs.created_at BETWEEN :date_from AND :date_to
        """
        
        avg_questions = await self.db.fetch_one(
            text(avg_questions_query),
            {"date_from": date_from, "date_to": date_to}
        )
        
        avg_time = await self.db.fetch_one(
            text(avg_time_query),
            {"date_from": date_from, "date_to": date_to}
        )
        
        return {
            "avg_questions_per_session": avg_questions[0] if avg_questions else 0,
            "avg_time_per_question": avg_time[0] if avg_time else 0
        }
    
    async def get_recommendation_metrics(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas de recomendaciones"""
        
        query = """
        SELECT 
            AVG(recommendations_count) as avg_recommendations_per_session,
            AVG(relevance_score) as avg_relevance_score,
            AVG(confidence_score) as avg_confidence_score
        FROM (
            SELECT 
                session_id,
                COUNT(*) as recommendations_count,
                AVG(relevance_score) as relevance_score,
                AVG(confidence_score) as confidence_score
            FROM product_recommendations pr
            JOIN recommendation_sessions rs ON pr.session_id = rs.id
            WHERE rs.created_at BETWEEN :date_from AND :date_to
            GROUP BY session_id
        ) subq
        """
        
        result = await self.db.fetch_one(
            text(query),
            {"date_from": date_from, "date_to": date_to}
        )
        
        return dict(result) if result else {}
    
    async def get_feedback_metrics(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas de feedback"""
        
        query = """
        SELECT 
            COUNT(*) as total_feedback,
            AVG(rating) as avg_rating,
            COUNT(*) FILTER (WHERE likely_to_purchase = 'very_likely') as very_likely_purchase,
            COUNT(*) FILTER (WHERE likely_to_purchase = 'likely') as likely_purchase,
            COUNT(*) FILTER (WHERE likely_to_purchase = 'unlikely') as unlikely_purchase
        FROM recommendation_feedback rf
        WHERE rf.created_at BETWEEN :date_from AND :date_to
        """
        
        result = await self.db.fetch_one(
            text(query),
            {"date_from": date_from, "date_to": date_to}
        )
        
        return dict(result) if result else {}
    
    async def get_business_type_performance(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> List[Dict[str, Any]]:
        """Obtener performance por tipo de negocio"""
        
        query = """
        SELECT 
            business_type,
            COUNT(*) as total_sessions,
            AVG(completion_percentage) as avg_completion_rate,
            AVG(session_duration_minutes) as avg_duration,
            COUNT(*) FILTER (WHERE status = 'completed') as completed_sessions
        FROM recommendation_sessions
        WHERE created_at BETWEEN :date_from AND :date_to
        GROUP BY business_type
        ORDER BY total_sessions DESC
        """
        
        results = await self.db.fetch_all(
            text(query),
            {"date_from": date_from, "date_to": date_to}
        )
        
        return [dict(row) for row in results]
```

---

## 🧪 **Testing Strategy**

### **📋 Suite de Tests**

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from main import app
from core.database import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Test client for API calls"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    """Test database session"""
    # Setup test database
    # ... database setup code
    yield session
    # Cleanup

@pytest.fixture
def sample_client_profile():
    """Sample client profile for testing"""
    return {
        "business_type": "bakery",
        "company_size": "small",
        "location": {"city": "Mexico City", "country": "Mexico"},
        "business_details": {
            "daily_bread_production_kg": 50,
            "bread_types": ["artisan", "sourdough"],
            "has_pastry_section": True
        }
    }

@pytest.fixture
def sample_requirements():
    """Sample requirements for testing"""
    return {
        "functional_requirements": [
            {
                "category": "production",
                "description": "Amasado eficiente para masa madre",
                "importance": "critical"
            }
        ],
        "technical_requirements": [
            {
                "specification": "capacity",
                "min_value": 25,
                "max_value": 75,
                "unit": "kg",
                "is_mandatory": True
            }
        ]
    }
```

```python
# tests/unit/test_scoring.py
import pytest
from utils.scoring import ProductScorer, ScoringWeights

class TestProductScorer:
    def test_calculate_overall_score(self):
        """Test overall score calculation"""
        scorer = ProductScorer()
        
        score = scorer.calculate_overall_score(
            functional_score=90,
            technical_score=85,
            budget_score=70,
            vendor_score=80,
            review_score=88,
            market_score=75
        )
        
        # Should be weighted average
        expected = (90*0.30 + 85*0.25 + 70*0.20 + 80*0.10 + 88*0.10 + 75*0.05)
        assert abs(score - expected) < 0.1
    
    def test_functional_score_calculation(self, sample_requirements):
        """Test functional score calculation"""
        scorer = ProductScorer()
        
        product_capabilities = {
            "mixing_efficiency": "high",
            "capacity_kg": 50,
            "sourdough_compatibility": True
        }
        
        score = scorer.calculate_functional_score(
            sample_requirements["functional_requirements"],
            product_capabilities
        )
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
```

```python
# tests/integration/test_recommendation_flow.py
import pytest
from httpx import AsyncClient

class TestRecommendationFlow:
    async def test_complete_recommendation_flow(self, client: AsyncClient):
        """Test complete recommendation flow"""
        
        # 1. Create session
        response = await client.post("/api/v1/recommendations/sessions", json={
            "business_type": "bakery",
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        session_data = response.json()
        session_id = session_data["session_id"]
        
        # 2. Answer questions
        for i in range(3):  # Answer 3 questions
            # Get next question
            response = await client.get(f"/api/v1/questionnaire/next-question/{session_id}")
            assert response.status_code == 200
            
            question_data = response.json()
            question_id = question_data["question"]["id"]
            
            # Answer question
            answer_response = await client.post("/api/v1/questionnaire/answer", json={
                "session_id": session_id,
                "question_id": question_id,
                "answer": {
                    "type": "numeric_input",
                    "value": 50
                }
            })
            assert answer_response.status_code == 200
        
        # 3. Generate recommendations
        response = await client.post("/api/v1/recommendations/generate", json={
            "session_id": session_id
        })
        
        assert response.status_code == 200
        recommendations = response.json()
        
        assert "recommendations" in recommendations
        assert len(recommendations["recommendations"]) > 0
        
        # Verify recommendation structure
        rec = recommendations["recommendations"][0]
        assert "product" in rec
        assert "scores" in rec
        assert "reasoning" in rec
```

---

## 🚀 **Deployment Configuration**

### **🐳 Docker Configuration**

```dockerfile
# Dockerfile
FROM python:3.11-slim

LABEL maintainer="FixeatAI Team"
LABEL service="recommender-service"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV RECOMMENDER_SERVICE_PORT=8070

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 recommender && \
    mkdir -p /app /app/logs /app/data && \
    chown -R recommender:recommender /app

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R recommender:recommender /app

# Switch to non-root user
USER recommender

# Expose port
EXPOSE 8070

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8070/health || exit 1

# Command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8070"]
```

```yaml
# docker-compose.yml
version: "3.9"

services:
  recommender-service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: recommender-service
    restart: unless-stopped
    ports:
      - "${RECOMMENDER_SERVICE_PORT:-8070}:8070"
    environment:
      # Service configuration
      - RECOMMENDER_SERVICE_PORT=8070
      - RECOMMENDER_LOG_LEVEL=${RECOMMENDER_LOG_LEVEL:-info}
      
      # LLM configuration
      - RECOMMENDER_LLM_PROVIDER=${RECOMMENDER_LLM_PROVIDER:-openai}
      - RECOMMENDER_LLM_API_KEY=${RECOMMENDER_LLM_API_KEY}
      - RECOMMENDER_LLM_MODEL=${RECOMMENDER_LLM_MODEL:-gpt-4o}
      
      # Database
      - RECOMMENDER_DB_HOST=recommender-db
      - RECOMMENDER_DB_NAME=${RECOMMENDER_DB_NAME:-recommender_db}
      - RECOMMENDER_DB_USER=${RECOMMENDER_DB_USER:-recommender}
      - RECOMMENDER_DB_PASSWORD=${RECOMMENDER_DB_PASSWORD}
      
      # Cache
      - RECOMMENDER_REDIS_URL=redis://recommender-redis:6379/2
      
      # Knowledge Base
      - RECOMMENDER_KB_URL=${RECOMMENDER_KB_URL}
      
    volumes:
      - recommender-logs:/app/logs
      - recommender-data:/app/data
      
    networks:
      - recommender-network
      
    depends_on:
      - recommender-db
      - recommender-redis
      
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8070/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  recommender-db:
    image: postgres:15-alpine
    container_name: recommender-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${RECOMMENDER_DB_NAME:-recommender_db}
      - POSTGRES_USER=${RECOMMENDER_DB_USER:-recommender}
      - POSTGRES_PASSWORD=${RECOMMENDER_DB_PASSWORD}
    volumes:
      - recommender-db-data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - recommender-network

  recommender-redis:
    image: redis:7-alpine
    container_name: recommender-redis
    restart: unless-stopped
    volumes:
      - recommender-redis-data:/data
    networks:
      - recommender-network

volumes:
  recommender-logs:
  recommender-data:
  recommender-db-data:
  recommender-redis-data:

networks:
  recommender-network:
    driver: bridge
```

---

**Esta especificación técnica completa proporciona todos los detalles necesarios para implementar el Recommender Service con las mejores prácticas de desarrollo, testing y deployment.** 🔧📋


