import { useEffect, useState } from "react";
import DashboardShell from "../components/DashboardShell";
import StarRating from "../components/StarRating";
import { api, ApiError } from "../api/client";

const CRITERIOS = [
  { key: "dominio", label: "Dominio del tema" },
  { key: "claridad", label: "Claridad en las explicaciones" },
  { key: "puntualidad", label: "Puntualidad y asistencia" },
  { key: "trato", label: "Trato al aprendiz" },
  { key: "metodologia", label: "Recursos didácticos y metodología" },
];

function vaciarRatings() {
  return CRITERIOS.reduce((acc, c) => ({ ...acc, [c.key]: 0 }), {});
}

export default function AprendizDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [instructorActivo, setInstructorActivo] = useState(null);
  const [ratings, setRatings] = useState(vaciarRatings());
  const [comentario, setComentario] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [formError, setFormError] = useState("");

  async function cargar() {
    setLoading(true);
    setError("");
    try {
      const dashboard = await api.aprendizDashboard();
      setData(dashboard);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar tu información.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  function abrirEvaluacion(instructor) {
    setInstructorActivo(instructor);
    setRatings(vaciarRatings());
    setComentario("");
    setFormError("");
  }

  function cerrarModal() {
    setInstructorActivo(null);
  }

  async function enviarEvaluacion(e) {
    e.preventDefault();
    const faltantes = CRITERIOS.filter((c) => !ratings[c.key]);
    if (faltantes.length > 0) {
      setFormError("Califica todos los criterios antes de enviar.");
      return;
    }
    setEnviando(true);
    setFormError("");
    try {
      await api.enviarEvaluacion(instructorActivo.id, ratings, comentario);
      setInstructorActivo(null);
      await cargar();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "No se pudo enviar la evaluación.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <DashboardShell title="Instructores por evaluar">
      {loading && <p className="state-message">Cargando...</p>}
      {error && <p className="state-message state-message--error">{error}</p>}

      {data && (
        <>
          <div className="summary-bar">
            <div>
              <span className="summary-bar__label">Ficha</span>
              <span className="summary-bar__value">{data.ficha || "—"}</span>
            </div>
            <div>
              <span className="summary-bar__label">Programa</span>
              <span className="summary-bar__value">{data.programa || "—"}</span>
            </div>
            <div>
              <span className="summary-bar__label">Trimestre</span>
              <span className="summary-bar__value">{data.trimestre}</span>
            </div>
          </div>

          {data.instructores.length === 0 ? (
            <p className="state-message">
              No tienes instructores asignados para evaluar en este trimestre.
            </p>
          ) : (
            <div className="instructor-grid">
              {data.instructores.map((inst) => (
                <article key={inst.id} className="instructor-card">
                  <div className="instructor-card__avatar">
                    {inst.imagen ? (
                      <img src={inst.imagen} alt={inst.nombre} />
                    ) : (
                      inst.nombre.charAt(0)
                    )}
                  </div>
                  <div className="instructor-card__body">
                    <h3>{inst.nombre}</h3>
                    <p>{inst.competencia}</p>
                    <p className="instructor-card__ficha">Ficha {inst.ficha}</p>
                  </div>
                  {inst.evaluado ? (
                    <span className="badge badge--done">Evaluado</span>
                  ) : (
                    <button
                      className="button button--primary"
                      onClick={() => abrirEvaluacion(inst)}
                    >
                      Evaluar
                    </button>
                  )}
                </article>
              ))}
            </div>
          )}
        </>
      )}

      {instructorActivo && (
        <div className="modal-backdrop" onClick={cerrarModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Evaluar a {instructorActivo.nombre}</h2>
            <p className="modal__subtitle">{instructorActivo.competencia}</p>

            <form onSubmit={enviarEvaluacion}>
              <div className="modal__ratings">
                {CRITERIOS.map((c) => (
                  <StarRating
                    key={c.key}
                    label={c.label}
                    value={ratings[c.key]}
                    onChange={(n) => setRatings((r) => ({ ...r, [c.key]: n }))}
                  />
                ))}
              </div>

              <label className="field">
                <span className="field__label">Comentario (opcional)</span>
                <textarea
                  className="field__input field__input--textarea"
                  value={comentario}
                  onChange={(e) => setComentario(e.target.value)}
                  rows={3}
                />
              </label>

              {formError && <p className="login__error">{formError}</p>}

              <div className="modal__actions">
                <button type="button" className="button" onClick={cerrarModal}>
                  Cancelar
                </button>
                <button type="submit" className="button button--primary" disabled={enviando}>
                  {enviando ? "Enviando..." : "Enviar evaluación"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
