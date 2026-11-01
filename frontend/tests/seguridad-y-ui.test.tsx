import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import {
  sanitizarTextoModelo,
  esEnlaceSeguro,
  obtenerIdSesion,
} from "../src/api/cliente";
import { MensajeChat } from "../src/components/MensajeChat";
import { ChecklistSignosAlarma } from "../src/components/ChecklistSignosAlarma";
import { AlertaEstado } from "../src/components/AlertaEstado";
import { Cabecera } from "../src/components/Cabecera";
import { App } from "../src/App";

describe("Reto 6, 7 y 8 · Seguridad OWASP LLM05, Sesión Anónima y Accesibilidad WCAG 2.2", () => {
  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it("OWASP LLM05: neutraliza payloads XSS en el texto del modelo y nunca ejecuta onerror", () => {
    const payloadMalicioso = '¡Gracias! <img src=x onerror="robar(document.cookie)">';
    const limpio = sanitizarTextoModelo(payloadMalicioso);

    expect(limpio).not.toContain("onerror");
    expect(limpio).not.toContain("<img");

    // Al renderizar en el componente MensajeChat, se muestra como texto inerte y no crea etiqueta img
    const { container } = render(
      <MensajeChat
        mensaje={{
          id: "m1",
          rol: "assistant",
          texto: payloadMalicioso,
          seAbstiene: false,
          fuentes: [],
        }}
        onValorar={() => {}}
      />
    );

    expect(container.querySelector("img")).toBeNull();
    expect(screen.getByText(/Respuesta generada con IA/i)).toBeInTheDocument();
  });

  it("OWASP LLM05: rechaza enlaces javascript: y solo permite http/https", () => {
    expect(esEnlaceSeguro("javascript:alert(1)")).toBe(false);
    expect(esEnlaceSeguro("data:text/html,<script>alert(1)</script>")).toBe(false);
    expect(esEnlaceSeguro("https://www.salud.gob.ec")).toBe(true);
  });

  it("Sesión Zero-PII: genera y conserva únicamente session_id en sessionStorage", () => {
    const id1 = obtenerIdSesion(window.sessionStorage);
    const id2 = obtenerIdSesion(window.sessionStorage);

    expect(id1).toBe(id2);
    expect(id1).toMatch(/^[A-Za-z0-9_-]{6,64}$/);
    expect(window.sessionStorage.getItem("sid")).toBe(id1);
  });

  it("Accesibilidad WAI-ARIA: anuncia errores 429 con role='alert' y muestra la cuenta regresiva", () => {
    render(
      <AlertaEstado
        estado={{
          tipo: "reintentar",
          segundos: 6,
          detalle: "Demasiadas solicitudes.",
          textoConservado: "Mi consulta",
        }}
        onReintentar={() => {}}
      />
    );

    const alerta = screen.getByRole("alert");
    expect(alerta).toBeInTheDocument();
    expect(screen.getByTestId("cuenta-regresiva")).toHaveTextContent("6 s");
  });

  it("Checklist determinista de signos de alarma (ADR-004): activa alerta urgente al marcar un signo", () => {
    render(<ChecklistSignosAlarma abierto={true} onCerrar={() => {}} />);

    expect(
      screen.getByText(/Sin signos de alarma marcados actualmente/i)
    ).toBeInTheDocument();

    const checkboxDolor = screen.getByLabelText(/Dolor abdominal intenso y continuo/i);
    fireEvent.click(checkboxDolor);

    const alertaUrgente = screen.getByRole("alert");
    expect(alertaUrgente).toHaveTextContent(/ATENCIÓN MÉDICA URGENTE REQUERIDA/i);
  });

  it("Semana 3 UI: Botón flotante superior izquierdo despliega opciones en pantallas pequeñas", () => {
    const fnChecklist = vi.fn();
    const fnNueva = vi.fn();

    render(
      <Cabecera
        idSesion="sesion_test_12345"
        onAbrirChecklist={fnChecklist}
        onNuevaConversacion={fnNueva}
      />
    );

    const btnMenu = screen.getByLabelText(/Abrir menú de opciones de salud/i);
    expect(btnMenu).toBeInTheDocument();

    // Al hacer clic, abre el panel flotante
    fireEvent.click(btnMenu);
    expect(screen.getByText(/Opciones de GuíaVital/i)).toBeInTheDocument();

    // Puede abrir signos de alarma desde el panel flotante
    const itemsAlarma = screen.getAllByText(/Signos de Alarma/i);
    fireEvent.click(itemsAlarma[itemsAlarma.length - 1]);
    expect(fnChecklist).toHaveBeenCalled();
  });

  it("Semana 3 HITL: Renderiza tarjeta de confirmación humana cuando el agente v2 lo requiere", () => {
    const fnConfirmar = vi.fn();

    render(
      <MensajeChat
        mensaje={{
          id: "m-agente-hitl",
          rol: "assistant",
          texto: "Requiere autorización:",
          accionPendiente: {
            tool_call_id: "call_123",
            nombre_herramienta: "buscar_centro_salud",
            argumentos: { parroquia: "Tarqui", tipo: "Tipo C" },
            advertencia: "Autorice la búsqueda del centro de salud.",
          },
          estadoAgente: "requiere_confirmacion",
        }}
        onValorar={() => {}}
        onConfirmarAccion={fnConfirmar}
      />
    );

    expect(screen.getByText(/Autorización Humana Requerida/i)).toBeInTheDocument();
    expect(screen.getByText(/buscar_centro_salud/i)).toBeInTheDocument();

    const btnAprobar = screen.getByRole("button", { name: /Aprobar acción/i });
    fireEvent.click(btnAprobar);
    expect(fnConfirmar).toHaveBeenCalledWith("call_123", true);
  });
it("Alternancia del botón Agente: inicia activo con 'Agente' e ícono, y al desactivar mantiene ícono y texto cambiando a inactivo", () => {
    // scrollIntoView mock for jsdom if needed
    window.HTMLElement.prototype.scrollIntoView = vi.fn();

    render(<App />);

    // 1. Estado inicial: debe iniciar activo, con texto 'Agente' y clase 'activo'
    const btnAgente = screen.getByRole("button", { name: /Modo Agente activo/i });
    expect(btnAgente).toBeInTheDocument();
    expect(btnAgente).toHaveTextContent("Agente");
    expect(btnAgente).toHaveClass("btn-modo-agente", "activo");
    expect(btnAgente).not.toHaveClass("inactivo");
    expect(btnAgente).toHaveAttribute("aria-pressed", "true");

    // 2. Al hacer clic (desactivar):
    fireEvent.click(btnAgente);

    // No debe cambiar el texto ni el ícono, solo el estado/color a inactivo
    expect(btnAgente).toHaveTextContent("Agente");
    expect(btnAgente).not.toHaveTextContent("RAG v1");
    expect(btnAgente).toHaveClass("btn-modo-agente", "inactivo");
    expect(btnAgente).not.toHaveClass("activo");
    expect(btnAgente).toHaveAttribute("aria-pressed", "false");
    expect(btnAgente).toHaveAttribute(
      "aria-label",
      "Modo Agente inactivo, usando versión 1"
    );

    // 3. Al hacer clic nuevamente vuelve a activarse
    fireEvent.click(btnAgente);
    expect(btnAgente).toHaveClass("btn-modo-agente", "activo");
    expect(btnAgente).not.toHaveClass("inactivo");
    expect(btnAgente).toHaveTextContent("Agente");
  });
});
