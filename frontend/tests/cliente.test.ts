import { describe, it, expect, beforeAll, afterAll, afterEach } from "vitest";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { consultarAsistente, ErrorContratoAPI } from "../src/api/cliente";

const API_URL = "http://localhost:8000";

const server = setupServer(
  http.post(`${API_URL}/api/v1/chat`, async ({ request }) => {
    const body = (await request.json()) as { idSesion: string; texto: string };

    if (body.texto.length < 5) {
      return HttpResponse.json(
        {
          type: "/errores/422",
          title: "Solicitud inválida",
          status: 422,
          detail: "Revisa idSesion y texto (5 a 2000 caracteres).",
          instance: "/api/v1/chat",
        },
        {
          status: 422,
          headers: { "Content-Type": "application/problem+json" },
        }
      );
    }

    if (body.texto === "DISPARAR_429") {
      return HttpResponse.json(
        {
          type: "/errores/429",
          title: "Demasiadas solicitudes",
          status: 429,
          detail: "Espera un momento antes de volver a consultar.",
          instance: "/api/v1/chat",
        },
        {
          status: 429,
          headers: {
            "Content-Type": "application/problem+json",
            "Retry-After": "6",
          },
        }
      );
    }

    if (body.texto === "DISPARAR_503") {
      return HttpResponse.json(
        {
          type: "/errores/503",
          title: "Servicio no disponible",
          status: 503,
          detail: "Ningún proveedor responde en este momento.",
          instance: "/api/v1/chat",
        },
        {
          status: 503,
          headers: {
            "Content-Type": "application/problem+json",
            "Retry-After": "30",
          },
        }
      );
    }

    if (body.texto === "DISPARAR_STREAM") {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode("event: token\ndata: Acuda al \n\n"));
          controller.enqueue(encoder.encode("event: token\ndata: centro de salud.\n\n"));
          controller.enqueue(
            encoder.encode(
              'event: fin\ndata: {"respuesta":"Acuda al centro de salud.","se_abstiene":true,"derivar_a":"Centro de Salud MSP","fuentes":[]}\n\n'
            )
          );
          controller.close();
        },
      });
      return new HttpResponse(stream, {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      });
    }

    return HttpResponse.json({
      respuesta: "El dengue se transmite por la picadura del mosquito Aedes aegypti.",
      se_abstiene: false,
      derivar_a: null,
      fuentes: [{ documento: "Guía Clínica Dengue MSP", seccion: "Sección 1" }],
      proveedor: "gemini",
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("Reto 2, 4 y 5 · Contrato OpenAPI, Errores RFC 9457 y AbortController (MSW)", () => {
  it("procesa respuesta 200 tipada con fuentes oficiales del MSP", async () => {
    const r = await consultarAsistente(
      { idSesion: "sesion_valida_001", texto: "¿Cómo se transmite el dengue?" },
      { apiUrl: API_URL }
    );

    expect(r.se_abstiene).toBe(false);
    expect(r.respuesta).toContain("Aedes aegypti");
    expect(r.fuentes?.[0]?.documento).toBe("Guía Clínica Dengue MSP");
  });

  it("captura error 422 problem+json cuando los datos son inválidos", async () => {
    await expect(
      consultarAsistente({ idSesion: "sesion_valida_001", texto: "abc" }, { apiUrl: API_URL })
    ).rejects.toMatchObject({
      status: 422,
      problema: {
        title: "Solicitud inválida",
        detail: "Revisa idSesion y texto (5 a 2000 caracteres).",
      },
    });
  });

  it("lee la cabecera Retry-After cuando el backend responde 429 Too Many Requests", async () => {
    try {
      await consultarAsistente(
        { idSesion: "sesion_valida_001", texto: "DISPARAR_429" },
        { apiUrl: API_URL }
      );
      expect.fail("Debió lanzar ErrorContratoAPI 429");
    } catch (err) {
      expect(err).toBeInstanceOf(ErrorContratoAPI);
      const apiErr = err as ErrorContratoAPI;
      expect(apiErr.status).toBe(429);
      expect(apiErr.retryAfter).toBe(6);
    }
  });

  it("maneja 503 Service Unavailable cuando ningún proveedor responde", async () => {
    try {
      await consultarAsistente(
        { idSesion: "sesion_valida_001", texto: "DISPARAR_503" },
        { apiUrl: API_URL }
      );
      expect.fail("Debió lanzar ErrorContratoAPI 503");
    } catch (err) {
      const apiErr = err as ErrorContratoAPI;
      expect(apiErr.status).toBe(503);
      expect(apiErr.retryAfter).toBe(30);
      expect(apiErr.problema.detail).toContain("Ningún proveedor responde");
    }
  });

  it("procesa flujo SSE por POST y emite cada token al callback", async () => {
    const tokensRecibidos: string[] = [];
    const r = await consultarAsistente(
      { idSesion: "sesion_valida_001", texto: "DISPARAR_STREAM" },
      {
        apiUrl: API_URL,
        onToken: (t) => tokensRecibidos.push(t),
      }
    );

    expect(tokensRecibidos).toEqual(["Acuda al ", "centro de salud."]);
    expect(r.se_abstiene).toBe(true);
    expect(r.derivar_a).toBe("Centro de Salud MSP");
  });

  it("aborta la petición inmediatamente cuando se acciona AbortController (Botón Detener)", async () => {
    const ctrl = new AbortController();
    ctrl.abort();

    await expect(
      consultarAsistente(
        { idSesion: "sesion_valida_001", texto: "Consulta abortada" },
        { apiUrl: API_URL, signal: ctrl.signal }
      )
    ).rejects.toThrow();
  });
});
