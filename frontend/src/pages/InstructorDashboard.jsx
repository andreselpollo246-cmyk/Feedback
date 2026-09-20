import { useEffect, useState } from "react";
import DashboardShell from "../components/DashboardShell";
import { api, ApiError } from "../api/client";

function EstrellasFijas({ promedio }) {
  const llenas = Math.round(promedio);
  return (
    <div className="stars-fixed" aria-label={`Promedio ${promedio} de 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <svg key={n} viewBox="0 0 24 24" width="18" height="18">
          <path
            d="M12 2.6l2.86 5.94 6.44.77-4.72 4.5 1.24 6.53L12 17.3 6.18 20.34l1.24-6.53-4.72-4.5 6.44-.77z"
            fill={n <= llenas ? "var(--color-accent)" : "none"}
            stroke={n <= llenas ? "var(--color-accent)" : "var(--color-border)"}
            strokeWidth="1.5"
          />
        </svg>
      ))}
    </div>
  );
}

export default function InstructorDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .instructorDashboard()
      .then(setData)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar tu información.")
      )
      .finally(() => setLoading(false));
  }, []);

  const fichas = data ? Object.entries(data.fichas_data) : [];

  return (
    <DashboardShell title="Mi desempeño por ficha">
      {loading && <p className="state-message">Cargando...</p>}
      {error && <p className="state-message state-message--error">{error}</p>}

      {data && fichas.length === 0 && (
        <p className="state-message">
          Todavía no tienes fichas asignadas en el trimestre activo.
        </p>
      )}

      <div className="ficha-stats">
        {fichas.map(([numeroFicha, stats]) => (
          <article key={numeroFicha} className="ficha-card">
            <header className="ficha-card__header">
              <div>
                <h3>Ficha {numeroFicha}</h3>
                <p>{stats.programa}</p>
                <p className="ficha-card__competencia">{stats.competencia}</p>
              </div>
              <div className="ficha-card__score">
                <span className="ficha-card__score-number">{stats.promedio}</span>
                <EstrellasFijas promedio={stats.promedio} />
                <span className={`badge badge--${stats.rendimiento.toLowerCase()}`}>
                  {stats.rendimiento}
                </span>
              </div>
            </header>

            <div className="ficha-card__bar-track">
              <div
                className="ficha-card__bar-fill"
                style={{ width: `${stats.porcentaje}%` }}
              />
            </div>

            <p className="ficha-card__mensaje">{stats.mensaje}</p>
            <p className="ficha-card__total">
              {stats.total} evaluación{stats.total === 1 ? "" : "es"} recibida
              {stats.total === 1 ? "" : "s"}
            </p>

            {stats.comentarios.length > 0 && (
              <div className="ficha-card__comentarios">
                {stats.comentarios.map((c, i) => (
                  <blockquote key={i}>“{c.texto}”</blockquote>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
    </DashboardShell>
  );
}
