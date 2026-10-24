import { describe, it, expect } from "vitest";
import { transicionarEstado, type EstadoInterfaz } from "../src/types/estados";
import { extraerEventosSSE } from "../src/api/cliente";

describe("Reto 1 y 3 · Máquina de 7 Estados y Parser SSE de Eventos Partidos", () => {
  it("inicia en estado 'inactiva' y transiciona a 'enviando' al enviar consulta", () => {
    const inicial: EstadoInterfaz = { tipo: "inactiva" };
    const enviando = transicionarEstado(inicial, { tipo: "ENVIAR" });
    expect(enviando).toEqual({ tipo: "enviando" });
  });

  it("acumula fragmentos progresivamente en el estado 'recibiendo'", () => {
    let estado: EstadoInterfaz = { tipo: "enviando" };
    estado = transicionarEstado(estado, { tipo: "TOKEN_RECIBIDO", fragmento: "El dengue " });
    expect(estado).toEqual({ tipo: "recibiendo", texto: "El dengue " });

    estado = transicionarEstado(estado, {
      tipo: "TOKEN_RECIBIDO",
      fragmento: "requiere hidratación.",
    });
    expect(estado).toEqual({
      tipo: "recibiendo",
      texto: "El dengue requiere hidratación.",
    });
  });

  it("transiciona a 'completa' cuando la respuesta 200 no se abstiene ni deriva", () => {
    const respuesta = {
      respuesta: "Lava y cepilla los tanques de agua cada semana.",
      se_abstiene: false,
      derivar_a: null,
      fuentes: [{ documento: "Guía MSP Control Vectorial", seccion: "Prevención" }],
      proveedor: "gemini",
    };

    const estado = transicionarEstado(
      { tipo: "enviando" },
      { tipo: "RESPUESTA_COMPLETA", respuesta }
    );

    expect(estado.tipo).toBe("completa");
    if (estado.tipo === "completa") {
      expect(estado.respuesta.respuesta).toContain("Lava y cepilla");
    }
  });

  it("transiciona a 'revision' (200 + revisión humana/derivación) cuando se_abstiene es true", () => {
    const respuesta = {
      respuesta: "El dolor abdominal continuo es un signo de alarma.",
      se_abstiene: true,
      derivar_a: "Centro de Salud MSP / Emergencias 911",
      fuentes: [],
      proveedor: "gemini",
    };

    const estado = transicionarEstado(
      { tipo: "enviando" },
      { tipo: "RESPUESTA_COMPLETA", respuesta }
    );

    expect(estado.tipo).toBe("revision");
    if (estado.tipo === "revision") {
      expect(estado.motivo).toBe("Centro de Salud MSP / Emergencias 911");
    }
  });

  it("gestiona la cuenta regresiva en el estado 'reintentar' (429) hasta volver a 'inactiva'", () => {
    let estado = transicionarEstado(
      { tipo: "enviando" },
      {
        tipo: "ERROR_429",
        segundos: 2,
        detalle: "Límite por minuto excedido",
        textoConservado: "Consulta conservada",
      }
    );

    expect(estado.tipo).toBe("reintentar");
    if (estado.tipo === "reintentar") {
      expect(estado.segundos).toBe(2);
      expect(estado.textoConservado).toBe("Consulta conservada");
    }

    estado = transicionarEstado(estado, { tipo: "TICK_CUENTA_REGRESIVA" });
    expect(estado.tipo).toBe("reintentar");
    if (estado.tipo === "reintentar") {
      expect(estado.segundos).toBe(1);
    }

    estado = transicionarEstado(estado, { tipo: "TICK_CUENTA_REGRESIVA" });
    expect(estado.tipo).toBe("inactiva");
  });

  it("parsea correctamente eventos SSE partidos en múltiples trozos de red", () => {
    // Primer trozo cortado a la mitad de un evento
    const trozo1 = "event: token\ndata: El mosquito Aedes\n\nevent: tok";
    const paso1 = extraerEventosSSE("", trozo1);

    expect(paso1.eventos).toHaveLength(1);
    expect(paso1.eventos[0]).toEqual({
      evento: "token",
      datos: "El mosquito Aedes",
    });
    expect(paso1.restoBuffer).toBe("event: tok");

    // Segundo trozo que completa el evento anterior y envía fin
    const trozo2 =
      'en\ndata:  aegypti.\n\nevent: fin\ndata: {"respuesta":"El mosquito Aedes aegypti.","se_abstiene":false}\n\n';
    const paso2 = extraerEventosSSE(paso1.restoBuffer, trozo2);

    expect(paso2.eventos).toHaveLength(2);
    expect(paso2.eventos[0]).toEqual({
      evento: "token",
      datos: " aegypti.",
    });
    expect(paso2.eventos[1].evento).toBe("fin");
    expect(paso2.restoBuffer).toBe("");
  });
});
