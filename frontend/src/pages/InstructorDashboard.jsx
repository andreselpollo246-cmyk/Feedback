import { useEffect, useState } from "react";
import DashboardShell from "../components/DashboardShell";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";

function EstrellasFijas({ promedio }) {
  const llenas = Math.round(promedio);
  return (
    <div className="d-flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <i
          key={n}
          className={`bi ${n <= llenas ? "bi-star-fill" : "bi-star"}`}
          style={{ color: n <= llenas ? "#ffc107" : "#dee2e6" }}
        />
      ))}
    </div>
  );
}

export default function InstructorDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .instructorDashboard()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar tu información."))
      .finally(() => setLoading(false));
  }, []);

  const fichas = data ? Object.entries(data.fichas_data) : [];

  return (
    <DashboardShell>
      <div className="saludo-bar">
        <p className="saludo-texto">
          <i className="bi bi-bar-chart-line me-2"></i>
          Hola, <span className="nombre-verde">{data?.nombre || user?.nombre}</span>
        </p>
        <p className="ficha-texto">Tu desempeño por ficha en el trimestre actual</p>
      </div>

      {loading && <p className="state-message">Cargando...</p>}
      {error && <p className="state-message state-message--error">{error}</p>}

      {data && fichas.length === 0 && (
        <p className="state-message">
          <i className="bi bi-inbox fs-1 text-muted me-2"></i>
          Todavía no tienes fichas asignadas en el trimestre activo.
        </p>
      )}

      {fichas.map(([numeroFicha, stats]) => (
        <div key={numeroFicha} className="ficha-card">
          <div className="ficha-card__header">
            <div>
              <span className="badge-ficha mb-2 d-inline-block">Ficha {numeroFicha}</span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, margin: "0.3rem 0" }}>{stats.programa}</h3>
              <p style={{ color: "var(--verde)", fontWeight: 600, fontSize: "0.85rem" }}>{stats.competencia}</p>
            </div>
            <div className="ficha-card__score">
              <span className="ficha-card__score-number">{stats.promedio}</span>
              <EstrellasFijas promedio={stats.promedio} />
              <span className="badge-estado badge-evaluado">{stats.rendimiento}</span>
            </div>
          </div>

          <div className="ficha-card__bar-track">
            <div className="ficha-card__bar-fill" style={{ width: `${stats.porcentaje}%` }} />
          </div>

          <p style={{ margin: "0 0 0.25rem", color: "#444" }}>
            <i className="bi bi-lightbulb me-2"></i>{stats.mensaje}
          </p>
          <p style={{ color: "#888", fontSize: "0.85rem" }}>
            <i className="bi bi-people me-2"></i>
            {stats.total} evaluación{stats.total === 1 ? "" : "es"} recibida{stats.total === 1 ? "" : "s"}
          </p>

          {stats.comentarios.length > 0 && (
            <div className="mt-3">
              <p style={{ fontWeight: 600, fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                <i className="bi bi-chat-square-text me-2"></i>Comentarios recientes
              </p>
              {stats.comentarios.map((c, i) => (
                <div key={i} className="comentario-card">
                  <p className="comentario-texto">"{c.texto}"</p>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </DashboardShell>
  );
}
