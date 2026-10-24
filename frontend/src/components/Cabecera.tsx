import React from "react";
import { PhoneCall, ShieldAlert, RotateCcw, Activity } from "lucide-react";

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
  return (
    <header className="cabecera">
      <div className="cabecera-superior">
        <div className="marca">
          <div className="icono-marca" aria-hidden="true">
            <Activity size={24} />
          </div>
          <div>
            <h1>GuíaVital · Orientación sobre Dengue</h1>
            <p className="subtitulo">
              Asistente preventivo basado en guías del MSP Ecuador y OPS · Cero Diagnóstico
            </p>
          </div>
        </div>

        <div className="acciones-cabecera">
          <button
            type="button"
            className="btn-checklist"
            onClick={onAbrirChecklist}
            aria-label="Verificar signos de alarma de dengue"
          >
            <ShieldAlert size={18} aria-hidden="true" />
            <span>Signos de Alarma</span>
          </button>

          <button
            type="button"
            className="btn-secundario"
            onClick={onNuevaConversacion}
            title={`Sesión anónima activa: ${idSesion.slice(0, 8)}`}
          >
            <RotateCcw size={16} aria-hidden="true" />
            <span>Nueva consulta</span>
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

      <div className="aviso-permanente" role="note">
        <strong>Aviso ético y de privacidad (Zero-PII):</strong> Esta herramienta usa IA generativa
        únicamente para orientación preventiva. <strong>Nunca diagnostica ni receta medicamentos</strong>{" "}
        (evite automedicarse con ibuprofeno, aspirina o diclofenaco). No ingrese nombres, cédulas ni
        direcciones. Ante dolor abdominal intenso, vómitos persistentes o sangrado, acuda de inmediato
        al centro de salud.
      </div>
    </header>
  );
};
