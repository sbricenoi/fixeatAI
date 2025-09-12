# KB Dummy Técnico de Equipamientos (para ingesta RAG)

Nota: Documento de referencia técnica con casos frecuentes, procedimientos y listas de verificación. Diseñado para alimentar la KB (Chroma) y facilitar respuestas precisas y accionables.

---
id: dummy-unique-uhp12pro60g-001
domain: technical_procedure
brand: UNIQUE
model: UHP12PRO60G
category: horno_piso
location: N/A
summary: Fugas de vapor y problemas de sellado en cámaras 1 y 2.
common_symptoms:
  - Pérdida de vapor visible en puerta y marcos
  - Condensación excesiva en cámara
  - Tiempos de cocción irregulares
diagnostic_steps:
  - Verificar estado de burletes y su continuidad (deformaciones, cortes)
  - Comprobar ajuste y presión de cierre de puerta (bisagras y manilla)
  - Inspeccionar drenajes y desagües por obstrucción
  - Chequear lectura de sonda de temperatura de cámara vs termómetro externo (±2°C)
root_causes:
  - Burletes deteriorados por temperatura y uso
  - Desalineación de puerta o desgaste de bisagras
  - Sonda de temperatura descalibrada
repair_procedure:
  - Reemplazar burlete de puerta (parcial o completo)
  - Alinear puerta; ajustar bisagras y cierre
  - Verificar y recalibrar sonda; reemplazar si deriva >3°C
parts_tools:
  - Burlete puerta UHP12PRO60G
  - Kit bisagras puerta
  - Sonda de temperatura cámara
  - Herramientas: llaves, destornilladores, termómetro de referencia
preventive_maintenance:
  - Limpieza semanal de asiento de puerta y burlete
  - Revisión mensual de cierre de puerta y ajuste
  - Verificación trimestral de calibración de sonda (agua-hielo)
acceptance_tests:
  - Prueba de cocción estándar; fuga de vapor no visible en contorno
  - Estabilidad térmica ±2°C a consigna durante 20 min

---
id: dummy-unique-uhp9pro60g-001
domain: technical_procedure
brand: UNIQUE
model: UHP9PRO60G
category: horno_piso
summary: Encendido intermitente y cocción dispareja.
common_symptoms:
  - Cámara que no enciende a la primera
  - Productos con coloración desigual
diagnostic_steps:
  - Revisar presión de gas y regulador
  - Limpieza de quemadores y termocuplas
  - Verificar protección térmica/guardamotor del ventilador
root_causes:
  - Suciedad en quemadores y termocuplas
  - Caídas de tensión eléctrica o regulación de gas incorrecta
repair_procedure:
  - Limpieza profunda de quemadores y conductos
  - Ajustar flujo de gas según especificación
  - Reemplazo de termocupla si resistencia fuera de rango
acceptance_tests:
  - Encendido en <5 s; llama estable
  - Uniformidad de cocción medible (±10% en colorimetría)

---
id: dummy-unique-uhp3pro60g-001
domain: technical_procedure
brand: UNIQUE
model: UHP3PRO60G
category: horno_piso
summary: Saltos de llave y apagados por protección.
diagnostic_steps:
  - Medir consumo por fase y verificar protecciones
  - Revisar cableado de panel de control y puntos calientes
root_causes:
  - Ajuste incorrecto de protección térmica
  - Corto intermitente en cableado de panel
repair_procedure:
  - Regular guardamotor según placa
  - Corrección de conexiones y reemplazo de cableado degradado

---
id: dummy-unox-xebc10eugprm-001
domain: technical_procedure
brand: UNOX
model: XEBC-10EUGPRM
category: horno_convector
summary: Configuración y pruebas de lavado; mantenimiento de generador de vapor.
diagnostic_steps:
  - Verificar mangueras de desagüe y filtro antical
  - Ejecutar ciclo de lavado y observar errores
root_causes:
  - Acumulación de cal en circuito de vapor
  - Filtro o desagüe obstruido
repair_procedure:
  - Desincrustación del generador de vapor conforme manual
  - Cambio de filtro y kit de desagüe
acceptance_tests:
  - Ciclo de lavado completo sin errores
  - Generación de vapor estable en consigna

---
id: dummy-unox-xebl16eu-gprs-001
domain: technical_procedure
brand: UNOX
model: XEBL-16EU-GPRS
category: horno_convector
summary: Calibración, uniformidad y validación de osmosis.
diagnostic_steps:
  - Validar presión y caudal de agua tratada (osmosis)
  - Test de uniformidad con sondas en bandejas
repair_procedure:
  - Reemplazo de electrodos de chispa y sensor de llama si necesario
  - Ajuste de ventiladores y limpieza de difusores
acceptance_tests:
  - Delta térmico entre posiciones <±2°C

---
id: dummy-unox-xb813g-001
domain: technical_procedure
brand: UNOX
model: XB813G
category: horno_convector
summary: Puesta en marcha y chequeo de seguridad en gas.
diagnostic_steps:
  - Test de estanqueidad y verificación de inyectoría
  - Revisión de llama y ventilación
preventive_maintenance:
  - Limpieza mensual de quemadores y revisión de filtros de aire

---
id: dummy-zucchelli-rotor60x80g-001
domain: technical_procedure
brand: ZUCCHELLI
model: ROTOR 60X80G
category: horno_rotatorio
summary: Repuestos críticos y estabilización térmica.
common_symptoms:
  - Enfriamiento de cabina por relé pegado
  - Desalineación de carro
repair_procedure:
  - Cambio de relé/PCB de válvula de enfriamiento
  - Ajuste de rodajes del carro y rieles
parts_tools:
  - PCB control, relé, junta de carro, kit ventilación

---
id: dummy-zucchelli-rotor6080-touch-001
domain: technical_procedure
brand: ZUCCHELLI
model: ROTOR 6080 TOUCH
category: horno_rotatorio
summary: Panel táctil y rutinas de mantenimiento.
diagnostic_steps:
  - Test táctil; actualización de firmware si aplica
  - Revisión de ventilación y limpieza interna

---
id: dummy-zucchelli-rotor80x80-001
domain: technical_procedure
brand: ZUCCHELLI
model: ROTOR 80X80
category: horno_rotatorio
summary: Instalación eléctrica y verificación de levantador.
diagnostic_steps:
  - Calibración de sensores de puerta y elevador
  - Verificación de resistencias y ventiladores

---
id: dummy-sinmag-sm630-001
domain: technical_procedure
brand: SINMAG
model: SM630
category: laminadora
summary: Rodillo 60 cm; ajuste mecánico y seguridad.
diagnostic_steps:
  - Revisión de cadenas, piñones y rascadores
  - Ajuste de correa y tensión
repair_procedure:
  - Cambio de piñón desgastado; lubricación completa
acceptance_tests:
  - Espesor uniforme a lo largo del pliego (±0.5 mm)

---
id: dummy-sinmag-sm302-001
domain: technical_procedure
brand: SINMAG
model: SM-302
category: rebanadora
summary: Sistema de seguridad y pruebas operativas.
diagnostic_steps:
  - Test de micro-switches de seguridad y guardas
  - Alineación de cuchillas
repair_procedure:
  - Sustitución de switch defectuoso; ajuste de cuchillas
acceptance_tests:
  - Corte consistente sin rebabas

---
id: dummy-sinmag-scft2p9cad-001
domain: technical_procedure
brand: SINMAG
model: SCFT2P9CAD
category: camara_fermentacion
summary: Control de humedad y temperatura; flotadores.
diagnostic_steps:
  - Revisión de resistencias y flotadores de humedad
  - Inspección de evaporador/condensador por corrosión
repair_procedure:
  - Reemplazo de dos resistencias y un flotador; sugerir cambio de agua si hay sarro

---
id: dummy-monferrina-generic-001
domain: technical_procedure
brand: MONFERRINA
model: GENERICO
category: maquinaria_pasta
summary: Motor/reductor no arranca; diagnóstico eléctrico.
diagnostic_steps:
  - Verificar alimentación, térmicos y estado del motor
  - Comprobar caja reductora por trabas
repair_procedure:
  - Servicio de motor; reemplazo de rodamientos; ajuste reductor

---
id: dummy-izo-fs24-001
domain: technical_procedure
brand: IZO
model: FS24
category: freidora
summary: Brote violento a 150°C; causas y mitigación.
diagnostic_steps:
  - Confirmar ausencia de agua en aceite y cuba
  - Revisar restos de detergente o humedad en alimentos
root_causes:
  - Contaminación por agua/humedad o residuos
repair_procedure:
  - Limpieza profunda; secado total; filtrado/cambio de aceite
preventive_maintenance:
  - Filtrado periódico y control de impurezas

---
id: dummy-taxonomy-synonyms-001
domain: taxonomy
summary: Sinónimos y normalización de equipos frecuente.
synonyms:
  - { term: "burlete", aliases: ["junta", "goma puerta"] }
  - { term: "termocupla", aliases: ["sonda de llama", "sensor llama"] }
  - { term: "cámara", aliases: ["horno", "compartimiento"] }
  - { term: "generador de vapor", aliases: ["caldera", "boiler"] }

---
id: dummy-checklist-pm-hornos-001
domain: preventive_maintenance
category: hornos
summary: Checklist de mantención preventiva (mensual/trimestral).
tasks:
  - Limpieza de ventiladores, filtros y difusores
  - Revisión de conexiones eléctricas y consumo por fase
  - Verificación de burletes y cierre de puerta
  - Calibración de temperatura y sondas (prueba agua-hielo)
  - Test de seguridad gas (estanquesidad, llama)
acceptance:
  - Sin fugas, sin errores; estabilidad térmica <±2°C

---
id: dummy-ops-metrics-001
domain: operations
summary: Señales, métricas y accionables para analítica operativa.
signals:
  - low_water_quality
  - dirty_burners
  - worn_gaskets
metrics:
  - { name: "MTBF_horno", target: ">= 180 días" }
  - { name: "Tiempo_respuesta", target: "<= 24 h" }
actions:
  - Programar cambio de burletes con historial de fugas repetidas
  - Implementar protocolo de limpieza semanal en quemadores


