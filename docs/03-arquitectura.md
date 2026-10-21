# Arquitectura · GuíaVital

**Caso 05:** Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis
**Tipo de producto:** Asistente conversacional con RAG y salvaguardas
**Repositorio:** https://github.com/UNIPI6TO/PROY_GRADUACION_ASISTENTE_MEDICO_APP
**Etapa:** Semana 2 · Construcción del MVP e integración con IA generativa

## Problema

La aplicación resuelve el problema de las complicaciones graves por dengue asociadas a la consulta médica tardía y la falta de comprensión ciudadana sobre las guías de salud oficiales. Mediante un asistente de orientación preventivo, busca evitar la saturación del sistema sanitario y promover la búsqueda oportuna de atención cuando aparecen signos de alarma.

## Equipo

| Integrante | Rol |
|---|---|
| Luis Cahuana | Tech Lead |
| Wilson Salinas | Builder |
| Rafael Minaya | QA / Seguridad |

## Diagrama de contexto (C4 nivel 1)

```mermaid
flowchart LR
  U0(["Ciudadano"])
  U1(["Familiar del Enfermo"])
  SYS["<b>GuíaVital</b><br/>Sistema de software"]
  P1["Google Gemini (AI Studio)<br/>gemini-2.0-flash"]
  P2["Groq<br/>llama-3.1-8b-instant"]
  E0["Registro de establecimientos MSP<br/>semana 3"]
  U0 -- usa --> SYS
  U1 -- usa --> SYS
  SYS -- "genera texto" --> P1
  SYS -. "respaldo" .-> P2
  SYS -. "semana 3" .-> E0
  classDef ext fill:#eceff1,stroke:#607d8b
  classDef sys fill:#dcebf3,stroke:#145c80
  classDef fut fill:#f6e9d8,stroke:#a8641a,stroke-dasharray:5 5
  class SYS sys
  class P1,P2 ext
  class E0 fut
```

## Diagrama de contenedores (C4 nivel 2)

Los elementos con borde punteado naranja llegan en la semana 3.

```mermaid
flowchart LR
  U0(["Ciudadano"])
  U1(["Familiar del Enfermo"])
  subgraph SYS["GuíaVital"]
    FE["Frontend<br/>React + Vite"]
    BE["Backend API<br/>FastAPI (Python)<br/>POST /api/chat<br/>GET /manage/health<br/>POST /manage/info"]
    LLM["Servicio IA · llm.py<br/>tiempo límite, reintentos, respaldo"]
    PR[("app/prompts/")]
    DB[("SQLite")]
    OB["Registro: Logs estructurados sin datos personales"]
    VEC[("Base vectorial RAG<br/>semana 3")]
    AG["Agente y herramientas<br/>semana 3"]
  end
  P1["Google Gemini (AI Studio)<br/>gemini-2.0-flash"]
  P2["Groq<br/>llama-3.1-8b-instant"]
  E0["Registro de establecimientos MSP"]
  U0 --> FE
  U1 --> FE
  FE -- "HTTPS / JSON" --> BE
  BE --> LLM
  LLM -- API --> P1
  LLM -. respaldo .-> P2
  BE --> PR
  BE --> DB
  BE --> OB
  BE -.-> AG
  AG -.-> VEC
  BE -.-> E0
  classDef fut fill:#f6e9d8,stroke:#a8641a,stroke-dasharray:5 5
  classDef ext fill:#eceff1,stroke:#607d8b
  class VEC,AG fut
  class P1,P2 ext
  class E0 fut
```

## Tecnologías

| Contenedor | Tecnología |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Datos | SQLite |
| Modelo principal | Google Gemini (AI Studio) · gemini-2.0-flash |
| Modelo de respaldo | Groq · llama-3.1-8b-instant |
| Patrón de integración | Enrutamiento por tipo de consulta |
| Registro | Logs estructurados sin datos personales |
| Despliegue previsto | _Por decidir_ |

## Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/chat` | Orientación con salvaguardas; deriva ante signos de alarma |
| GET | `/manage/health` | Estado del servicio |
| POST | `/manage/info` | Información de la versión del servicio |

## Prompts versionados

| Archivo | Qué cambia en esta versión |
|---|---|
| `app/prompts/system_v1.md` | No diagnosticar, no recetar, derivar ante signos de alarma |

## Requisitos no funcionales de IA

| Requisito | Presupuesto |
|---|---|
| Tiempo de respuesta | ≤ 3 s |
| Tokens máximos de salida | 600 |
| Temperatura | 0.2 |
| Caracteres máximos de entrada | 2000 |
| Solicitudes por minuto por usuario | 10 |
| Si el proveedor falla | Reintentar con espera creciente; si sigue fallando, usar el proveedor de respaldo y avisar al usuario |

## Semana 3: herramientas del agente (previstas)

- `evaluar_signos_alarma(respuestas)`
- `ubicar_establecimiento(ciudad)`

## Decisiones de arquitectura

Ver `docs/09-decisiones.md`: ADR-001 Proveedor y modelo generativo (Propuesto); ADR-002 Patrón de integración: workflow o agente (Propuesto); ADR-003 Manejo de claves y datos personales (Propuesto); ADR-004 Signos de alarma por reglas, no por el modelo (Propuesto).

## Uso de la plantilla

Partieron de la propuesta de la plantilla en: Prompts, Requisitos no funcionales. El grupo la revisó y ajustó.
