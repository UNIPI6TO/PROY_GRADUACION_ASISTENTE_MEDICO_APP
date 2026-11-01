/**
 * Módulo de Observabilidad y Gestión Operativa SRE para el Frontend (GuíaVital).
 * Implementa la misma funcionalidad y especificación que el Backend (app/main.py):
 * - /manage/health: Diagnóstico de Liveness y Readiness (código 200 o 503).
 * - /manage/info: Metadatos de la aplicación y versión bajo SemVer oficial.
 */

import packageJson from "../../package.json";

export const APP_NAME = "GuíaVital";
export const APP_VERSION = packageJson.version;

export const SEMVER_REGEX =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;

export interface EstadoSonda {
  status: "UP" | "DOWN";
}

export interface DiagnosticoSalud {
  status: "UP" | "DOWN";
  checks: {
    liveness: EstadoSonda;
    readiness: EstadoSonda;
  };
}

export interface InformacionApp {
  name: string;
  version: string;
}

/**
 * Evalúa el estado de salud de la aplicación (Liveness y Readiness).
 *
 * - Liveness: 'UP' si el proceso está activo y respondiendo.
 * - Readiness: 'UP' si todas las sondas de preparación pasan con éxito; 'DOWN' si alguna falla.
 *
 * @param readinessProbes Lista opcional de funciones predicado que evalúan componentes dependientes.
 * @returns Tupla con el diagnóstico estructurado y el código de estado HTTP (200 o 503).
 */
export function checkHealth(
  readinessProbes?: Array<() => boolean>
): { payload: DiagnosticoSalud; statusCode: number } {
  const livenessStatus: "UP" | "DOWN" = "UP";
  let readinessStatus: "UP" | "DOWN" = "UP";

  if (readinessProbes && readinessProbes.length > 0) {
    for (const probe of readinessProbes) {
      try {
        if (!probe()) {
          readinessStatus = "DOWN";
          break;
        }
      } catch {
        readinessStatus = "DOWN";
        break;
      }
    }
  }

  const isHealthy = livenessStatus === "UP" && readinessStatus === "UP";
  const statusCode = isHealthy ? 200 : 503;

  const payload: DiagnosticoSalud = {
    status: isHealthy ? "UP" : "DOWN",
    checks: {
      liveness: { status: livenessStatus },
      readiness: { status: readinessStatus },
    },
  };

  return { payload, statusCode };
}

/**
 * Retorna la información y metadatos de versión de la aplicación.
 * Garantiza el cumplimiento del formato semántico SemVer.
 *
 * @param appName Nombre opcional de la aplicación (por defecto APP_NAME).
 * @param version Versión opcional SemVer (por defecto APP_VERSION o VITE_APP_VERSION).
 * @returns Tupla con el diccionario { name, version } y el código 200 OK.
 * @throws Error si la versión no cumple la especificación SemVer.
 */
export function getInfo(
  appName?: string,
  version?: string
): { payload: InformacionApp; statusCode: number } {
  const finalName = appName || APP_NAME;
  const rawVersion =
    version ||
    (typeof import.meta !== "undefined" && import.meta.env?.VITE_APP_VERSION) ||
    APP_VERSION;

  const finalVersion = String(rawVersion).trim();

  if (!SEMVER_REGEX.test(finalVersion)) {
    throw new Error(`Versión inválida bajo SemVer: ${finalVersion}`);
  }

  return {
    payload: {
      name: finalName,
      version: finalVersion,
    },
    statusCode: 200,
  };
}
