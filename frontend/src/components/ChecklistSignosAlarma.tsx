import React, { useState, useEffect } from "react";
import { ShieldAlert, CheckCircle2, PhoneCall, X, AlertTriangle } from "lucide-react";
import { evaluarSignosAlarmaHttp, type EvaluarSignosAlarmaHttpOut } from "../api/cliente";

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
 * Herramienta determinista (Semana 3 · ADR-004 y /herramientas/signos-alarma):
 * Evalúa deterministamente los signos de alarma y parámetros clínicos según la guía MSP.
 */
export const ChecklistSignosAlarma: React.FC<ChecklistSignosAlarmaProps> = ({
  abierto,
  onCerrar,
}) => {
  const [seleccionados, setSeleccionados] = useState<Record<string, boolean>>({});
  const [diasFiebre, setDiasFiebre] = useState<number>(3);
  const [edad, setEdad] = useState<number>(25);
  const [resultadoHttp, setResultadoHttp] = useState<EvaluarSignosAlarmaHttpOut | null>(null);
  const [evaluandoHttp, setEvaluandoHttp] = useState<boolean>(false);

  // Consulta el endpoint HTTP determinista de la Semana 3 ante cambios
  useEffect(() => {
    if (!abierto) return;

    let cancelado = false;
    const ejecutarEvaluacionServidor = async () => {
      setEvaluandoHttp(true);
      try {
        const respuesta = await evaluarSignosAlarmaHttp({
          dias_fiebre: Math.max(0, Math.min(30, diasFiebre)),
          dolor_abdominal: Boolean(seleccionados["dolor_abdominal"]),
          vomitos_persistentes: Boolean(seleccionados["vomitos"]),
          sangrado: Boolean(seleccionados["sangrado"]),
          edad: Math.max(0, Math.min(120, edad)),
        });
        if (!cancelado) {
          setResultadoHttp(respuesta);
        }
      } catch {
        // En caso de estar sin conexión o error de red, se mantiene el fallback determinista local
      } finally {
        if (!cancelado) {
          setEvaluandoHttp(false);
        }
      }
    };

    void ejecutarEvaluacionServidor();

    return () => {
      cancelado = true;
    };
  }, [abierto, seleccionados, diasFiebre, edad]);

  if (!abierto) return null;

  const alternarSigno = (id: string) => {
    setSeleccionados((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const totalActivos = Object.values(seleccionados).filter(Boolean).length;
  const hayPeligro = totalActivos > 0 || resultadoHttp?.nivel === "alarma";

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

        {/* Parámetros clínicos de la Semana 3 */}
        <div className="parametros-clinicos-grid">
          <div className="campo-parametro">
            <label htmlFor="dias-fiebre-input">
              <strong>Días con fiebre:</strong>
            </label>
            <input
              id="dias-fiebre-input"
              type="number"
              min={0}
              max={30}
              value={diasFiebre}
              onChange={(e) => setDiasFiebre(Number(e.target.value) || 0)}
              className="input-parametro"
            />
            <span className="pista-parametro">Fase crítica: 3 a 7 días</span>
          </div>

          <div className="campo-parametro">
            <label htmlFor="edad-paciente-input">
              <strong>Edad del paciente:</strong>
            </label>
            <input
              id="edad-paciente-input"
              type="number"
              min={0}
              max={120}
              value={edad}
              onChange={(e) => setEdad(Number(e.target.value) || 0)}
              className="input-parametro"
            />
            <span className="pista-parametro">Grupos vulnerables: &lt;5 y &gt;65</span>
          </div>
        </div>

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

        {/* Resultado del triaje clínico */}
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
              {resultadoHttp && (
                <div className="detalle-servidor-msp">
                  <span className="etiqueta-msp">Nivel MSP: {resultadoHttp.nivel.toUpperCase()}</span>
                  <p className="rec-msp">{resultadoHttp.recomendacion}</p>
                  <small className="fuente-msp">Fuente: {resultadoHttp.fuente}</small>
                </div>
              )}
              <a href="tel:911" className="btn-emergencia-inline">
                <PhoneCall size={16} aria-hidden="true" />
                <span>Llamar al 911 ahora</span>
              </a>
            </div>
          </div>
        ) : resultadoHttp?.nivel === "vigilancia" ? (
          <div className="resultado-checklist vigilancia" role="status">
            <AlertTriangle size={22} aria-hidden="true" />
            <div>
              <strong>Estado de Vigilancia Médica ({diasFiebre} días de fiebre)</strong>
              <p>
                {resultadoHttp.recomendacion}. Al cumplir 3 o más días con fiebre, entra en la fase crítica
                donde pueden manifestarse signos de alarma.
              </p>
              <small className="fuente-msp">Fuente: {resultadoHttp.fuente}</small>
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
              {resultadoHttp && (
                <small className="fuente-msp">Fuente oficial: {resultadoHttp.fuente}</small>
              )}
            </div>
          </div>
        )}

        <div className="modal-pie-checklist">
          {evaluandoHttp && (
            <span className="pista-parametro" style={{ marginRight: "auto", alignSelf: "center" }}>
              Consultando triaje MSP en tiempo real...
            </span>
          )}
          <button type="button" className="btn-cerrar-modal" onClick={onCerrar}>
            Cerrar lista de verificación
          </button>
        </div>
      </div>
    </div>
  );
};
