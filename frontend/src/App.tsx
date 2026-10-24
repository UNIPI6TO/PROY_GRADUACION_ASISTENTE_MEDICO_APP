import React, { useState, useReducer, useRef, useEffect, useCallback } from "react";
import { Send, Square, Sparkles } from "lucide-react";
import {
  obtenerIdSesion,
  reiniciarIdSesion,
  consultarAsistente,
  ErrorContratoAPI,
} from "./api/cliente";
import {
  transicionarEstado,
  type EstadoInterfaz,
  type MensajeHistorialUI,
} from "./types/estados";
import { Cabecera } from "./components/Cabecera";
import { MensajeChat } from "./components/MensajeChat";
import { AlertaEstado } from "./components/AlertaEstado";
import { ChecklistSignosAlarma } from "./components/ChecklistSignosAlarma";
import "./App.css";

const SUGERENCIAS_RAPIDAS = [
  "¿Cuáles son los signos de alarma del dengue según el MSP?",
  "¿Cómo elimino los criaderos de mosquitos en mi casa?",
  "¿Por qué no debo tomar ibuprofeno ni aspirina si tengo fiebre?",
  "¿Qué pasa cuando baja la fiebre en el tercer día del dengue?",
];

export const App: React.FC = () => {
  const [idSesion, setIdSesion] = useState<string>(() => obtenerIdSesion());
  const [texto, setTexto] = useState<string>("");
  const [consultaEnCurso, setConsultaEnCurso] = useState<string>("");
  const [mensajes, setMensajes] = useState<MensajeHistorialUI[]>([]);
  const [checklistAbierto, setChecklistAbierto] = useState<boolean>(false);

  const [estado, dispatch] = useReducer(transicionarEstado, { tipo: "inactiva" } as EstadoInterfaz);

  const abortControllerRef = useRef<AbortController | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const historialRef = useRef<HTMLElement | null>(null);
  const finChatRef = useRef<HTMLDivElement | null>(null);

  const estaOcupado = estado.tipo === "enviando" || estado.tipo === "recibiendo";

  // Auto-scroll hacia el último mensaje o indicador de carga al hacer una nueva consulta o recibir respuesta
  useEffect(() => {
    const prefiereSinMovimiento =
      typeof window !== "undefined" &&
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const comportamiento: ScrollBehavior = prefiereSinMovimiento ? "auto" : "smooth";

    const contenedor = historialRef.current;
    if (contenedor) {
      if (typeof contenedor.scrollTo === "function") {
        contenedor.scrollTo({ top: contenedor.scrollHeight, behavior: comportamiento });
      } else {
        contenedor.scrollTop = contenedor.scrollHeight;
      }
    }

    if (finChatRef.current && typeof finChatRef.current.scrollIntoView === "function") {
      finChatRef.current.scrollIntoView({ behavior: comportamiento, block: "end" });
    }
  }, [mensajes, estado, consultaEnCurso]);

  const ejecutarConsulta = useCallback(
    async (consultaTexto: string) => {
      const limpio = consultaTexto.trim();
      if (limpio.length < 5 || limpio.length > 2000) {
        dispatch({
          tipo: "ERROR_422",
          detalle: "Revisa idSesion y texto (5 a 2000 caracteres).",
          textoConservado: consultaTexto,
        });
        return;
      }

      const controlador = new AbortController();
      abortControllerRef.current = controlador;

      setConsultaEnCurso(limpio);
      dispatch({ tipo: "ENVIAR" });

      try {
        const respuesta = await consultarAsistente(
          { idSesion, texto: limpio },
          {
            signal: controlador.signal,
            onToken: (fragmento) => {
              dispatch({ tipo: "TOKEN_RECIBIDO", fragmento });
            },
          }
        );

        const idTurnoUsuario = `usr-${Date.now()}`;
        const idTurnoAsistente = `ast-${Date.now() + 1}`;

        setMensajes((prev) => [
          ...prev,
          { id: idTurnoUsuario, rol: "user", texto: limpio },
          {
            id: idTurnoAsistente,
            rol: "assistant",
            texto: respuesta.respuesta,
            seAbstiene: respuesta.se_abstiene,
            derivarA: respuesta.derivar_a,
            fuentes: respuesta.fuentes ?? [],
            proveedor: respuesta.proveedor,
            valoracion: null,
          },
        ]);

        setTexto("");
        dispatch({ tipo: "RESPUESTA_COMPLETA", respuesta });
        textareaRef.current?.focus();
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          dispatch({ tipo: "ABORTAR" });
          textareaRef.current?.focus();
          return;
        }
        if (err instanceof Error && err.name === "AbortError") {
          dispatch({ tipo: "ABORTAR" });
          textareaRef.current?.focus();
          return;
        }

        if (err instanceof ErrorContratoAPI) {
          if (err.status === 422) {
            dispatch({
              tipo: "ERROR_422",
              detalle: err.problema.detail,
              textoConservado: consultaTexto,
            });
            return;
          }
          if (err.status === 429) {
            dispatch({
              tipo: "ERROR_429",
              segundos: err.retryAfter ?? 10,
              detalle: err.problema.detail,
              textoConservado: consultaTexto,
            });
            return;
          }
          if (err.status === 503) {
            dispatch({
              tipo: "ERROR_503",
              segundos: err.retryAfter ?? 30,
              detalle: err.problema.detail,
              textoConservado: consultaTexto,
            });
            return;
          }
        }

        dispatch({
          tipo: "ERROR_503",
          segundos: 30,
          detalle: "No se pudo conectar con el servidor de orientación.",
          textoConservado: consultaTexto,
        });
      } finally {
        setConsultaEnCurso("");
        abortControllerRef.current = null;
      }
    },
    [idSesion]
  );

  // Cuenta regresiva para estado 429 (Diapositiva 8: Cuenta regresiva y reintento cuando llega a cero)
  useEffect(() => {
    if (estado.tipo !== "reintentar") return;

    const timer = window.setTimeout(() => {
      if (estado.segundos <= 1) {
        const textoParaReintentar = estado.textoConservado;
        dispatch({ tipo: "TICK_CUENTA_REGRESIVA" });
        if (textoParaReintentar.trim().length >= 5) {
          void ejecutarConsulta(textoParaReintentar);
        }
      } else {
        dispatch({ tipo: "TICK_CUENTA_REGRESIVA" });
      }
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [estado, ejecutarConsulta]);

  const manejarDetener = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    dispatch({ tipo: "ABORTAR" });
    textareaRef.current?.focus();
  }, []);

  // Atajo global Escape para detener generación (Diapositiva 12)
  useEffect(() => {
    const alPresionarTecla = (e: KeyboardEvent) => {
      if (e.key === "Escape" && estaOcupado) {
        e.preventDefault();
        manejarDetener();
      }
    };
    window.addEventListener("keydown", alPresionarTecla);
    return () => window.removeEventListener("keydown", alPresionarTecla);
  }, [estaOcupado, manejarDetener]);

  const manejarEnvioFormulario = (e: React.FormEvent) => {
    e.preventDefault();
    if (estaOcupado || estado.tipo === "reintentar") return;
    void ejecutarConsulta(texto);
  };

  const manejarTeclaTextarea = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!estaOcupado && estado.tipo !== "reintentar") {
        void ejecutarConsulta(texto);
      }
    }
  };

  const manejarNuevaConversacion = () => {
    manejarDetener();
    const nueva = reiniciarIdSesion();
    setIdSesion(nueva);
    setMensajes([]);
    setTexto("");
    dispatch({ tipo: "REINICIAR" });
    textareaRef.current?.focus();
  };

  const manejarValoracion = (id: string, valor: "util" | "no_util") => {
    setMensajes((prev) =>
      prev.map((m) => (m.id === id ? { ...m, valoracion: valor } : m))
    );
  };

  return (
    <div className="contenedor-app">
      <Cabecera
        idSesion={idSesion}
        onNuevaConversacion={manejarNuevaConversacion}
        onAbrirChecklist={() => setChecklistAbierto(true)}
      />

      <main className="area-principal">
        {/* Región viva accesible (Diapositiva 12): anuncia la respuesta completa cuando termina */}
        <section
          ref={historialRef}
          className="historial-chat"
          aria-live="polite"
          aria-busy={estaOcupado}
          aria-label="Conversación con GuíaVital"
        >
          {mensajes.length === 0 && !estaOcupado && (
            <div className="estado-vacio">
              <h2>¿Qué deseas consultar hoy sobre prevención o síntomas del dengue?</h2>
              <p>
                Selecciona una pregunta frecuente o escribe tu consulta abajo. Todas las respuestas
                se basan en lineamientos oficiales del Ministerio de Salud Pública (MSP) y la OPS.
              </p>
              <div className="sugerencias-grid">
                {SUGERENCIAS_RAPIDAS.map((sugerencia) => (
                  <button
                    key={sugerencia}
                    type="button"
                    className="btn-sugerencia"
                    onClick={() => {
                      setTexto(sugerencia);
                      void ejecutarConsulta(sugerencia);
                    }}
                  >
                    <Sparkles size={15} aria-hidden="true" />
                    <span>{sugerencia}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {mensajes.map((msg) => (
            <MensajeChat key={msg.id} mensaje={msg} onValorar={manejarValoracion} />
          ))}

          {estaOcupado && consultaEnCurso && (
            <MensajeChat
              mensaje={{
                id: "consulta-en-curso",
                rol: "user",
                texto: consultaEnCurso,
              }}
              onValorar={() => {}}
            />
          )}

          {estado.tipo === "enviando" && (
            <div className="indicador-pensando" role="status">
              <span className="punto-pulso" aria-hidden="true" />
              <span>Consultando guías oficiales del MSP / OPS...</span>
            </div>
          )}

          {estado.tipo === "recibiendo" && (
            <article className="mensaje mensaje-asistente mensaje-parcial">
              <div className="mensaje-encabezado">
                <span className="etiqueta-ia">Generando respuesta con IA...</span>
              </div>
              <p className="mensaje-texto">{estado.texto}</p>
            </article>
          )}

          <div ref={finChatRef} aria-hidden="true" />
        </section>

        <AlertaEstado
          estado={estado}
          onReintentar={() => {
            if (estado.tipo === "caido" || estado.tipo === "reintentar") {
              void ejecutarConsulta(estado.textoConservado || texto);
            }
          }}
        />

        <form className="formulario-chat" onSubmit={manejarEnvioFormulario} noValidate>
          <div className="campo-contenedor">
            <label htmlFor="consulta-dengue" className="sr-only">
              Escribe tu consulta sobre prevención o signos de dengue (5 a 2000 caracteres)
            </label>
            <textarea
              id="consulta-dengue"
              ref={textareaRef}
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              onKeyDown={manejarTeclaTextarea}
              placeholder="Escribe tu consulta preventiva sobre el dengue (mín. 5 caracteres)... Presiona Enter para enviar o Escape para detener."
              rows={3}
              maxLength={2000}
              aria-invalid={estado.tipo === "invalido"}
              disabled={estado.tipo === "reintentar"}
            />
            <div className="barra-inferior-campo">
              <span className="contador-caracteres">
                {texto.length} / 2000 caracteres · Sesión: <code>{idSesion.slice(0, 8)}</code>
              </span>

              <div className="botones-envio">
                {estaOcupado ? (
                  <button
                    type="button"
                    className="btn-detener"
                    onClick={manejarDetener}
                    aria-label="Detener generación de respuesta"
                  >
                    <Square size={16} aria-hidden="true" />
                    <span>Detener (Esc)</span>
                  </button>
                ) : (
                  <button
                    type="submit"
                    className="btn-enviar"
                    disabled={estado.tipo === "reintentar"}
                  >
                    <Send size={16} aria-hidden="true" />
                    <span>Enviar consulta</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </form>
      </main>

      <ChecklistSignosAlarma
        abierto={checklistAbierto}
        onCerrar={() => setChecklistAbierto(false)}
      />
    </div>
  );
};

export default App;
