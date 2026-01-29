/**
 * Fixeat Widget - Embeddable AI Recommendation Chat
 * Version: 1.0.0
 * 
 * Insertable widget that automatically detects business type
 * and provides intelligent equipment recommendations
 */

(function(window, document) {
  'use strict';
  
  // Verificar si ya está cargado
  if (window.FixeatWidget) {
    console.warn('[Fixeat Widget] Widget already loaded');
    return;
  }
  
  // Constantes
  const WIDGET_VERSION = '1.0.0';
  const API_BASE_URL = 'https://api.fixeat.ai/v1';
  const CDN_BASE_URL = 'https://cdn.fixeat.ai/widget/v1';
  
  /**
   * Cliente API para comunicación con Recommender Service
   */
  class FixeatAPIClient {
    constructor(config) {
      this.config = config;
      this.apiUrl = config.apiUrl || API_BASE_URL;
      this.headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Widget-Version': WIDGET_VERSION
      };
    }
    
    async createSession(data) {
      try {
        const response = await fetch(`${this.apiUrl}/recommendations/sessions`, {
          method: 'POST',
          headers: this.headers,
          body: JSON.stringify({
            business_type: data.businessType,
            user_id: data.userId || null,
            anonymous_id: this.generateAnonymousId(),
            initial_context: {
              page_url: window.location.href,
              page_title: document.title,
              detected_business: data.detectionData,
              widget_version: WIDGET_VERSION
            }
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result.data || result;
        
      } catch (error) {
        console.error('[Fixeat API] Create session failed:', error);
        throw error;
      }
    }
    
    async sendMessage(sessionId, message) {
      try {
        const response = await fetch(`${this.apiUrl}/questionnaire/answer`, {
          method: 'POST',
          headers: this.headers,
          body: JSON.stringify({
            session_id: sessionId,
            message: message,
            timestamp: new Date().toISOString()
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result.data || result;
        
      } catch (error) {
        console.error('[Fixeat API] Send message failed:', error);
        throw error;
      }
    }
    
    async getNextQuestion(sessionId) {
      try {
        const response = await fetch(`${this.apiUrl}/questionnaire/next-question/${sessionId}`, {
          headers: this.headers
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result.data || result;
        
      } catch (error) {
        console.error('[Fixeat API] Get next question failed:', error);
        throw error;
      }
    }
    
    async generateRecommendations(sessionId, preferences = {}) {
      try {
        const response = await fetch(`${this.apiUrl}/recommendations/generate`, {
          method: 'POST',
          headers: this.headers,
          body: JSON.stringify({
            session_id: sessionId,
            preferences: {
              max_recommendations: 5,
              include_alternatives: true,
              ...preferences
            }
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result.data || result;
        
      } catch (error) {
        console.error('[Fixeat API] Generate recommendations failed:', error);
        throw error;
      }
    }
    
    async sendAnalytics(events) {
      try {
        await fetch(`${this.apiUrl}/analytics/widget-events`, {
          method: 'POST',
          headers: this.headers,
          body: JSON.stringify({ events })
        });
      } catch (error) {
        console.warn('[Fixeat API] Analytics failed:', error);
      }
    }
    
    generateAnonymousId() {
      return 'anon_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
  }
  
  /**
   * Detector de tipo de negocio basado en contenido del sitio
   */
  class BusinessDetector {
    constructor() {
      this.keywords = {
        bakery: {
          es: ['pan', 'panadería', 'horno', 'masa', 'levadura', 'pastelería', 'croissant', 'baguette', 'integral', 'artesanal'],
          en: ['bread', 'bakery', 'oven', 'dough', 'yeast', 'pastry', 'croissant', 'baguette', 'sourdough', 'artisan']
        },
        restaurant: {
          es: ['restaurante', 'menú', 'carta', 'cocina', 'chef', 'comida', 'platos', 'gastronomía', 'cena', 'almuerzo'],
          en: ['restaurant', 'menu', 'kitchen', 'chef', 'food', 'dishes', 'cuisine', 'dining', 'dinner', 'lunch']
        },
        cafe: {
          es: ['café', 'cafetería', 'espresso', 'cappuccino', 'barista', 'bebidas', 'desayuno', 'merienda'],
          en: ['coffee', 'cafe', 'espresso', 'cappuccino', 'barista', 'drinks', 'breakfast', 'latte']
        },
        pizzeria: {
          es: ['pizza', 'pizzería', 'italiana', 'mozzarella', 'horno de leña', 'delivery', 'napolitana'],
          en: ['pizza', 'pizzeria', 'italian', 'mozzarella', 'wood oven', 'delivery', 'neapolitan']
        },
        food_truck: {
          es: ['food truck', 'móvil', 'callejera', 'evento', 'festival', 'rápida'],
          en: ['food truck', 'mobile', 'street food', 'event', 'festival', 'fast']
        }
      };
      
      this.urlPatterns = {
        bakery: ['panaderia', 'bakery', 'bread', 'pan'],
        restaurant: ['restaurante', 'restaurant', 'comida', 'food'],
        cafe: ['cafe', 'coffee', 'cafeteria'],
        pizzeria: ['pizza', 'pizzeria'],
        food_truck: ['foodtruck', 'food-truck']
      };
    }
    
    async detect(config = {}) {
      const startTime = performance.now();
      
      try {
        const detectionMethods = [
          { method: this.analyzeContent.bind(this), weight: config.contentWeight || 0.4 },
          { method: this.analyzeStructure.bind(this), weight: config.structureWeight || 0.3 },
          { method: this.analyzeImages.bind(this), weight: config.imageWeight || 0.2 },
          { method: this.analyzeURL.bind(this), weight: config.urlWeight || 0.1 }
        ];
        
        const scores = {};
        const indicators = [];
        
        // Ejecutar métodos de detección en paralelo
        const results = await Promise.allSettled(
          detectionMethods.map(({ method, weight }) =>
            method().then(result => ({ result, weight }))
          )
        );
        
        // Combinar resultados
        results.forEach((promiseResult, index) => {
          if (promiseResult.status === 'fulfilled') {
            const { result, weight } = promiseResult.value;
            
            Object.entries(result.scores || {}).forEach(([businessType, score]) => {
              if (!scores[businessType]) scores[businessType] = 0;
              scores[businessType] += score * weight;
            });
            
            if (result.indicators) {
              indicators.push(...result.indicators);
            }
          } else {
            console.warn(`[Business Detector] Method ${index} failed:`, promiseResult.reason);
          }
        });
        
        // Encontrar el tipo con mayor puntuación
        const sortedResults = Object.entries(scores)
          .sort(([,a], [,b]) => b - a)
          .map(([type, score]) => ({ 
            type, 
            confidence: Math.min(Math.round(score * 100), 100) 
          }));
        
        const topResult = sortedResults[0];
        const detectionTime = performance.now() - startTime;
        
        const result = {
          type: topResult?.type || 'unknown',
          confidence: topResult?.confidence || 0,
          indicators,
          allResults: sortedResults,
          detectionTime: Math.round(detectionTime),
          timestamp: new Date().toISOString()
        };
        
        console.log('[Business Detector] Detection completed:', result);
        return result;
        
      } catch (error) {
        console.error('[Business Detector] Detection failed:', error);
        return {
          type: 'unknown',
          confidence: 0,
          indicators: [],
          allResults: [],
          detectionTime: performance.now() - startTime,
          error: error.message
        };
      }
    }
    
    async analyzeContent() {
      const lang = document.documentElement.lang?.substr(0, 2) || 'es';
      const text = this.extractPageText();
      const scores = {};
      const indicators = [];
      
      if (!text || text.length < 50) {
        return { scores, indicators };
      }
      
      Object.entries(this.keywords).forEach(([businessType, langKeywords]) => {
        const keywords = langKeywords[lang] || langKeywords.es;
        let totalMatches = 0;
        let weightedScore = 0;
        
        keywords.forEach(keyword => {
          const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}\\b`, 'gi');
          const matches = (text.match(regex) || []).length;
          
          if (matches > 0) {
            const weight = this.getTextLocationWeight(keyword);
            totalMatches += matches;
            weightedScore += matches * weight;
            
            indicators.push({
              source: 'content',
              evidence: `Keyword "${keyword}" found ${matches} times`,
              businessType,
              weight,
              confidence: Math.min(matches * 20, 100)
            });
          }
        });
        
        // Normalizar score por longitud del texto
        scores[businessType] = Math.min(weightedScore / (text.split(' ').length / 100), 1);
      });
      
      return { scores, indicators };
    }
    
    async analyzeStructure() {
      const scores = {};
      const indicators = [];
      
      // Analizar elementos específicos
      const structureChecks = [
        {
          selector: '[class*="menu"], [class*="carta"], [id*="menu"], nav',
          businessTypes: ['restaurant', 'cafe', 'pizzeria'],
          weight: 0.3,
          name: 'menu_elements'
        },
        {
          selector: '[class*="product"], [class*="item"], [class*="dish"]',
          businessTypes: ['bakery', 'restaurant', 'pizzeria'],
          weight: 0.2,
          name: 'product_elements'
        },
        {
          selector: '[class*="galeria"], [class*="gallery"], [class*="photo"]',
          businessTypes: ['bakery', 'restaurant', 'cafe'],
          weight: 0.1,
          name: 'gallery_elements'
        }
      ];
      
      structureChecks.forEach(({ selector, businessTypes, weight, name }) => {
        const elements = document.querySelectorAll(selector);
        
        if (elements.length > 0) {
          businessTypes.forEach(businessType => {
            if (!scores[businessType]) scores[businessType] = 0;
            scores[businessType] += Math.min(elements.length * weight, weight);
          });
          
          indicators.push({
            source: 'structure',
            evidence: `Found ${elements.length} ${name}`,
            businessTypes,
            confidence: Math.min(elements.length * 25, 100)
          });
        }
      });
      
      return { scores, indicators };
    }
    
    async analyzeImages() {
      const scores = {};
      const indicators = [];
      const images = document.querySelectorAll('img[alt], img[src]');
      
      if (images.length === 0) {
        return { scores, indicators };
      }
      
      images.forEach((img, index) => {
        if (index > 20) return; // Limitar análisis a primeras 20 imágenes
        
        const alt = (img.alt || '').toLowerCase();
        const src = (img.src || '').toLowerCase();
        const combinedText = `${alt} ${src}`;
        
        Object.entries(this.keywords).forEach(([businessType, langKeywords]) => {
          const allKeywords = [...langKeywords.es, ...langKeywords.en];
          
          allKeywords.forEach(keyword => {
            if (combinedText.includes(keyword.toLowerCase())) {
              if (!scores[businessType]) scores[businessType] = 0;
              scores[businessType] += 0.05;
              
              indicators.push({
                source: 'images',
                evidence: `Image contains "${keyword}"`,
                businessType,
                confidence: 60
              });
            }
          });
        });
      });
      
      return { scores, indicators };
    }
    
    async analyzeURL() {
      const scores = {};
      const indicators = [];
      const url = window.location.href.toLowerCase();
      const hostname = window.location.hostname.toLowerCase();
      
      Object.entries(this.urlPatterns).forEach(([businessType, patterns]) => {
        patterns.forEach(pattern => {
          if (hostname.includes(pattern) || url.includes(pattern)) {
            if (!scores[businessType]) scores[businessType] = 0;
            scores[businessType] += hostname.includes(pattern) ? 0.8 : 0.4;
            
            indicators.push({
              source: 'url',
              evidence: `URL contains "${pattern}"`,
              businessType,
              confidence: hostname.includes(pattern) ? 90 : 70
            });
          }
        });
      });
      
      return { scores, indicators };
    }
    
    extractPageText() {
      // Extraer texto de elementos importantes con prioridad
      const importantSelectors = [
        { selector: 'title', weight: 3 },
        { selector: 'h1', weight: 2.5 },
        { selector: 'h2, h3', weight: 2 },
        { selector: 'nav, [class*="nav"]', weight: 2 },
        { selector: 'meta[name="description"]', weight: 2, attr: 'content' },
        { selector: 'main, [class*="content"], article', weight: 1 }
      ];
      
      let weightedText = '';
      
      importantSelectors.forEach(({ selector, weight, attr }) => {
        try {
          const elements = document.querySelectorAll(selector);
          elements.forEach(el => {
            const text = attr ? el.getAttribute(attr) : el.textContent;
            if (text && text.trim()) {
              // Repetir texto según peso para dar mayor importancia
              for (let i = 0; i < weight; i++) {
                weightedText += ' ' + text.trim();
              }
            }
          });
        } catch (error) {
          console.warn(`[Business Detector] Error extracting text from ${selector}:`, error);
        }
      });
      
      return weightedText.toLowerCase().trim();
    }
    
    getTextLocationWeight(keyword) {
      let weight = 1;
      
      // Verificar en título
      if (document.title.toLowerCase().includes(keyword)) {
        weight += 2;
      }
      
      // Verificar en H1s
      const h1s = Array.from(document.querySelectorAll('h1'))
        .map(h => h.textContent.toLowerCase())
        .join(' ');
      
      if (h1s.includes(keyword)) {
        weight += 1.5;
      }
      
      // Verificar en navegación
      const navs = Array.from(document.querySelectorAll('nav, [class*="nav"]'))
        .map(n => n.textContent.toLowerCase())
        .join(' ');
      
      if (navs.includes(keyword)) {
        weight += 1;
      }
      
      return weight;
    }
  }
  
  /**
   * Gestor de conversación
   */
  class ConversationManager {
    constructor(apiClient, uiManager) {
      this.apiClient = apiClient;
      this.uiManager = uiManager;
      this.messages = [];
      this.isTyping = false;
    }
    
    async addMessage(messageData) {
      const message = {
        id: this.generateMessageId(),
        timestamp: new Date(),
        ...messageData
      };
      
      this.messages.push(message);
      await this.uiManager.renderMessage(message);
      
      // Scroll al último mensaje
      this.scrollToBottom();
    }
    
    async showTyping() {
      if (this.isTyping) return;
      
      this.isTyping = true;
      await this.uiManager.showTypingIndicator();
    }
    
    async hideTyping() {
      if (!this.isTyping) return;
      
      this.isTyping = false;
      this.uiManager.hideTypingIndicator();
    }
    
    scrollToBottom() {
      const conversationEl = this.uiManager.elements.conversation;
      if (conversationEl) {
        setTimeout(() => {
          conversationEl.scrollTop = conversationEl.scrollHeight;
        }, 100);
      }
    }
    
    generateMessageId() {
      return 'msg_' + Math.random().toString(36).substr(2, 9);
    }
    
    getMessageHistory() {
      return this.messages.map(msg => ({
        type: msg.type,
        content: msg.content,
        timestamp: msg.timestamp
      }));
    }
  }
  
  /**
   * Gestor de interfaz de usuario
   */
  class UIManager {
    constructor(widget) {
      this.widget = widget;
      this.elements = {};
      this.isCreated = false;
    }
    
    async create() {
      if (this.isCreated) return;
      
      // Crear estructura HTML
      const widgetHTML = this.generateWidgetHTML();
      
      // Insertar en el DOM
      document.body.insertAdjacentHTML('beforeend', widgetHTML);
      
      // Cargar CSS
      await this.loadStyles();
      
      // Obtener referencias a elementos
      this.elements = {
        widget: document.getElementById('fixeat-widget'),
        trigger: document.querySelector('.fixeat-trigger'),
        panel: document.querySelector('.fixeat-panel'),
        conversation: document.querySelector('.fixeat-conversation'),
        textarea: document.querySelector('.fixeat-textarea'),
        sendBtn: document.querySelector('.fixeat-send-btn'),
        closeBtn: document.querySelector('.fixeat-header-close'),
        badge: document.querySelector('.fixeat-notification-badge')
      };
      
      // Aplicar tema personalizado
      this.applyTheme();
      
      this.isCreated = true;
    }
    
    generateWidgetHTML() {
      const config = this.widget.config;
      const position = config.position || 'bottom-right';
      
      return `
        <div id="fixeat-widget" class="fixeat-widget fixeat-position-${position}">
          <!-- Botón Flotante -->
          <div class="fixeat-trigger" role="button" 
               aria-label="Abrir asistente de recomendaciones" 
               tabindex="0">
            <div class="fixeat-trigger-icon">
              <svg class="fixeat-icon-chat" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
              </svg>
              <svg class="fixeat-icon-close" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </div>
            <div class="fixeat-notification-badge" aria-hidden="true">1</div>
          </div>
          
          <!-- Panel Principal -->
          <div class="fixeat-panel" role="dialog" aria-hidden="true" aria-labelledby="fixeat-header-title">
            <!-- Header -->
            <div class="fixeat-header">
              <div class="fixeat-header-content">
                <div class="fixeat-avatar">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1L13.5 2.5L16.17 5.23C15.09 5.79 14 6.79 14 8H10C10 6.79 8.91 5.79 7.83 5.23L10.5 2.5L9 1L3 7V9H1V11H3L4 21C4.11 21.72 4.64 22.3 5.3 22.45L8.5 23L12 21L15.5 23L18.7 22.45C19.36 22.3 19.89 21.72 20 21L21 11H23V9H21Z"/>
                  </svg>
                </div>
                <div class="fixeat-header-text">
                  <h3 id="fixeat-header-title">Asistente de Equipamiento</h3>
                  <p class="fixeat-status">
                    <span class="fixeat-status-dot" aria-hidden="true"></span>
                    En línea
                  </p>
                </div>
              </div>
              <button class="fixeat-header-close" aria-label="Cerrar chat" type="button">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
            
            <!-- Área de Conversación -->
            <div class="fixeat-conversation" 
                 role="log" 
                 aria-live="polite" 
                 aria-label="Conversación con asistente">
            </div>
            
            <!-- Área de Input -->
            <div class="fixeat-input-area">
              <div class="fixeat-input-container">
                <textarea class="fixeat-textarea" 
                          placeholder="Escribe tu mensaje..."
                          rows="1"
                          aria-label="Escribir mensaje"></textarea>
                <button class="fixeat-send-btn" 
                        aria-label="Enviar mensaje" 
                        type="button">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                  </svg>
                </button>
              </div>
              <div class="fixeat-footer">
                <p class="fixeat-powered-by">
                  <a href="https://fixeat.ai" target="_blank" rel="noopener">
                    Powered by <strong>Fixeat AI</strong>
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      `;
    }
    
    async loadStyles() {
      // Verificar si ya están cargados los estilos
      if (document.querySelector('#fixeat-widget-styles')) return;
      
      const link = document.createElement('link');
      link.id = 'fixeat-widget-styles';
      link.rel = 'stylesheet';
      link.href = `${CDN_BASE_URL}/fixeat-widget.min.css`;
      
      return new Promise((resolve, reject) => {
        link.onload = resolve;
        link.onerror = () => {
          console.warn('[Fixeat Widget] Failed to load CSS from CDN, using inline styles');
          this.injectInlineStyles();
          resolve();
        };
        document.head.appendChild(link);
      });
    }
    
    injectInlineStyles() {
      // CSS inline como fallback
      const style = document.createElement('style');
      style.id = 'fixeat-widget-inline-styles';
      style.textContent = `
        /* Estilos básicos del widget como fallback */
        .fixeat-widget {
          position: fixed !important;
          z-index: 2147483647 !important;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
          font-size: 14px !important;
          line-height: 1.5 !important;
          box-sizing: border-box !important;
        }
        
        .fixeat-widget *, .fixeat-widget *::before, .fixeat-widget *::after {
          box-sizing: inherit !important;
        }
        
        .fixeat-position-bottom-right {
          bottom: 20px !important;
          right: 20px !important;
        }
        
        .fixeat-position-bottom-left {
          bottom: 20px !important;
          left: 20px !important;
        }
        
        .fixeat-trigger {
          width: 60px !important;
          height: 60px !important;
          background: #007bff !important;
          border-radius: 50% !important;
          cursor: pointer !important;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          position: relative !important;
          transition: all 0.3s ease !important;
        }
        
        .fixeat-trigger:hover {
          transform: scale(1.05) !important;
          background: #0056b3 !important;
        }
        
        .fixeat-trigger-icon svg {
          width: 24px !important;
          height: 24px !important;
          fill: white !important;
        }
        
        .fixeat-panel {
          position: absolute !important;
          bottom: 80px !important;
          right: 0 !important;
          width: 380px !important;
          height: 600px !important;
          background: white !important;
          border-radius: 12px !important;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
          opacity: 0 !important;
          transform: translateY(20px) scale(0.95) !important;
          transition: all 0.3s ease !important;
          visibility: hidden !important;
          overflow: hidden !important;
        }
        
        .fixeat-widget.open .fixeat-panel {
          opacity: 1 !important;
          transform: translateY(0) scale(1) !important;
          visibility: visible !important;
        }
        
        @media (max-width: 480px) {
          .fixeat-panel {
            width: calc(100vw - 40px) !important;
            height: 70vh !important;
            max-height: 600px !important;
          }
        }
      `;
      
      document.head.appendChild(style);
    }
    
    applyTheme() {
      const theme = this.widget.config.theme || {};
      const widget = this.elements.widget;
      
      if (theme.primaryColor) {
        widget.style.setProperty('--fixeat-primary', theme.primaryColor);
        
        // Calcular color más oscuro para hover
        const darkerColor = this.darkenColor(theme.primaryColor, 20);
        widget.style.setProperty('--fixeat-primary-dark', darkerColor);
      }
      
      if (theme.fontFamily) {
        widget.style.setProperty('--fixeat-font-family', theme.fontFamily);
      }
      
      if (theme.borderRadius) {
        widget.style.setProperty('--fixeat-radius', theme.borderRadius);
      }
    }
    
    darkenColor(color, percent) {
      // Función simple para oscurecer un color
      const num = parseInt(color.replace("#", ""), 16);
      const amt = Math.round(2.55 * percent);
      const R = (num >> 16) - amt;
      const G = (num >> 8 & 0x00FF) - amt;
      const B = (num & 0x0000FF) - amt;
      return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255))
        .toString(16).slice(1);
    }
    
    async renderMessage(message) {
      const messageEl = this.createMessageElement(message);
      this.elements.conversation.appendChild(messageEl);
      
      // Animar entrada
      requestAnimationFrame(() => {
        messageEl.style.opacity = '1';
        messageEl.style.transform = 'translateY(0)';
      });
    }
    
    createMessageElement(message) {
      const div = document.createElement('div');
      div.className = `fixeat-message fixeat-message-${message.type}`;
      div.style.opacity = '0';
      div.style.transform = 'translateY(10px)';
      div.style.transition = 'all 0.3s ease';
      
      let html = '';
      
      if (message.type === 'bot') {
        html += `
          <div class="fixeat-message-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z"/>
            </svg>
          </div>
        `;
      }
      
      html += '<div class="fixeat-message-content">';
      
      if (message.content) {
        html += `<div class="fixeat-message-bubble"><p>${this.escapeHtml(message.content)}</p></div>`;
      }
      
      // Agregar widget si existe
      if (message.widget) {
        html += this.createWidgetElement(message.widget);
      }
      
      // Agregar opciones si existen
      if (message.options) {
        html += '<div class="fixeat-message-actions">';
        message.options.forEach(option => {
          html += `<button class="fixeat-btn fixeat-btn-secondary" data-option="${this.escapeHtml(option)}">${this.escapeHtml(option)}</button>`;
        });
        html += '</div>';
      }
      
      // Agregar acciones si existen
      if (message.actions) {
        html += '<div class="fixeat-message-actions">';
        message.actions.forEach(action => {
          html += `<button class="fixeat-btn fixeat-btn-primary" data-action="${action.action}">${this.escapeHtml(action.text)}</button>`;
        });
        html += '</div>';
      }
      
      html += '</div>';
      
      div.innerHTML = html;
      
      // Agregar event listeners a botones
      this.bindMessageEvents(div, message);
      
      return div;
    }
    
    createWidgetElement(widget) {
      switch (widget.type) {
        case 'numeric_input':
          return this.createNumericInputWidget(widget);
        case 'product_recommendation':
          return this.createProductRecommendationWidget(widget);
        default:
          return '';
      }
    }
    
    createNumericInputWidget(widget) {
      return `
        <div class="fixeat-question-widget">
          <div class="fixeat-input-group">
            <input type="number" 
                   class="fixeat-input" 
                   placeholder="${widget.placeholder || 'Ingresa un número'}" 
                   min="${widget.min || ''}"
                   max="${widget.max || ''}"
                   data-question-id="${widget.questionId}">
            ${widget.unit ? `<span class="fixeat-input-suffix">${widget.unit}</span>` : ''}
          </div>
          ${widget.help ? `<div class="fixeat-help-text"><small>💡 ${this.escapeHtml(widget.help)}</small></div>` : ''}
          <button class="fixeat-btn fixeat-btn-primary fixeat-btn-send" data-question-id="${widget.questionId}">
            Continuar
          </button>
        </div>
      `;
    }
    
    createProductRecommendationWidget(widget) {
      const { rank, product, scores, reasoning, pricing } = widget;
      
      return `
        <div class="fixeat-product-recommendation">
          <div class="fixeat-product-header">
            <span class="fixeat-product-rank">#${rank}</span>
            <h4 class="fixeat-product-name">${this.escapeHtml(product.name)}</h4>
            <span class="fixeat-product-score">${scores.overall_fit}% match</span>
          </div>
          
          <div class="fixeat-product-details">
            <p class="fixeat-product-brand">${this.escapeHtml(product.brand)} - ${this.escapeHtml(product.category)}</p>
            
            ${reasoning.primary_reasons ? `
              <div class="fixeat-product-reasons">
                <strong>Por qué es ideal para ti:</strong>
                <ul>
                  ${reasoning.primary_reasons.slice(0, 3).map(reason => 
                    `<li>${this.escapeHtml(reason)}</li>`
                  ).join('')}
                </ul>
              </div>
            ` : ''}
            
            ${pricing ? `
              <div class="fixeat-product-pricing">
                <span class="fixeat-price">$${pricing.base_price?.toLocaleString()} ${pricing.currency || 'MXN'}</span>
                ${pricing.financing_available ? '<span class="fixeat-financing">💳 Financiamiento disponible</span>' : ''}
              </div>
            ` : ''}
          </div>
          
          <div class="fixeat-product-actions">
            <button class="fixeat-btn fixeat-btn-primary" data-product-action="details" data-product-id="${product.id}">
              Ver detalles
            </button>
            <button class="fixeat-btn fixeat-btn-secondary" data-product-action="contact" data-product-id="${product.id}">
              Contactar vendedor
            </button>
          </div>
        </div>
      `;
    }
    
    bindMessageEvents(messageEl, message) {
      // Botones de opciones
      messageEl.querySelectorAll('[data-option]').forEach(btn => {
        btn.addEventListener('click', () => {
          const option = btn.dataset.option;
          this.widget.handleUserResponse(option);
        });
      });
      
      // Botones de acciones
      messageEl.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
          const action = btn.dataset.action;
          this.widget.handleUserAction(action);
        });
      });
      
      // Inputs numéricos
      messageEl.querySelectorAll('[data-question-id]').forEach(input => {
        if (input.tagName === 'INPUT') {
          input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
              const btn = messageEl.querySelector(`button[data-question-id="${input.dataset.questionId}"]`);
              if (btn) btn.click();
            }
          });
        } else if (input.tagName === 'BUTTON') {
          input.addEventListener('click', () => {
            const inputEl = messageEl.querySelector(`input[data-question-id="${input.dataset.questionId}"]`);
            if (inputEl && inputEl.value) {
              this.widget.handleQuestionResponse(input.dataset.questionId, inputEl.value);
            }
          });
        }
      });
      
      // Acciones de productos
      messageEl.querySelectorAll('[data-product-action]').forEach(btn => {
        btn.addEventListener('click', () => {
          const action = btn.dataset.productAction;
          const productId = btn.dataset.productId;
          this.widget.handleProductAction(action, productId);
        });
      });
    }
    
    async showTypingIndicator() {
      const typingEl = document.createElement('div');
      typingEl.className = 'fixeat-message fixeat-message-bot fixeat-typing-message';
      typingEl.innerHTML = `
        <div class="fixeat-message-avatar">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z"/>
          </svg>
        </div>
        <div class="fixeat-message-content">
          <div class="fixeat-message-bubble">
            <div class="fixeat-typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      `;
      
      this.elements.conversation.appendChild(typingEl);
      this.elements.conversation.scrollTop = this.elements.conversation.scrollHeight;
    }
    
    hideTypingIndicator() {
      const typingEl = this.elements.conversation.querySelector('.fixeat-typing-message');
      if (typingEl) {
        typingEl.remove();
      }
    }
    
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  }
  
  /**
   * Clase principal del Widget
   */
  class FixeatWidget {
    constructor(config = {}) {
      this.config = this.mergeConfig(config);
      this.isInitialized = false;
      this.isOpen = false;
      
      // Inicializar componentes
      this.apiClient = new FixeatAPIClient(this.config);
      this.businessDetector = new BusinessDetector();
      this.uiManager = new UIManager(this);
      this.conversationManager = new ConversationManager(this.apiClient, this.uiManager);
      
      // Estado
      this.detectedBusiness = null;
      this.currentSession = null;
      this.currentQuestionId = null;
    }
    
    getDefaultConfig() {
      return {
        apiKey: null,
        apiUrl: API_BASE_URL,
        theme: {
          primaryColor: '#007bff',
          fontFamily: 'inherit',
          borderRadius: '12px'
        },
        position: 'bottom-right',
        autoDetect: true,
        language: 'es',
        debug: false,
        autoStart: true,
        welcomeDelay: 3000,
        customPrompts: {},
        detectionConfig: {
          contentWeight: 0.4,
          structureWeight: 0.3,
          imageWeight: 0.2,
          urlWeight: 0.1
        }
      };
    }
    
    mergeConfig(userConfig) {
      const defaultConfig = this.getDefaultConfig();
      return {
        ...defaultConfig,
        ...userConfig,
        theme: { ...defaultConfig.theme, ...(userConfig.theme || {}) },
        detectionConfig: { ...defaultConfig.detectionConfig, ...(userConfig.detectionConfig || {}) }
      };
    }
    
    async init() {
      if (this.isInitialized) {
        this.log('Widget already initialized');
        return;
      }
      
      try {
        this.log('Initializing Fixeat Widget v' + WIDGET_VERSION);
        
        if (!this.config.apiKey) {
          throw new Error('API Key is required. Please provide apiKey in FixeatConfig.');
        }
        
        // Detectar tipo de negocio
        if (this.config.autoDetect) {
          this.detectedBusiness = await this.businessDetector.detect(this.config.detectionConfig);
          this.log('Business detected:', this.detectedBusiness);
        }
        
        // Crear UI
        await this.uiManager.create();
        
        // Asignar conversationManager con uiManager
        this.conversationManager.uiManager = this.uiManager;
        
        // Bind events
        this.bindEvents();
        
        // Auto-start
        if (this.config.autoStart) {
          setTimeout(() => {
            this.showWelcomeMessage();
          }, this.config.welcomeDelay);
        }
        
        this.isInitialized = true;
        this.log('Widget initialized successfully');
        
        this.dispatchEvent('fixeat:initialized', { 
          detectedBusiness: this.detectedBusiness,
          version: WIDGET_VERSION
        });
        
      } catch (error) {
        this.error('Failed to initialize widget:', error);
        throw error;
      }
    }
    
    bindEvents() {
      // Trigger click
      this.uiManager.elements.trigger.addEventListener('click', () => {
        this.toggle();
      });
      
      // Trigger keyboard
      this.uiManager.elements.trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.toggle();
        }
      });
      
      // Close button
      this.uiManager.elements.closeBtn.addEventListener('click', () => {
        this.close();
      });
      
      // Send button
      this.uiManager.elements.sendBtn.addEventListener('click', () => {
        this.handleSendMessage();
      });
      
      // Textarea
      this.uiManager.elements.textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.handleSendMessage();
        }
      });
      
      // Auto-resize textarea
      this.uiManager.elements.textarea.addEventListener('input', () => {
        this.autoResizeTextarea();
      });
      
      // Click outside
      document.addEventListener('click', (e) => {
        if (!this.uiManager.elements.widget.contains(e.target) && this.isOpen) {
          this.close();
        }
      });
      
      // Escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.close();
        }
      });
    }
    
    async showWelcomeMessage() {
      try {
        if (!this.detectedBusiness || this.detectedBusiness.confidence < 60) {
          await this.conversationManager.addMessage({
            type: 'bot',
            content: this.config.customPrompts.welcome || 
                     '¡Hola! Soy tu asistente de equipamiento. ¿En qué tipo de negocio trabajas?',
            options: ['Panadería', 'Restaurante', 'Cafetería', 'Pizzería', 'Otro']
          });
        } else {
          const businessName = this.getBusinessTypeName(this.detectedBusiness.type);
          await this.conversationManager.addMessage({
            type: 'bot',
            content: `¡Hola! Detecté que tienes ${businessName}. ¿Te ayudo a encontrar el equipo perfecto para optimizar tu negocio?`,
            actions: [
              { text: '¡Sí, ayúdame!', action: 'start_recommendation' },
              { text: 'No es mi tipo de negocio', action: 'correct_business_type' },
              { text: 'No ahora', action: 'dismiss' }
            ]
          });
        }
        
        this.showNotification();
        
      } catch (error) {
        this.error('Error showing welcome message:', error);
      }
    }
    
    async handleSendMessage() {
      const text = this.uiManager.elements.textarea.value.trim();
      if (!text) return;
      
      this.uiManager.elements.textarea.value = '';
      this.autoResizeTextarea();
      
      await this.conversationManager.addMessage({
        type: 'user',
        content: text
      });
      
      await this.processUserMessage(text);
    }
    
    async processUserMessage(message) {
      try {
        await this.conversationManager.showTyping();
        
        // Crear sesión si no existe
        if (!this.currentSession) {
          this.currentSession = await this.apiClient.createSession({
            businessType: this.detectedBusiness?.type || 'unknown',
            userMessage: message,
            detectionData: this.detectedBusiness
          });
        }
        
        // Enviar mensaje
        const response = await this.apiClient.sendMessage(this.currentSession.id, message);
        
        await this.conversationManager.hideTyping();
        await this.handleAPIResponse(response);
        
      } catch (error) {
        await this.conversationManager.hideTyping();
        this.error('Error processing message:', error);
        
        await this.conversationManager.addMessage({
          type: 'bot',
          content: 'Lo siento, hubo un problema. ¿Puedes intentar de nuevo?'
        });
      }
    }
    
    async handleAPIResponse(response) {
      // Esta función será implementada según la respuesta real de la API
      await this.conversationManager.addMessage({
        type: 'bot',
        content: response.message || 'Gracias por tu respuesta. Estoy procesando la información...'
      });
    }
    
    async handleUserResponse(response) {
      await this.conversationManager.addMessage({
        type: 'user',
        content: response
      });
      
      await this.processUserMessage(response);
    }
    
    async handleUserAction(action) {
      switch (action) {
        case 'start_recommendation':
          await this.startRecommendationFlow();
          break;
        case 'correct_business_type':
          await this.correctBusinessType();
          break;
        case 'dismiss':
          this.close();
          break;
        default:
          this.log('Unknown action:', action);
      }
    }
    
    async handleQuestionResponse(questionId, value) {
      this.currentQuestionId = questionId;
      
      await this.conversationManager.addMessage({
        type: 'user',
        content: `${value}`
      });
      
      await this.processUserMessage(value);
    }
    
    async handleProductAction(action, productId) {
      switch (action) {
        case 'details':
          await this.showProductDetails(productId);
          break;
        case 'contact':
          await this.showContactInfo(productId);
          break;
        default:
          this.log('Unknown product action:', action);
      }
    }
    
    async startRecommendationFlow() {
      await this.conversationManager.addMessage({
        type: 'bot',
        content: 'Perfecto. Para recomendarte el equipo ideal, necesito hacerte algunas preguntas breves.',
        widget: {
          type: 'numeric_input',
          questionId: 'production_volume',
          placeholder: 'Ej: 50',
          min: 1,
          max: 10000,
          unit: 'kg/día',
          help: 'Incluye toda tu producción diaria'
        }
      });
    }
    
    async correctBusinessType() {
      await this.conversationManager.addMessage({
        type: 'bot',
        content: '¿Podrías decirme qué tipo de negocio tienes?',
        options: ['Panadería', 'Restaurante', 'Cafetería', 'Pizzería', 'Food Truck', 'Hotel', 'Otro']
      });
    }
    
    async showProductDetails(productId) {
      await this.conversationManager.addMessage({
        type: 'bot',
        content: `Te envío más información del producto por email. ¿Cuál es tu dirección de correo?`
      });
    }
    
    async showContactInfo(productId) {
      await this.conversationManager.addMessage({
        type: 'bot',
        content: 'Te conecto con un especialista. ¿Prefieres que te llamemos o te enviamos información por WhatsApp?',
        actions: [
          { text: '📞 Llamada', action: 'request_call' },
          { text: '💬 WhatsApp', action: 'request_whatsapp' },
          { text: '📧 Email', action: 'request_email' }
        ]
      });
    }
    
    // UI Methods
    toggle() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    }
    
    open() {
      this.isOpen = true;
      this.uiManager.elements.widget.classList.add('open');
      this.uiManager.elements.panel.setAttribute('aria-hidden', 'false');
      this.hideNotification();
      
      // Focus en textarea después de que la animación termine
      setTimeout(() => {
        this.uiManager.elements.textarea.focus();
      }, 300);
      
      this.dispatchEvent('fixeat:opened');
    }
    
    close() {
      this.isOpen = false;
      this.uiManager.elements.widget.classList.remove('open');
      this.uiManager.elements.panel.setAttribute('aria-hidden', 'true');
      this.dispatchEvent('fixeat:closed');
    }
    
    showNotification() {
      if (!this.isOpen) {
        this.uiManager.elements.badge.classList.add('show');
        this.uiManager.elements.badge.textContent = '1';
      }
    }
    
    hideNotification() {
      this.uiManager.elements.badge.classList.remove('show');
    }
    
    autoResizeTextarea() {
      const textarea = this.uiManager.elements.textarea;
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }
    
    // Utility methods
    getBusinessTypeName(type) {
      const names = {
        bakery: 'una panadería',
        restaurant: 'un restaurante',
        cafe: 'una cafetería',
        pizzeria: 'una pizzería',
        food_truck: 'un food truck',
        hotel: 'un hotel'
      };
      return names[type] || 'un negocio gastronómico';
    }
    
    dispatchEvent(eventName, data = {}) {
      const event = new CustomEvent(eventName, { 
        detail: { 
          ...data, 
          widget: this,
          timestamp: new Date().toISOString()
        } 
      });
      window.dispatchEvent(event);
      this.log('Event dispatched:', eventName, data);
    }
    
    log(...args) {
      if (this.config.debug) {
        console.log('[Fixeat Widget]', ...args);
      }
    }
    
    error(...args) {
      console.error('[Fixeat Widget]', ...args);
    }
    
    // Public API
    destroy() {
      if (this.uiManager.elements.widget) {
        this.uiManager.elements.widget.remove();
      }
      
      const styles = document.querySelector('#fixeat-widget-styles, #fixeat-widget-inline-styles');
      if (styles) {
        styles.remove();
      }
      
      this.isInitialized = false;
      this.dispatchEvent('fixeat:destroyed');
    }
    
    updateConfig(newConfig) {
      this.config = this.mergeConfig({ ...this.config, ...newConfig });
      
      if (this.isInitialized) {
        this.uiManager.applyTheme();
      }
    }
  }
  
  // Exportar al scope global
  window.FixeatWidget = FixeatWidget;
  
  // Auto-inicialización
  if (window.FixeatConfig) {
    const initWidget = () => {
      try {
        const widget = new FixeatWidget(window.FixeatConfig);
        widget.init().catch(console.error);
        window.fixeatWidget = widget;
      } catch (error) {
        console.error('[Fixeat Widget] Auto-initialization failed:', error);
      }
    };
    
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initWidget);
    } else {
      initWidget();
    }
  }
  
})(window, document);


