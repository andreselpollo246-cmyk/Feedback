import { useEffect, useState } from "react";
import DashboardShell from "../components/DashboardShell";
import { useAuth } from "../context/AuthContext";
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

function EstrellaGrupo({ value, onChange }) {
  const [hover, setHover] = useState(0);
  const shown = hover || value;
  return (
    <div className="estrella-grupo" onMouseLeave={() => setHover(0)}>
      {[1, 2, 3, 4, 5].map((n) => (
        <i
          key={n}
          className={`bi estrella ${n <= shown ? "bi-star-fill activa" : "bi-star"}`}
          onMouseEnter={() => setHover(n)}
          onClick={() => onChange(n)}
        />
      ))}
    </div>
  );
}

export default function AprendizDashboard() {
  const { user } = useAuth();
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
      setData(await api.aprendizDashboard());
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
    <DashboardShell>
      <div className="saludo-bar d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div>
          <p className="saludo-texto">
            <i className="bi bi-hand-wave me-2"></i>
            Hola, <span className="nombre-verde">{data?.nombre || user?.nombre}</span>
          </p>
          <p className="ficha-texto">
            Ficha {data?.ficha || "—"} · {data?.programa || "—"}
          </p>
        </div>
        {data && <span className="badge-trimestre">{data.trimestre}</span>}
      </div>

      {loading && <p className="state-message">Cargando...</p>}
      {error && <p className="state-message state-message--error">{error}</p>}

      {data && data.instructores.length === 0 && (
        <p className="state-message">
          <i className="bi bi-inbox fs-1 text-muted me-2"></i>
          No tienes instructores asignados para evaluar en este trimestre.
        </p>
      )}

      {data && data.instructores.length > 0 && (
        <div className="instructores-grid mb-5">
          {data.instructores.map((inst) => (
            <div key={inst.id} className="instructor-card">
              <div className="instructor-foto">
                {inst.imagen ? (
                  <img src={inst.imagen} alt={inst.nombre} />
                ) : (
                  <i className="bi bi-person-badge-fill"></i>
                )}
              </div>
              <div className="instructor-info">
                <span className="instructor-ficha">Ficha {inst.ficha}</span>
                <span className="instructor-nombre">{inst.nombre}</span>
                <span className="instructor-competencia">{inst.competencia}</span>

                {inst.evaluado ? (
                  <span className="badge-estado badge-evaluado">
                    <i className="bi bi-check-circle-fill me-1"></i>Evaluado
                  </span>
                ) : (
                  <button className="btn-evaluar-instructor" onClick={() => abrirEvaluacion(inst)}>
                    <i className="bi bi-pencil-square me-2"></i>Evaluar
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {instructorActivo && (
        <div className="modal-backdrop-custom" onClick={() => setInstructorActivo(null)}>
          <div className="modal-custom" onClick={(e) => e.stopPropagation()}>
            <div className="eval-instructor-info">
              <i className="bi bi-person-badge-fill eval-icon"></i>
              <div>
                <div className="eval-nombre">{instructorActivo.nombre}</div>
                <div className="eval-competencia">{instructorActivo.competencia}</div>
              </div>
            </div>

            <form onSubmit={enviarEvaluacion}>
              <div className="criterios-evaluacion mb-3">
                {CRITERIOS.map((c) => (
                  <div key={c.key} className="criterio-item">
                    <span className="criterio-label">{c.label}</span>
                    <EstrellaGrupo
                      value={ratings[c.key]}
                      onChange={(n) => setRatings((r) => ({ ...r, [c.key]: n }))}
                    />
                  </div>
                ))}
              </div>

              <div className="campo-grupo mt-4">
                <label className="campo-label mb-2">
                  <i className="bi bi-chat-dots me-2"></i>Comentario (opcional)
                </label>
                <textarea
                  className="campo-input"
                  rows={3}
                  value={comentario}
                  onChange={(e) => setComentario(e.target.value)}
                />
              </div>

              {formError && <div className="alert-error">{formError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setInstructorActivo(null)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-evaluar-instructor" disabled={enviando} style={{ padding: "8px 20px" }}>
                  <i className="bi bi-send-fill me-2"></i>
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
