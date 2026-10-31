/**
 * Este archivo representa el contrato OpenAPI 3.1 publicado por FastAPI (/openapi.json).
 * Se actualiza con: npm run tipos (npx openapi-typescript http://localhost:8000/openapi.json -o src/api/esquema.ts)
 */

export interface paths {
  "/api/v1/chat": {
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["Solicitud"];
        };
      };
      responses: {
        /** @description Successful Response */
        200: {
          content: {
            "application/json": components["schemas"]["RespuestaChat"];
          };
        };
        /** @description Solicitud inválida */
        422: {
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
        /** @description Demasiadas solicitudes */
        429: {
          headers: {
            "Retry-After"?: string;
          };
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
        /** @description Servicio no disponible */
        503: {
          headers: {
            "Retry-After"?: string;
          };
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
      };
    };
  };
  "/manage/health": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": Record<string, unknown>;
          };
        };
      };
    };
  };
  "/manage/info": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": Record<string, string>;
          };
        };
      };
    };
  };
  "/herramientas/signos-alarma": {
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["EvaluarSignosAlarmaHttpIn"];
        };
      };
      responses: {
        200: {
          content: {
            "application/json": components["schemas"]["EvaluarSignosAlarmaHttpOut"];
          };
        };
        422: {
          content: {
            "application/json": components["schemas"]["ErrorValidacionPydantic"];
          };
        };
      };
    };
  };
  "/api/v2/chat": {
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["Solicitud"];
        };
      };
      responses: {
        200: {
          content: {
            "application/json": components["schemas"]["RespuestaChatV2"];
          };
        };
        422: {
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
        429: {
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
        503: {
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
      };
    };
  };
  "/api/v2/chat/confirmar": {
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["SolicitudConfirmacion"];
        };
      };
      responses: {
        200: {
          content: {
            "application/json": components["schemas"]["RespuestaChatV2"];
          };
        };
        422: {
          content: {
            "application/problem+json": components["schemas"]["ProblemaRFC9457"];
          };
        };
      };
    };
  };
}

export interface components {
  schemas: {
    /** @description Cita documental oficial (MSP / OPS) */
    Fuente: {
      documento: string;
      seccion: string | null;
    };
    /** @description Formato de error estándar (Problem Details for HTTP APIs - RFC 9457) */
    ProblemaRFC9457: {
      type: string;
      title: string;
      status: number;
      detail: string;
      instance: string;
    };
    /** @description Error de validación de Pydantic para endpoints de herramientas */
    ErrorValidacionPydantic: {
      detail: Array<{
        loc: (string | number)[];
        msg: string;
        type: string;
      }>;
    };
    /** @description Respuesta completa del endpoint de chat hacia el cliente/frontend */
    RespuestaChat: {
      respuesta: string;
      se_abstiene: boolean;
      derivar_a?: string | null;
      fuentes?: components["schemas"]["Fuente"][];
      proveedor?: string | null;
    };
    /** @description Lo que envía el usuario. Límite de tamaño = defensa contra consumo excesivo (OWASP LLM10) */
    Solicitud: {
      /** @description ID de la sesión del usuario (letras, números, '-' o '_', máx. 64) */
      idSesion: string;
      /** @description Consulta del usuario (5 a 2000 caracteres) */
      texto: string;
    };
    /** @description Entrada para la herramienta de signos de alarma de la Semana 3 */
    EvaluarSignosAlarmaHttpIn: {
      dias_fiebre: number;
      dolor_abdominal: boolean;
      vomitos_persistentes: boolean;
      sangrado: boolean;
      edad: number;
    };
    /** @description Salida de la herramienta de signos de alarma de la Semana 3 */
    EvaluarSignosAlarmaHttpOut: {
      signos_presentes: number;
      nivel: "alarma" | "vigilancia" | "sin_alarma" | string;
      recomendacion: string;
      fuente: string;
    };
    /** @description Estados posibles del agente v2 */
    EstadoAgente: "completado" | "requiere_confirmacion" | "tope_alcanzado";
    /** @description Acción que requiere autorización humana antes de ejecutarse */
    AccionPendiente: {
      tool_call_id: string;
      nombre_herramienta: string;
      argumentos: Record<string, unknown>;
      advertencia?: string;
    };
    /** @description Respuesta del Agente v2 con function calling y human-in-the-loop */
    RespuestaChatV2: {
      idSesion: string;
      estado: components["schemas"]["EstadoAgente"];
      respuesta?: string | null;
      accion_pendiente?: components["schemas"]["AccionPendiente"] | null;
      fuentes?: components["schemas"]["Fuente"][];
      vueltas_usadas?: number;
    };
    /** @description Decisión humana para autorizar o rechazar una acción del agente */
    SolicitudConfirmacion: {
      idSesion: string;
      tool_call_id: string;
      aprobado: boolean;
    };
  };
}
