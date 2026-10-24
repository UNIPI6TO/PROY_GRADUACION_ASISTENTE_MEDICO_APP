import React, { useState } from "react";
import { ShieldAlert, CheckCircle2, PhoneCall, X } from "lucide-react";

interface SignoAlarma {
  id: string;
  titulo: string;
  descripcion: string;
}

const SIGNOS_ALARMA_OPS: SignoAlarma[] = [
  {
    id: "dolor_abdominal",
    titulo: "Dolor abdominal intenso y continuo",
    descripcion: "Dolor fuerte en la boca del estómago o abdomen que no cede.",
  },
  {
    id: "vomitos",
    titulo: "Vómitos persistentes",
    descripcion: "Tres o más episodios en 1 hora, o cuatro en 6 horas (impide hidratarse).",
  },
  {
    id: "sangrado",
    titulo: "Sangrado de mucosas",
    descripcion: "Sangrado por encías, nariz, vómito con sangre o heces oscuras.",
  },
  {
    id: "letargo",
    titulo: "Somnolencia extrema o irritabilidad",
    descripcion: "Decaimiento severo, dificultad para despertar o confusión.",
  },
  {
    id: "mareo_postural",
    titulo: "Mareo o desmayo al ponerse de pie",
    descripcion: "Hipotensión postural (sensación de desvanecimiento al levantarse).",
  },
  {
    id: "liquidos",
    titulo: "Dificultad respiratoria o acumulación de líquidos",
    descripcion: "Hinchazón abdominal marcada o falta de aire.",
  },
];

interface ChecklistSignosAlarmaProps {
  abierto: boolean;
  onCerrar: () => void;
}

/**
 * Herramienta determinista en cliente (ADR-004 y HU-04):
 * La evaluación de signos de alarma usa reglas booleanas rígidas, nunca inferencia libre del LLM.
 */
export const ChecklistSignosAlarma: React.FC<ChecklistSignosAlarmaProps> = ({
  abierto,
  onCerrar,
}) => {
  const [seleccionados, setSeleccionados] = useState<Record<string, boolean>>({});

  if (!abierto) return null;

  const alternarSigno = (id: string) => {
    setSeleccionados((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const totalActivos = Object.values(seleccionados).filter(Boolean).length;
  const hayPeligro = totalActivos > 0;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="titulo-checklist"
    >
      <div className="modal-contenedor">
        <div className="modal-cabecera">
          <h2 id="titulo-checklist">
            <ShieldAlert size={22} aria-hidden="true" />
            <span>Lista de Verificación de Signos de Alarma (OPS / MSP)</span>
          </h2>
          <button
            type="button"
            className="btn-cerrar"
            onClick={onCerrar}
            aria-label="Cerrar lista de verificación"
          >
            <X size={20} />
          </button>
        </div>

        <p className="modal-instruccion">
          Marque si el paciente con sospecha de dengue presenta <strong>cualquiera</strong> de los
          siguientes signos clínicos (especialmente cuando empieza a bajar la fiebre, entre el 3.°
          y 7.° día):
        </p>

        <ul className="lista-signos">
          {SIGNOS_ALARMA_OPS.map((signo) => {
            const marcado = Boolean(seleccionados[signo.id]);
            return (
              <li key={signo.id} className={`item-signo ${marcado ? "marcado" : ""}`}>
                <label>
                  <input
                    type="checkbox"
                    checked={marcado}
                    onChange={() => alternarSigno(signo.id)}
                  />
                  <div>
                    <strong>{signo.titulo}</strong>
                    <span>{signo.descripcion}</span>
                  </div>
                </label>
              </li>
            );
          })}
        </ul>

        {hayPeligro ? (
          <div className="resultado-checklist peligro" role="alert">
            <ShieldAlert size={24} aria-hidden="true" />
            <div>
              <strong>¡ATENCIÓN MÉDICA URGENTE REQUERIDA! ({totalActivos} signo/s detectado/s)</strong>
              <p>
                La presencia de al menos un signo de alarma indica riesgo de dengue grave.{" "}
                <strong>No espere y no automedique.</strong> Traslade al paciente de inmediato al
                Hospital o Centro de Salud Tipo C del MSP más cercano o llame al ECU-911.
              </p>
              <a href="tel:911" className="btn-emergencia-inline">
                <PhoneCall size={16} aria-hidden="true" />
                <span>Llamar al 911 ahora</span>
              </a>
            </div>
          </div>
        ) : (
          <div className="resultado-checklist informativo" role="status">
            <CheckCircle2 size={22} aria-hidden="true" />
            <div>
              <strong>Sin signos de alarma marcados actualmente</strong>
              <p>
                Mantenga hidratación oral abundante, reposo bajo mosquitero y vigilancia continua
                cada 4 horas. Si aparece fiebre o cualquiera de los signos superiores, acuda al
                centro de salud del MSP.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
