# Changelog · Frontend GuíaVital

Todas las modificaciones notables del frontend de GuíaVital (Aplicación Web React + Vite + TypeScript) se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el frontend se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

## [0.2.0-SNAPSHOT-RC5] - 2026-11-01

- fix: (frontend) mejorar estado del botón Agente
- feat: (ci) mover quality gates a deploy y mejorar SemVer
- feat: (frontend) agregar endpoints SRE /manage/health e info
- chore: (changelog) separar bitácoras por aplicación
- feat: (app) integrar agente v2 y arbovirosis

## [0.2.0-SNAPSHOT-RC4] - 2026-11-01

- fix: (frontend) mejorar estado del botón Agente
- feat: (ci) mover quality gates a deploy y mejorar SemVer
- feat: (frontend) agregar endpoints SRE /manage/health e info
- chore: (changelog) separar bitácoras por aplicación
- feat: (app) integrar agente v2 y arbovirosis

## [0.2.0-SNAPSHOT-RC2] - 2026-10-31

### Conectividad y Resiliencia
- **Compatibilidad CORS**: Ajuste de llamadas HTTP para admitir orígenes locales (`localhost:5173`, `localhost:5174`) y cabeceras estrictas `Content-Type` y `Accept`.
- **Manejo de Errores de Red**: Manejo visual amigable de estados HTTP 503 (Servicio temporalmente no disponible) permitiendo reintento asistido.

---

## [0.2.0-SNAPSHOT-RC1] - 2026-10-31 (Semana 3)

### Integración con Agente Clínico v2
- **Contratos de API v2**: Consumo de `/api/v2/chat` con soporte para respuestas del agente orquestado y estados de atención extendidos.
- **Flujo Human-in-the-Loop (HITL)**:
  - Modal y tarjeta interactiva para confirmación de acciones sensibles (como `notificar_contacto_emergencia`).
  - Envío de decisión del usuario (`aprobado: true / false`) al endpoint `/api/v2/chat/confirmar`.
- **Componente de Checklist de Síntomas**:
  - Actualización de criterios clínicos alineados con el Manual SIVE-Alerta del MSP y Guía OPS.
  - Indicadores visuales de signos de alarma de consulta urgente.

### Seguridad y Calidad
- **Script de Detección de Secretos (`scripts/verificar-secretos.mjs`)**: Prevención de fugas de tokens o variables de entorno en el empaquetado de producción (`npm run build`).
- **Pruebas Automatizadas con Vitest**: Pruebas de renderizado de componentes y flujos de interacción del chat.

---

## [0.1.1] - 2026-10-24 (Semana 2)

### Interfaz de Usuario Conversacional
- **Arquitectura de Componentes**:
  - `Cabecera`: Identidad visual del Ministerio de Salud Pública / OPS y estado del servicio.
  - `MensajeChat`: Burbujas de mensajes accesibles con soporte Markdown y roles (usuario / asistente).
  - `AlertaEstado`: Banner contextual de riesgo y recomendaciones preventivas.
  - `ChecklistSignosAlarma`: Herramienta de autoevaluación guiada.
- **Semáforo de Riesgo Visual**:
  - Verde: Sin signos de alarma / Manejo ambulatorio y prevención.
  - Amarillo: Dengue con comorbilidades o criterios de vigilancia activa.
  - Rojo: Signos de alarma detectados / Advertencia prioritaria de acudir a urgencias.
- **Cliente API Tipado**:
  - Módulos `cliente.ts` y `esquema.ts` sincronizados con el esquema OpenAPI del backend.

### Accesibilidad (a11y)
- Cumplimiento de pautas WCAG: contraste de colores en alertas, navegación por teclado y etiquetas `aria-*` en controles de chat.

---

## [0.1.0] - 2026-10-17 (Semana 1)

### Inicialización del Proyecto Frontend
- Configuración inicial con React 18, Vite y TypeScript.
- Maquetación de la pantalla principal de orientación ciudadana sobre el dengue.
- Definición de requisitos visuales para el catálogo GeoSalud de centros de salud.
