import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";

const ROLES = [
  { value: "aprendiz", label: "Aprendiz", icon: "bi-mortarboard-fill", hint: "Número de identificación" },
  { value: "instructor", label: "Instructor", icon: "bi-person-badge-fill", hint: "Número de identificación" },
  { value: "admin", label: "Admin", icon: "bi-shield-lock-fill", hint: "Usuario" },
];

export default function Login() {
  const [rol, setRol] = useState("aprendiz");
  const [identificacion, setIdentificacion] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const rolActivo = ROLES.find((r) => r.value === rol);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login(rol, identificacion, contrasena);
      navigate(`/${data.rol}`, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Ocurrió un error inesperado.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-bg">
      <div className="login-container">
        <div className="feedback-logo-grande">
          <img src="/img/logo-feedback.png" alt="Feedback" />
        </div>

        <div className="login-card" style={{ width: "100%" }}>
          <div className="roles-container">
            {ROLES.map((r) => (
              <button
                key={r.value}
                type="button"
                className={`btn-rol ${rol === r.value ? "activo" : ""}`}
                onClick={() => setRol(r.value)}
              >
                <i className={`bi ${r.icon}`}></i>
                <span>{r.label}</span>
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {error && (
              <div className="alert-error">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                {error}
              </div>
            )}

            <div className="campo-grupo">
              <label className="campo-label">
                <i className="bi bi-person-vcard me-2"></i>
                {rolActivo.hint}
              </label>
              <input
                className="campo-input"
                value={identificacion}
                onChange={(e) => setIdentificacion(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className="campo-grupo">
              <label className="campo-label">
                <i className="bi bi-lock-fill me-2"></i>
                Contraseña
              </label>
              <input
                type="password"
                className="campo-input"
                value={contrasena}
                onChange={(e) => setContrasena(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            <button className="btn-ingresar" disabled={loading}>
              {loading ? "Entrando..." : "Ingresar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
