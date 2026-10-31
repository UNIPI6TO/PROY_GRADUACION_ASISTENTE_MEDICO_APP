import React from "react";
import { AlertCircle, Clock, ServerCrash, RefreshCw } from "lucide-react";
import type { EstadoInterfaz } from "../types/estados";

interface AlertaEstadoProps {
  estado: EstadoInterfaz;
  onReintentar: () => void;
}

/**
 * Muestra la reacción prevista en la interfaz para cada error con contrato (Diapositivas 8 y 12).
 * Usa role="alert" para que el lector de pantalla anuncie inmediatamente errores 422, 429 y 503.
 */
export const AlertaEstado: React.FC<AlertaEstadoProps> = ({ estado, onReintentar }) => {
  if (estado.tipo === "invalido") {
    const tieneTextoConservado = Boolean(
      estado.textoConservado && estado.textoConservado.trim().length > 0
    );
    return (
      <div className="alerta-contrato alerta-422" role="alert">
        <AlertCircle size={20} aria-hidden="true" />
        <div className="alerta-contenido">
          <strong>Consulta incompleta o no válida:</strong>
          <p>
            {estado.detalle}
            {tieneTextoConservado
              ? " Tu mensaje se ha conservado en el cuadro inferior para que puedas completarlo."
              : ""}
          </p>
        </div>
      </div>
    );
  }

  if (estado.tipo === "reintentar") {
    return (
      <div className="alerta-contrato alerta-429" role="alert">
        <Clock size={20} aria-hidden="true" />
        <div className="alerta-contenido">
          <strong>Límite de consultas por minuto alcanzado (429):</strong>
          <p>
            {estado.detalle} Podrás reintentar en{" "}
            <strong data-testid="cuenta-regresiva">{estado.segundos} s</strong>. Tu consulta se
            conserva intacta.
          </p>
        </div>
      </div>
    );
  }

  if (estado.tipo === "caido") {
    return (
      <div className="alerta-contrato alerta-503" role="alert">
        <ServerCrash size={20} aria-hidden="true" />
        <div className="alerta-contenido">
          <strong>Servicio temporalmente no disponible (503):</strong>
          <p>
            {estado.detalle} Ningún proveedor pudo responder a tiempo. Tu mensaje sigue en el
            campo de texto para cuando desees volver a intentarlo.
          </p>
        </div>
        <button type="button" className="btn-reintentar" onClick={onReintentar}>
          <RefreshCw size={16} aria-hidden="true" />
          <span>Reintentar ahora</span>
        </button>
      </div>
    );
  }

  return null;
};
