import type { components } from "../api/esquema";

export type SolicitudChat = components["schemas"]["Solicitud"];
export type RespuestaChat = components["schemas"]["RespuestaChat"];
export type ProblemaRFC9457 = components["schemas"]["ProblemaRFC9457"];
export type Fuente = components["schemas"]["Fuente"];
export type AccionPendiente = components["schemas"]["AccionPendiente"];
export type EstadoAgente = components["schemas"]["EstadoAgente"];

/**
 * Los 7 estados de una interfaz de IA Generativa (Clase 4 · Diapositiva 4).
 * Unión discriminada para que los estados imposibles no se puedan escribir.
 */
export type EstadoInterfaz =
  | { tipo: "inactiva" }
  | { tipo: "enviando" }
  | { tipo: "recibiendo"; texto: string }
  | { tipo: "completa"; respuesta: RespuestaChat }
  | { tipo: "revision"; respuesta: RespuestaChat; motivo: string }
  | { tipo: "reintentar"; segundos: number; detalle: string; textoConservado: string }
  | { tipo: "caido"; segundos: number; detalle: string; textoConservado: string }
  | { tipo: "invalido"; detalle: string; textoConservado: string }
  | { tipo: "confirmacion_pendiente"; accion: AccionPendiente; textoUsuario: string };

export type AccionEstado =
  | { tipo: "ENVIAR" }
  | { tipo: "TOKEN_RECIBIDO"; fragmento: string }
  | { tipo: "RESPUESTA_COMPLETA"; respuesta: RespuestaChat }
  | { tipo: "REQUIERE_REVISION"; respuesta: RespuestaChat; motivo: string }
  | { tipo: "ERROR_422"; detalle: string; textoConservado: string }
  | { tipo: "ERROR_429"; segundos: number; detalle: string; textoConservado: string }
  | { tipo: "TICK_CUENTA_REGRESIVA" }
  | { tipo: "ERROR_503"; segundos: number; detalle: string; textoConservado: string }
  | { tipo: "ACCION_PENDIENTE"; accion: AccionPendiente; textoUsuario: string }
  | { tipo: "ABORTAR" }
  | { tipo: "REINICIAR" };

/**
 * Máquina de estados pura para transiciones deterministas de la interfaz.
 */
export function transicionarEstado(
  estadoActual: EstadoInterfaz,
  accion: AccionEstado
): EstadoInterfaz {
  switch (accion.tipo) {
    case "ENVIAR":
      return { tipo: "enviando" };

    case "TOKEN_RECIBIDO": {
      const previo = estadoActual.tipo === "recibiendo" ? estadoActual.texto : "";
      return {
        tipo: "recibiendo",
        texto: previo + accion.fragmento,
      };
    }

    case "RESPUESTA_COMPLETA":
      if (accion.respuesta.se_abstiene || accion.respuesta.derivar_a) {
        return {
          tipo: "revision",
          respuesta: accion.respuesta,
          motivo:
            accion.respuesta.derivar_a ||
            "Orientación derivada a personal de salud del MSP.",
        };
      }
      return {
        tipo: "completa",
        respuesta: accion.respuesta,
      };

    case "REQUIERE_REVISION":
      return {
        tipo: "revision",
        respuesta: accion.respuesta,
        motivo: accion.motivo,
      };

    case "ERROR_422":
      return {
        tipo: "invalido",
        detalle: accion.detalle,
        textoConservado: accion.textoConservado,
      };

    case "ERROR_429":
      return {
        tipo: "reintentar",
        segundos: Math.max(1, accion.segundos),
        detalle: accion.detalle,
        textoConservado: accion.textoConservado,
      };

    case "TICK_CUENTA_REGRESIVA":
      if (estadoActual.tipo !== "reintentar") {
        return estadoActual;
      }
      if (estadoActual.segundos <= 1) {
        return { tipo: "inactiva" };
      }
      return {
        ...estadoActual,
        segundos: estadoActual.segundos - 1,
      };

    case "ERROR_503":
      return {
        tipo: "caido",
        segundos: accion.segundos,
        detalle: accion.detalle,
        textoConservado: accion.textoConservado,
      };

    case "ACCION_PENDIENTE":
      return {
        tipo: "confirmacion_pendiente",
        accion: accion.accion,
        textoUsuario: accion.textoUsuario,
      };

    case "ABORTAR":
    case "REINICIAR":
      return { tipo: "inactiva" };

    default:
      return estadoActual;
  }
}

export interface MensajeHistorialUI {
  id: string;
  rol: "user" | "assistant";
  texto: string;
  seAbstiene?: boolean;
  derivarA?: string | null;
  fuentes?: Fuente[];
  proveedor?: string | null;
  valoracion?: "util" | "no_util" | null;
  accionPendiente?: AccionPendiente | null;
  estadoAgente?: EstadoAgente;
}
