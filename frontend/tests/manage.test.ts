/**
 * Pruebas unitarias para los endpoints de observabilidad SRE del frontend (manage/health y manage/info).
 * Valida la estricta paridad con el backend (app/main.py).
 */

import { describe, it, expect } from "vitest";
import {
  checkHealth,
  getInfo,
  APP_NAME,
  SEMVER_REGEX,
} from "../src/api/manage";

describe("SRE Management: checkHealth", () => {
  it("devuelve código HTTP 200 y status 'UP' en liveness y readiness por defecto", () => {
    const { payload, statusCode } = checkHealth();

    expect(statusCode).toBe(200);
    expect(payload.status).toBe("UP");
    expect(payload.checks.liveness.status).toBe("UP");
    expect(payload.checks.readiness.status).toBe("UP");
  });

  it("devuelve código HTTP 503 y readiness 'DOWN' si una sonda de preparación falla", () => {
    const sondaFallida = () => false;
    const { payload, statusCode } = checkHealth([sondaFallida]);

    expect(statusCode).toBe(503);
    expect(payload.status).toBe("DOWN");
    expect(payload.checks.liveness.status).toBe("UP");
    expect(payload.checks.readiness.status).toBe("DOWN");
  });

  it("devuelve código HTTP 503 si una sonda de preparación arroja una excepción", () => {
    const sondaConExcepcion = () => {
      throw new Error("Fallo de conexión a dependencia");
    };
    const { payload, statusCode } = checkHealth([sondaConExcepcion]);

    expect(statusCode).toBe(503);
    expect(payload.status).toBe("DOWN");
    expect(payload.checks.liveness.status).toBe("UP");
    expect(payload.checks.readiness.status).toBe("DOWN");
  });
});

describe("SRE Management: getInfo", () => {
  it("retorna el nombre de la aplicación y la versión en formato SemVer válido", () => {
    const { payload, statusCode } = getInfo();

    expect(statusCode).toBe(200);
    expect(payload.name).toBe(APP_NAME);
    expect(typeof payload.version).toBe("string");
    expect(SEMVER_REGEX.test(payload.version)).toBe(true);
  });

  it("admite parámetros personalizados y valida SemVer correctamente", () => {
    const { payload, statusCode } = getInfo("GuíaVital Custom", "1.5.0-SNAPSHOT-RC3");

    expect(statusCode).toBe(200);
    expect(payload.name).toBe("GuíaVital Custom");
    expect(payload.version).toBe("1.5.0-SNAPSHOT-RC3");
  });

  it("lanza un error si la versión no cumple con el estándar SemVer", () => {
    expect(() => getInfo("GuíaVital", "version-invalida")).toThrowError(
      /Versión inválida bajo SemVer/
    );
  });
});
