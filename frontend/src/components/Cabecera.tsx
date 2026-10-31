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
  const [modalAvisoAbierto, setModalAvisoAbierto] = useState<boolean>(false);

  const alternarMenu = () => setMenuMovilAbierto((prev) => !prev);
  const cerrarMenu = () => setMenuMovilAbierto(false);

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

        {/* Aviso permanente solo visible en pantallas grandes o sintetizado */}
        <div className="aviso-permanente desktop-only" role="note">
          <strong>Aviso ético (Zero-PII):</strong> Asistente preventivo basado en guías del MSP.{" "}
          <strong>Nunca diagnostica ni receta</strong> (no automedicarse con ibuprofeno ni aspirina). No ingrese datos personales.
          <button
            type="button"
            className="enlace-aviso-detalle"
            onClick={() => setModalAvisoAbierto(true)}
          >
            Ver aviso completo
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

      {/* Modal accesible para el Aviso Ético y de Privacidad (Zero-PII) */}
      {modalAvisoAbierto && (
        <div
          className="modal-backdrop"
          role="dialog"
          aria-modal="true"
          aria-labelledby="titulo-aviso-privacidad"
        >
          <div className="modal-contenedor">
            <div className="modal-cabecera">
              <h2 id="titulo-aviso-privacidad">
                <Info size={22} aria-hidden="true" />
                <span>Aviso Ético y de Privacidad (Zero-PII)</span>
              </h2>
              <button
                type="button"
                className="btn-cerrar"
                onClick={() => setModalAvisoAbierto(false)}
                aria-label="Cerrar aviso ético"
              >
                <X size={20} />
              </button>
            </div>

            <div className="contenido-aviso-modal">
              <div className="caja-alerta-medica">
                <strong>Importante para su salud:</strong> Esta herramienta utiliza modelos de
                Inteligencia Artificial únicamente para orientación preventiva basada en las guías
                del Ministerio de Salud Pública del Ecuador (MSP) y la OPS.
              </div>

              <ul>
                <li>
                  <strong>Cero Diagnóstico y Cero Prescripción:</strong> GuíaVital nunca reemplaza
                  la consulta médica profesional ni emite recetas médicas.
                </li>
                <li>
                  <strong>Alerta de Automedicación:</strong> Evite automedicarse. El uso de
                  antiinflamatorios como <em>ibuprofeno</em>, <em>aspirina</em>, <em>diclofenaco</em> o
                  <em>naproxeno</em> está contraindicado ante sospecha de dengue por riesgo grave de
                  hemorragias.
                </li>
                <li>
                  <strong>Privacidad Zero-PII:</strong> No ingrese nombres propios, números de cédula,
                  direcciones ni información de contacto. El sistema opera de forma anónima mediante
                  un identificador aleatorio de sesión.
                </li>
                <li>
                  <strong>Signos de Alarma:</strong> Si presenta dolor abdominal intenso, vómitos
                  persistentes, sangrado de mucosas o decaimiento severo, acuda de inmediato al
                  Centro de Salud u Hospital más cercano o llame al 911.
                </li>
              </ul>

              <div className="modal-pie">
                <button
                  type="button"
                  className="btn-primario-modal"
                  onClick={() => setModalAvisoAbierto(false)}
                >
                  Entendido
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
