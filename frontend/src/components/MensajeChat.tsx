import React from "react";
import {
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  BookOpen,
  Bot,
  User,
  ShieldCheck,
  Check,
  X,
  Cpu,
} from "lucide-react";
import type { MensajeHistorialUI } from "../types/estados";

interface MensajeChatProps {
  mensaje: MensajeHistorialUI;
  onValorar: (id: string, valor: "util" | "no_util") => void;
  onConfirmarAccion?: (toolCallId: string, aprobado: boolean) => void;
}

/**
 * Convierte marcadores inline (**negrita** y *cursiva*) en nodos React seguros (<strong> y <em>)
 * sin usar innerHTML, manteniendo 100% de protección OWASP LLM05 contra XSS.
 */
function formatearEnLinea(texto: string): React.ReactNode[] {
  const partes = texto.split(/(\*\*[^*]+\*\*|\*[^*\n]+\*)/g);
  return partes.map((parte, idx) => {
    if (parte.startsWith("**") && parte.endsWith("**") && parte.length > 4) {
      return <strong key={idx}>{parte.slice(2, -2)}</strong>;
    }
    if (parte.startsWith("*") && parte.endsWith("*") && parte.length > 2) {
      return <em key={idx}>{parte.slice(1, -1)}</em>;
    }
    return parte;
  });
}

/**
 * Transforma párrafos, encabezados y listas con viñetas (- / *) en elementos semánticos React.
 */
export function renderizarTextoEstructurado(texto: string): React.ReactNode {
  const lineas = texto.split(/\r?\n/);
  const bloques: React.ReactNode[] = [];
  let itemsListaActual: React.ReactNode[] = [];
  let filasTablaActual: string[][] = [];
  let lineasCitaActual: string[] = [];

  const cerrarListaSiExiste = (claveBase: number) => {
    if (itemsListaActual.length > 0) {
      bloques.push(
        <ul key={`lista-${claveBase}`} className="mensaje-lista">
          {itemsListaActual}
        </ul>
      );
      itemsListaActual = [];
    }
  };

  const cerrarCitaSiExiste = (claveBase: number) => {
    if (lineasCitaActual.length === 0) return;

    const textoCompleto = lineasCitaActual.join("\n");
    const primera = lineasCitaActual.find((l) => l.trim().length > 0) || "";

    // Detectar si es una advertencia de salud / signos de alarma / atención ciudadana
    const esAdvertencia =
      /^(?:¡?ATENCI[OÓ]N!?|¡?ADVERTENCIA!?|IMPORTANTE:?|ALERTA:?|PELIGRO:?)/i.test(
        primera.trim().replace(/^[#*_\s!¡]+|[!¡:*_\s]+$/g, "")
      ) ||
      /emergencia|911|hospital|riesgo|signos? de alarma|contraindicad|no tomes|no tomar|aspirina|ibuprofeno|sangrado/i.test(
        textoCompleto
      );

    let titulo = "";
    const lineasRestantes = [...lineasCitaActual];

    // Si la primera línea es un título como ¡ATENCIÓN! o ADVERTENCIA:
    const matchTitulo = primera
      .trim()
      .match(/^(?:#{1,4}\s+|\*{1,2}|¡)?(ATENCI[OÓ]N|ADVERTENCIA|IMPORTANTE|ALERTA|RECUERDA)(?:!|\*{1,2}|:)?/i);

    if (matchTitulo) {
      titulo = primera.trim().replace(/^>\s*|[#*_]+/g, "");
      const primerIdx = lineasRestantes.findIndex((l) => l.trim().length > 0);
      if (primerIdx !== -1) {
        lineasRestantes.splice(primerIdx, 1);
      }
    }

    const elementosInternos: React.ReactNode[] = [];
    let itemsListaCita: React.ReactNode[] = [];

    const volcarItemsListaCita = (k: number) => {
      if (itemsListaCita.length > 0) {
        elementosInternos.push(
          <ul key={`cita-ul-${k}`} className="mensaje-lista lista-advertencia">
            {itemsListaCita}
          </ul>
        );
        itemsListaCita = [];
      }
    };

    lineasRestantes.forEach((subLinea, subIdx) => {
      const limpia = subLinea.trim();
      if (!limpia) {
        volcarItemsListaCita(subIdx);
        return;
      }

      // Viñeta dentro de la cita (- item o * item o • item)
      const matchVineta = limpia.match(/^[-*•]\s+(.+)$/);
      if (matchVineta) {
        itemsListaCita.push(
          <li key={`cita-li-${subIdx}`} className="item-advertencia">
            {formatearEnLinea(matchVineta[1])}
          </li>
        );
      } else {
        volcarItemsListaCita(subIdx);
        elementosInternos.push(
          <p key={`cita-p-${subIdx}`} className="mensaje-parrafo-advertencia">
            {formatearEnLinea(limpia)}
          </p>
        );
      }
    });

    volcarItemsListaCita(lineasRestantes.length);

    bloques.push(
      <aside
        key={`callout-${claveBase}`}
        className={`mensaje-callout ${
          esAdvertencia ? "mensaje-callout-advertencia" : "mensaje-callout-info"
        }`}
        role={esAdvertencia ? "alert" : "note"}
        aria-label={
          titulo ||
          (esAdvertencia ? "Advertencia de salud prioritaria" : "Nota informativa")
        }
      >
        <div className="callout-encabezado">
          <AlertTriangle size={18} className="callout-icono" aria-hidden="true" />
          <strong className="callout-titulo">
            {titulo || (esAdvertencia ? "Atención" : "Información Importante")}
          </strong>
          {esAdvertencia && (
            <span className="badge-advertencia-vital">Aviso importante</span>
          )}
        </div>
        <div className="callout-cuerpo">{elementosInternos}</div>
      </aside>
    );

    lineasCitaActual = [];
  };

  const cerrarTablaSiExiste = (claveBase: number) => {
    if (filasTablaActual.length > 0) {
      const [encabezado, ...cuerpo] = filasTablaActual;
      bloques.push(
        <div key={`tabla-cards-${claveBase}`} className="tarjetas-comparativas">
          {cuerpo.map((fila, fIdx) => {
            const tituloFila = fila[0] ?? "";
            const atributos = fila.slice(1);
            return (
              <div key={`card-${fIdx}`} className="tarjeta-comparativa-item">
                <div className="tarjeta-comparativa-titulo">
                  {formatearEnLinea(tituloFila)}
                </div>
                <div className="tarjeta-comparativa-cuerpo">
                  {atributos.map((valor, cIdx) => {
                    const nombreColumna = encabezado?.[cIdx + 1] ?? `Opción ${cIdx + 1}`;
                    return (
                      <div key={`attr-${fIdx}-${cIdx}`} className="fila-atributo-comparativo">
                        <span className="etiqueta-columna-comp">
                          {formatearEnLinea(nombreColumna)}:
                        </span>
                        <span className="valor-columna-comp">
                          {formatearEnLinea(valor)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      );
      filasTablaActual = [];
    }
  };

  lineas.forEach((lineaCruda, idx) => {
    const linea = lineaCruda.trim();

    if (!linea) {
      cerrarListaSiExiste(idx);
      cerrarTablaSiExiste(idx);
      cerrarCitaSiExiste(idx);
      return;
    }

    // Citas en bloque / Callouts de advertencia médica o atención ciudadana (> texto)
    if (linea.startsWith(">")) {
      cerrarListaSiExiste(idx);
      cerrarTablaSiExiste(idx);
      lineasCitaActual.push(linea.replace(/^>\s?/, ""));
      return;
    }

    cerrarCitaSiExiste(idx);

    // Filas de tabla Markdown (| celda 1 | celda 2 |)
    if (linea.startsWith("|") && linea.includes("|", 1)) {
      cerrarListaSiExiste(idx);
      // Ignorar fila separadora de tabla (|---|---|)
      if (/^\|[\s:|-]+\|?$/.test(linea) && linea.includes("-")) {
        return;
      }
      const celdas = linea
        .replace(/^\|/, "")
        .replace(/\|$/, "")
        .split("|")
        .map((c) => c.trim());
      if (celdas.length > 0) {
        filasTablaActual.push(celdas);
      }
      return;
    }

    cerrarTablaSiExiste(idx);

    // Separadores horizontales de Markdown (---, ***, ___)
    if (/^([-*_])(?:\s*\1){2,}$/.test(linea)) {
      cerrarListaSiExiste(idx);
      bloques.push(<hr key={`hr-${idx}`} className="mensaje-separador" />);
      return;
    }

    // Viñetas (- texto o * texto o • texto)
    const matchVineta = linea.match(/^[-*•]\s+(.+)$/);
    if (matchVineta) {
      const contenidoVineta = matchVineta[1];
      const esSubItem =
        /^\s{2,}/.test(lineaCruda) ||
        /^(?:\*\*)?(?:Direcci[oó]n|Tel[eé]fonos?|Horario|Atenci[oó]n|Referencia)/i.test(
          contenidoVineta
        );
      itemsListaActual.push(
        <li
          key={`item-${idx}`}
          className={esSubItem ? "mensaje-subitem" : undefined}
        >
          {formatearEnLinea(contenidoVineta)}
        </li>
      );
      return;
    }

    // Pasos numerados (1. texto) sin doble viñeta
    const matchNumero = linea.match(/^(\d+)\.\s+(.+)$/);
    if (matchNumero) {
      cerrarListaSiExiste(idx);
      bloques.push(
        <div key={`paso-${idx}`} className="mensaje-paso-numerado">
          <span className="paso-numero">{matchNumero[1]}.</span>
          <div className="paso-contenido">{formatearEnLinea(matchNumero[2])}</div>
        </div>
      );
      return;
    }

    cerrarListaSiExiste(idx);

    // Encabezados (# Título)
    const matchTitulo = linea.match(/^#{1,4}\s+(.+)$/);
    if (matchTitulo) {
      bloques.push(
        <p key={`sub-${idx}`} className="mensaje-subtitulo">
          <strong>{formatearEnLinea(matchTitulo[1])}</strong>
        </p>
      );
      return;
    }

    bloques.push(
      <p key={`p-${idx}`} className="mensaje-parrafo">
        {formatearEnLinea(linea)}
      </p>
    );
  });

  cerrarListaSiExiste(lineas.length);
  cerrarTablaSiExiste(lineas.length);
  cerrarCitaSiExiste(lineas.length);

  return <div className="mensaje-texto">{bloques}</div>;
}

/**
 * Renderiza un turno de conversación cumpliendo OWASP LLM05 (nodos React seguros, nunca innerHTML)
 * y los criterios de la Semana 3:
 * - Etiqueta visible "Respuesta generada con IA"
 * - Tarjeta Human-in-the-Loop para acciones pendientes del Agente v2 (/api/v2/chat)
 * - Estado de revisión humana / derivación médica como estado normal y sereno
 * - Espacio para fuentes del RAG (MSP / OPS)
 * - Evaluación básica con pulgares arriba / abajo
 */
export const MensajeChat: React.FC<MensajeChatProps> = ({
  mensaje,
  onValorar,
  onConfirmarAccion,
}) => {
  if (mensaje.rol === "user") {
    return (
      <article className="mensaje mensaje-usuario" aria-label="Consulta del usuario">
        <div className="mensaje-encabezado">
          <User size={16} aria-hidden="true" />
          <span>Tú</span>
        </div>
        <p className="mensaje-texto">{mensaje.texto}</p>
      </article>
    );
  }

  const requiereDerivacion = Boolean(mensaje.seAbstiene || mensaje.derivarA);
  const tieneAccionPendiente = Boolean(mensaje.accionPendiente);

  return (
    <article
      className={`mensaje mensaje-asistente ${
        requiereDerivacion ? "mensaje-revision" : ""
      } ${tieneAccionPendiente ? "mensaje-accion-pendiente" : ""}`}
      aria-label="Respuesta del asistente GuíaVital"
    >
      <div className="mensaje-encabezado">
        <div className="etiqueta-ia">
          {mensaje.estadoAgente ? <Cpu size={16} aria-hidden="true" /> : <Bot size={16} aria-hidden="true" />}
          <span>
            {mensaje.estadoAgente
              ? "Agente Inteligente"
              : "Respuesta generada con IA"}
          </span>
          {mensaje.proveedor && (
            <span className="badge-proveedor" title="Proveedor del modelo">
              {mensaje.proveedor}
            </span>
          )}
        </div>
      </div>

      {/* Renderizado estructurado y seguro (OWASP LLM05): convierte negritas, cursivas y viñetas */}
      {mensaje.texto && renderizarTextoEstructurado(mensaje.texto)}

      {/* Tarjeta de autorización humana (Semana 3 · Human-in-the-Loop / Agente v2) */}
      {tieneAccionPendiente && mensaje.accionPendiente && (
        <div className="bloque-confirmacion-agente" role="alert">
          <div className="encabezado-confirmacion">
            <ShieldCheck size={20} className="icono-confirmacion" />
            <div>
              <strong>Autorización Humana Requerida (Semana 3 · HITL)</strong>
              <p className="advertencia-hitl">
                {mensaje.accionPendiente.advertencia ||
                  "El agente solicita permiso para ejecutar la siguiente acción clínica:"}
              </p>
            </div>
          </div>

          <div className="detalle-herramienta-agente">
            <span className="nombre-herramienta">
              Herramienta: <code>{mensaje.accionPendiente.nombre_herramienta}</code>
            </span>
            <pre className="argumentos-herramienta">
              {JSON.stringify(mensaje.accionPendiente.argumentos, null, 2)}
            </pre>
          </div>

          {onConfirmarAccion && (
            <div className="botones-confirmacion-agente">
              <button
                type="button"
                className="btn-aprobar-accion"
                onClick={() =>
                  onConfirmarAccion(mensaje.accionPendiente!.tool_call_id, true)
                }
              >
                <Check size={16} />
                <span>Aprobar acción</span>
              </button>
              <button
                type="button"
                className="btn-rechazar-accion"
                onClick={() =>
                  onConfirmarAccion(mensaje.accionPendiente!.tool_call_id, false)
                }
              >
                <X size={16} />
                <span>Rechazar acción</span>
              </button>
            </div>
          )}
        </div>
      )}

      {requiereDerivacion && (
        <div className="bloque-revision" role="status">
          <AlertTriangle size={20} aria-hidden="true" />
          <div>
            <strong>Derivación / Revisión en Salud Pública:</strong>
            <p>
              {mensaje.derivarA
                ? `Se recomienda acudir o contactar a: ${mensaje.derivarA}`
                : "El asistente se abstiene de validar este caso. Un profesional de salud debe evaluarlo presencialmente."}
            </p>
          </div>
        </div>
      )}

      {mensaje.fuentes && mensaje.fuentes.length > 0 && (
        <div className="bloque-fuentes" aria-label="Fuentes documentales">
          <BookOpen size={15} aria-hidden="true" />
          <ul className="lista-fuentes">
            {mensaje.fuentes.map((f, idx) => (
              <li key={`${f.documento}-${idx}`}>
                <strong>{f.documento}</strong>
                {f.seccion ? ` · ${f.seccion}` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="bloque-feedback" aria-label="Evaluar calidad de la respuesta">
        <span className="feedback-label">¿Fue útil esta orientación?</span>
        <button
          type="button"
          className={`btn-pulgar ${mensaje.valoracion === "util" ? "activo" : ""}`}
          onClick={() => onValorar(mensaje.id, "util")}
          aria-pressed={mensaje.valoracion === "util"}
          aria-label="Respuesta útil (pulgar arriba)"
        >
          <ThumbsUp size={15} aria-hidden="true" />
          <span>Sí</span>
        </button>
        <button
          type="button"
          className={`btn-pulgar ${mensaje.valoracion === "no_util" ? "activo" : ""}`}
          onClick={() => onValorar(mensaje.id, "no_util")}
          aria-pressed={mensaje.valoracion === "no_util"}
          aria-label="Respuesta no útil (pulgar abajo)"
        >
          <ThumbsDown size={15} aria-hidden="true" />
          <span>No</span>
        </button>
      </div>
    </article>
  );
};
