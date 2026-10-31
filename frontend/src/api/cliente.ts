import DOMPurify from "dompurify";
import type { components } from "./esquema";

export type Solicitud = components["schemas"]["Solicitud"];
export type RespuestaChat = components["schemas"]["RespuestaChat"];
export type ProblemaRFC9457 = components["schemas"]["ProblemaRFC9457"];
export type EvaluarSignosAlarmaHttpIn = components["schemas"]["EvaluarSignosAlarmaHttpIn"];
export type EvaluarSignosAlarmaHttpOut = components["schemas"]["EvaluarSignosAlarmaHttpOut"];
export type RespuestaChatV2 = components["schemas"]["RespuestaChatV2"];
export type AccionPendiente = components["schemas"]["AccionPendiente"];
export type SolicitudConfirmacion = components["schemas"]["SolicitudConfirmacion"];

const CLAVE_SESION_STORAGE = "sid";
const REGEX_SESION_VALIDA = /^[A-Za-z0-9_-]{6,64}$/;

/**
 * Obtiene la URL base del backend desde variables de entorno públicas de Vite.
 * Nunca contiene claves privadas (OWASP LLM02).
 */
export function obtenerUrlApi(): string {
  const envUrl = import.meta.env?.VITE_API_URL;
  return (envUrl ? String(envUrl).trim() : "http://localhost:8000").replace(/\/+$/, "");
}

/**
 * Gestiona el ID de sesión anónimo en sessionStorage (Clase 4 · Diapositiva 11 y ADR-003 Zero-PII).
 * El navegador guarda solo session_id; el historial vive en SQLite en el servidor.
 */
export function obtenerIdSesion(storage: Storage = window.sessionStorage): string {
  let sesion = storage.getItem(CLAVE_SESION_STORAGE);
  if (!sesion || !REGEX_SESION_VALIDA.test(sesion)) {
    sesion = crypto.randomUUID();
    storage.setItem(CLAVE_SESION_STORAGE, sesion);
  }
  return sesion;
}

/**
 * Reinicia la sesión actual generando un nuevo UUIDv4 en sessionStorage.
 */
export function reiniciarIdSesion(storage: Storage = window.sessionStorage): string {
  const nueva = crypto.randomUUID();
  storage.setItem(CLAVE_SESION_STORAGE, nueva);
  return nueva;
}

/**
 * Error tipado con soporte para RFC 9457 (Problem Details) y Retry-After.
 */
export class ErrorContratoAPI extends Error {
  public readonly status: number;
  public readonly problema: ProblemaRFC9457;
  public readonly retryAfter: number | null;

  constructor(status: number, problema: ProblemaRFC9457, retryAfter: number | null = null) {
    super(problema.detail || problema.title);
    this.name = "ErrorContratoAPI";
    this.status = status;
    this.problema = problema;
    this.retryAfter = retryAfter;
  }
}

export interface EventoSSE {
  evento: "token" | "fin" | "error";
  datos: string;
}

/**
 * Parser SSE para eventos partidos en la red (Clase 4 · Diapositiva 7).
 * Un trozo de red no equivale a un evento completo: acumula en buffer y separa por "\n\n".
 */
export function extraerEventosSSE(
  bufferActual: string,
  nuevoTrozo: string
): { eventos: EventoSSE[]; restoBuffer: string } {
  const acumulado = bufferActual + nuevoTrozo;
  const bloques = acumulado.split("\n\n");
  const restoBuffer = bloques.pop() ?? "";
  const eventos: EventoSSE[] = [];

  for (const bloque of bloques) {
    if (!bloque.trim()) continue;

    let tipoEvento: "token" | "fin" | "error" = "token";
    const lineasDatos: string[] = [];

    for (const linea of bloque.split("\n")) {
      if (linea.startsWith("event:")) {
        const valor = linea.slice(6).trim();
        if (valor === "token" || valor === "fin" || valor === "error") {
          tipoEvento = valor;
        }
      } else if (linea.startsWith("data:")) {
        const contenido = linea.startsWith("data: ") ? linea.slice(6) : linea.slice(5);
        lineasDatos.push(contenido);
      }
    }

    eventos.push({
      evento: tipoEvento,
      datos: lineasDatos.join("\n"),
    });
  }

  return { eventos, restoBuffer };
}

/**
 * Sanitiza cualquier texto de salida del modelo antes de mostrarlo si se requiere HTML seguro
 * (Clase 4 · Diapositiva 9 · OWASP LLM05 Improper Output Handling).
 */
export function sanitizarTextoModelo(texto: string): string {
  return DOMPurify.sanitize(texto, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "p", "ul", "ol", "li", "br"],
    ALLOWED_ATTR: [],
  });
}

/**
 * Valida que un enlace externo sea únicamente http o https (nunca javascript: o data:).
 */
export function esEnlaceSeguro(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" || parsed.protocol === "http:";
  } catch {
    return false;
  }
}

export interface OpcionesConsulta {
  apiUrl?: string;
  signal?: AbortSignal;
  onToken?: (fragmento: string) => void;
}

/**
 * Envía una consulta al endpoint POST /api/v1/chat cumpliendo el contrato OpenAPI.
 * Soporta respuesta JSON estructurada y streaming SSE con AbortController.
 */
export async function consultarAsistente(
  solicitud: Solicitud,
  opciones: OpcionesConsulta = {}
): Promise<RespuestaChat> {
  const base = opciones.apiUrl ?? obtenerUrlApi();
  const respuestaHttp = await fetch(`${base}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      idSesion: solicitud.idSesion,
      texto: solicitud.texto,
    }),
    signal: opciones.signal,
  });

  if (!respuestaHttp.ok) {
    const retryHeader = respuestaHttp.headers.get("Retry-After");
    const retryAfter = retryHeader ? parseInt(retryHeader, 10) : null;

    let problema: ProblemaRFC9457;
    try {
      problema = (await respuestaHttp.json()) as ProblemaRFC9457;
    } catch {
      problema = {
        type: `/errores/${respuestaHttp.status}`,
        title: "Error de comunicación",
        status: respuestaHttp.status,
        detail: "No se pudo completar la solicitud en este momento.",
        instance: "/api/v1/chat",
      };
    }

    throw new ErrorContratoAPI(
      respuestaHttp.status,
      problema,
      Number.isNaN(retryAfter) ? null : retryAfter
    );
  }

  const contentType = respuestaHttp.headers.get("content-type") || "";

  // Soporte para Streaming por POST si el backend emite text/event-stream (Diapositiva 7)
  if (contentType.includes("text/event-stream") && respuestaHttp.body) {
    const lector = respuestaHttp.body
      .pipeThrough(new TextDecoderStream())
      .getReader();

    let buf = "";
    let textoAcumulado = "";
    let respuestaFinal: RespuestaChat | null = null;

    while (true) {
      const { value, done } = await lector.read();
      if (done) break;
      const { eventos, restoBuffer } = extraerEventosSSE(buf, value);
      buf = restoBuffer;

      for (const ev of eventos) {
        if (ev.evento === "token") {
          textoAcumulado += ev.datos;
          opciones.onToken?.(ev.datos);
        } else if (ev.evento === "fin") {
          try {
            respuestaFinal = JSON.parse(ev.datos) as RespuestaChat;
          } catch {
            respuestaFinal = {
              respuesta: textoAcumulado,
              se_abstiene: false,
              derivar_a: null,
              fuentes: [],
              proveedor: null,
            };
          }
        } else if (ev.evento === "error") {
          throw new ErrorContratoAPI(503, {
            type: "/errores/stream",
            title: "Flujo interrumpido",
            status: 503,
            detail: ev.datos || "El flujo de respuesta se interrumpió.",
            instance: "/api/v1/chat",
          });
        }
      }
    }

    return (
      respuestaFinal ?? {
        respuesta: textoAcumulado,
        se_abstiene: false,
        derivar_a: null,
        fuentes: [],
        proveedor: null,
      }
    );
  }

  // Respuesta JSON estándar según contrato OpenAPI
  const datos = (await respuestaHttp.json()) as RespuestaChat;
  return datos;
}

/**
 * Consulta la herramienta oficial determinista de la Semana 3:
 * POST /herramientas/signos-alarma
 */
export async function evaluarSignosAlarmaHttp(
  datos: EvaluarSignosAlarmaHttpIn,
  apiUrl?: string
): Promise<EvaluarSignosAlarmaHttpOut> {
  const base = apiUrl ?? obtenerUrlApi();
  const respuestaHttp = await fetch(`${base}/herramientas/signos-alarma`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(datos),
  });

  if (!respuestaHttp.ok) {
    let mensaje = "No se pudo evaluar los signos de alarma clínicamente.";
    try {
      const errorJson = await respuestaHttp.json();
      if (Array.isArray(errorJson.detail)) {
        mensaje = errorJson.detail.map((e: { msg: string; loc?: string[] }) => e.msg).join("; ");
      } else if (typeof errorJson.detail === "string") {
        mensaje = errorJson.detail;
      }
    } catch {
      // Ignorar fallback
    }
    throw new ErrorContratoAPI(respuestaHttp.status, {
      type: `/errores/${respuestaHttp.status}`,
      title: "Error al evaluar signos de alarma",
      status: respuestaHttp.status,
      detail: mensaje,
      instance: "/herramientas/signos-alarma",
    });
  }

  return (await respuestaHttp.json()) as EvaluarSignosAlarmaHttpOut;
}

/**
 * Consulta el endpoint v2 del Agente con Function Calling y RAG (Semana 3):
 * POST /api/v2/chat
 */
export async function consultarAsistenteV2(
  solicitud: Solicitud,
  opciones: OpcionesConsulta = {}
): Promise<RespuestaChatV2> {
  const base = opciones.apiUrl ?? obtenerUrlApi();
  const respuestaHttp = await fetch(`${base}/api/v2/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      idSesion: solicitud.idSesion,
      texto: solicitud.texto,
    }),
    signal: opciones.signal,
  });

  if (!respuestaHttp.ok) {
    const retryHeader = respuestaHttp.headers.get("Retry-After");
    const retryAfter = retryHeader ? parseInt(retryHeader, 10) : null;

    let problema: ProblemaRFC9457;
    try {
      problema = (await respuestaHttp.json()) as ProblemaRFC9457;
    } catch {
      problema = {
        type: `/errores/${respuestaHttp.status}`,
        title: "Error del agente v2",
        status: respuestaHttp.status,
        detail: "No se pudo conectar con el agente inteligente.",
        instance: "/api/v2/chat",
      };
    }

    throw new ErrorContratoAPI(
      respuestaHttp.status,
      problema,
      Number.isNaN(retryAfter) ? null : retryAfter
    );
  }

  return (await respuestaHttp.json()) as RespuestaChatV2;
}

/**
 * Envía la decisión humana para aprobar o rechazar una acción pendiente del agente (Human-in-the-Loop):
 * POST /api/v2/chat/confirmar
 */
export async function confirmarAccionAgente(
  confirmacion: SolicitudConfirmacion,
  apiUrl?: string
): Promise<RespuestaChatV2> {
  const base = apiUrl ?? obtenerUrlApi();
  const respuestaHttp = await fetch(`${base}/api/v2/chat/confirmar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(confirmacion),
  });

  if (!respuestaHttp.ok) {
    let problema: ProblemaRFC9457;
    try {
      problema = (await respuestaHttp.json()) as ProblemaRFC9457;
    } catch {
      problema = {
        type: `/errores/${respuestaHttp.status}`,
        title: "Error de confirmación",
        status: respuestaHttp.status,
        detail: "No se pudo registrar la confirmación humana.",
        instance: "/api/v2/chat/confirmar",
      };
    }
    throw new ErrorContratoAPI(respuestaHttp.status, problema);
  }

  return (await respuestaHttp.json()) as RespuestaChatV2;
}
