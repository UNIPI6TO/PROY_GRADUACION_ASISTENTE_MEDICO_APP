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
  };
}
