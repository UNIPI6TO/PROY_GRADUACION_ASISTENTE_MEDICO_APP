import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import {
  sanitizarTextoModelo,
  esEnlaceSeguro,
  obtenerIdSesion,
} from "../src/api/cliente";
import { MensajeChat } from "../src/components/MensajeChat";
import { ChecklistSignosAlarma } from "../src/components/ChecklistSignosAlarma";
import { AlertaEstado } from "../src/components/AlertaEstado";

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
});
