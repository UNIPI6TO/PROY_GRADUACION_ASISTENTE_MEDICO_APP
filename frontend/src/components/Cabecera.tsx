import React, { useState } from "react";
import {
  PhoneCall,
  ShieldAlert,
  RotateCcw,
  Activity,
  Menu,
  X,
  Info,
} from "lucide-react";

interface CabeceraProps {
  idSesion: string;
  onNuevaConversacion: () => void;
  onAbrirChecklist: () => void;
}

export const Cabecera: React.FC<CabeceraProps> = ({
  idSesion,
  onNuevaConversacion,
  onAbrirChecklist,
}) => {
  const [menuMovilAbierto, setMenuMovilAbierto] = useState<boolean>(false);
  const [modalAvisoAbierto, setModalAvisoAbierto] = useState<boolean>(() => {
    try {
      return window.sessionStorage.getItem("aviso_ia_aceptado") !== "1";
    } catch {
      return true;
    }
  });

  const alternarMenu = () => setMenuMovilAbierto((prev) => !prev);
  const cerrarMenu = () => setMenuMovilAbierto(false);

  const aceptarAviso = () => {
    try {
      window.sessionStorage.setItem("aviso_ia_aceptado", "1");
    } catch {
      // Ignorar errores de sessionStorage en entornos restringidos
    }
    setModalAvisoAbierto(false);
  };

  return (
    <>
      <header className="cabecera">
        <div className="cabecera-superior">
          {/* Botón flotante/menú para pantallas pequeñas en el lado superior izquierdo */}
          <div className="bloque-marca-menu">
            <button
              type="button"
              className="btn-flotante-menu-movil"
              onClick={alternarMenu}
              aria-label={menuMovilAbierto ? "Cerrar menú de opciones" : "Abrir menú de opciones de salud"}
              aria-expanded={menuMovilAbierto}
            >
              {menuMovilAbierto ? <X size={20} /> : <Menu size={20} />}
            </button>

            <div className="marca">
              <div className="icono-marca" aria-hidden="true">
                <Activity size={22} />
              </div>
              <div className="marca-textos">
                <h1>GuíaVital · Dengue y Arbovirosis</h1>
                <p className="subtitulo">
                  Orientación preventiva MSP / OPS · Cero Diagnóstico
                </p>
              </div>
            </div>
          </div>

          {/* Acciones de cabecera: "Nueva consulta" siempre visible; el resto se agrupa en el menú flotante en móviles */}
          <div className="acciones-cabecera">
            <button
              type="button"
              className="btn-secundario btn-nueva-siempre-visible"
              onClick={onNuevaConversacion}
              title={`Sesión anónima activa: ${idSesion.slice(0, 8)}`}
              aria-label="Iniciar nueva consulta"
            >
              <RotateCcw size={16} aria-hidden="true" />
              <span>Nueva consulta</span>
            </button>

            <div className="acciones-cabecera-desktop">
              <button
                type="button"
                className="btn-checklist"
                onClick={onAbrirChecklist}
                aria-label="Verificar signos de alarma de dengue"
              >
                <ShieldAlert size={18} aria-hidden="true" />
                <span>Signos de Alarma</span>
              </button>

              <a
                href="tel:911"
                className="btn-emergencia"
                aria-label="Llamar de emergencia al ECU 911"
              >
                <PhoneCall size={18} aria-hidden="true" />
                <span>Emergencia 911</span>
              </a>
            </div>
          </div>
        </div>

        {/* Aviso permanente visible en la primera pantalla (s4g) */}
        <div className="aviso-permanente desktop-only" role="note">
          <strong>Aviso de IA y Datos:</strong> Hablas con una IA que puede equivocarse y{" "}
          <strong>no reemplaza al médico</strong>. No guarda datos personales; solo conserva un ID
          anónimo de sesión y el historial temporal durante tu sesión activa.
          <button
            type="button"
            className="enlace-aviso-detalle"
            onClick={() => setModalAvisoAbierto(true)}
          >
            Ver condiciones
          </button>
        </div>
      </header>

      {/* Menú flotante desplegable para móviles / pantallas pequeñas (Lado Superior Izquierdo) */}
      {menuMovilAbierto && (
        <>
          <div
            className="backdrop-flotante-movil"
            onClick={cerrarMenu}
            aria-hidden="true"
          />
          <div
            className="panel-flotante-superior-izquierdo"
            role="dialog"
            aria-label="Menú rápido de opciones"
          >
            <div className="panel-flotante-cabecera">
              <span className="panel-flotante-titulo">Opciones de GuíaVital</span>
              <button
                type="button"
                className="btn-cerrar-panel"
                onClick={cerrarMenu}
                aria-label="Cerrar menú"
              >
                <X size={18} />
              </button>
            </div>

            <div className="panel-flotante-botones">
              <button
                type="button"
                className="btn-flotante-item item-alarma"
                onClick={() => {
                  cerrarMenu();
                  onAbrirChecklist();
                }}
              >
                <ShieldAlert size={18} />
                <div className="item-texto">
                  <strong>Signos de Alarma</strong>
                  <span>Evaluación clínica MSP</span>
                </div>
              </button>

              <button
                type="button"
                className="btn-flotante-item item-info"
                onClick={() => {
                  cerrarMenu();
                  setModalAvisoAbierto(true);
                }}
              >
                <Info size={18} />
                <div className="item-texto">
                  <strong>Aviso ético (Zero-PII)</strong>
                  <span>Políticas de privacidad y salud</span>
                </div>
              </button>

              <a
                href="tel:911"
                className="btn-flotante-item item-emergencia"
                onClick={cerrarMenu}
              >
                <PhoneCall size={18} />
                <div className="item-texto">
                  <strong>Llamar al ECU 911</strong>
                  <span>Atención de emergencia inmediata</span>
                </div>
              </a>
            </div>
          </div>
        </>
      )}

      {/* Pop-up de Aviso al Usuario y Condiciones de Uso (s4g) */}
      {modalAvisoAbierto && (
        <div
          className="modal-backdrop"
          role="dialog"
          aria-modal="true"
          aria-labelledby="titulo-aviso-privacidad"
        >
          <div className="modal-contenedor modal-aviso-corto">
            <div className="modal-cabecera">
              <h2 id="titulo-aviso-privacidad">
                <Info size={22} aria-hidden="true" />
                <span>Aviso de IA y Tratamiento de Datos</span>
              </h2>
              <button
                type="button"
                className="btn-cerrar"
                onClick={aceptarAviso}
                aria-label="Cerrar aviso"
              >
                <X size={20} />
              </button>
            </div>

            <div className="contenido-aviso-modal">
              <div className="caja-alerta-medica">
                Antes de usar <strong>GuíaVital</strong>, ten en cuenta estas condiciones:
              </div>

              <ul>
                <li>
                  <strong>Hablas con una IA:</strong> Este asistente usa Inteligencia Artificial
                  basada en guías del MSP y la OPS. <strong>Puede equivocarse</strong>.
                </li>
                <li>
                  <strong>No reemplaza al profesional de salud:</strong> Es solo orientativo; no
                  diagnostica ni receta (evita automedicarte con ibuprofeno o aspirina). Ante
                  síntomas críticos, acude a un centro médico o llama al 911.
                </li>
                <li>
                  <strong>Qué datos guarda y por cuánto tiempo:</strong> No solicita ni almacena
                  datos personales (Zero-PII). Solo guarda un código de sesión anónimo en tu
                  navegador (<code>sessionStorage</code>, se borra al cerrar la pestaña) y los
                  mensajes de la conversación temporalmente durante la vigencia de la sesión e
                  instancia activa.
                </li>
              </ul>

              <div className="modal-pie">
                <button
                  type="button"
                  className="btn-primario-modal"
                  onClick={aceptarAviso}
                >
                  Acepto las condiciones
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
