import React from "react";
import { ThumbsUp, ThumbsDown, AlertTriangle, BookOpen, Bot, User } from "lucide-react";
import type { MensajeHistorialUI } from "../types/estados";

interface MensajeChatProps {
  mensaje: MensajeHistorialUI;
  onValorar: (id: string, valor: "util" | "no_util") => void;
}

/**
 * Renderiza un turno de conversación cumpliendo OWASP LLM05 (texto plano seguro, nunca innerHTML)
 * y los criterios de confianza de la Clase 4 (Diapositiva 13):
 * - Etiqueta visible "Respuesta generada con IA"
 * - Estado de revisión humana / derivación médica como estado normal y sereno
 * - Espacio para fuentes del RAG (MSP / OPS)
 * - Evaluación básica con pulgares arriba / abajo
 */
export const MensajeChat: React.FC<MensajeChatProps> = ({ mensaje, onValorar }) => {
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

  return (
    <article
      className={`mensaje mensaje-asistente ${requiereDerivacion ? "mensaje-revision" : ""}`}
      aria-label="Respuesta del asistente GuíaVital"
    >
      <div className="mensaje-encabezado">
        <div className="etiqueta-ia">
          <Bot size={16} aria-hidden="true" />
          <span>Respuesta generada con IA</span>
          {mensaje.proveedor && (
            <span className="badge-proveedor" title="Proveedor del modelo">
              {mensaje.proveedor}
            </span>
          )}
        </div>
      </div>

      {/* Renderizado seguro (OWASP LLM05): React escapa el contenido en nodos de texto */}
      <p className="mensaje-texto">{mensaje.texto}</p>

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

      <div className="bloque-fuentes" aria-label="Fuentes documentales">
        <BookOpen size={15} aria-hidden="true" />
        {mensaje.fuentes && mensaje.fuentes.length > 0 ? (
          <ul className="lista-fuentes">
            {mensaje.fuentes.map((f, idx) => (
              <li key={`${f.documento}-${idx}`}>
                <strong>{f.documento}</strong>
                {f.seccion ? ` · ${f.seccion}` : ""}
              </li>
            ))}
          </ul>
        ) : (
          <span className="fuentes-pendientes">
            Fuentes oficiales MSP / OPS (espacio reservado para citas verificadas del RAG)
          </span>
        )}
      </div>

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
