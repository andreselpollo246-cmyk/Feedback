import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";

const ROLES = [
  { value: "aprendiz", label: "Aprendiz", hint: "Número de documento" },
  { value: "instructor", label: "Instructor", hint: "Número de documento" },
  { value: "admin", label: "Administrador", hint: "Usuario" },
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
      setError(
        err instanceof ApiError
          ? err.message
          : "Ocurrió un error inesperado. Intenta de nuevo."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login">
      <div className="login__brand">
        <span className="login__brand-mark">SENA</span>
        <h1 className="login__brand-title">
          La voz del aprendiz
          <br />
          forma mejores instructores.
        </h1>
        <p className="login__brand-copy">
          Cada trimestre, tu evaluación ayuda a reconocer el buen trabajo
          docente y a mejorar lo que no está funcionando.
        </p>
      </div>

      <div className="login__panel">
        <form className="login__form" onSubmit={handleSubmit}>
          <h2 className="login__form-title">Inicia sesión</h2>

          <div className="login__roles" role="tablist">
            {ROLES.map((r) => (
              <button
                key={r.value}
                type="button"
                role="tab"
                aria-selected={rol === r.value}
                className={`login__role ${rol === r.value ? "login__role--active" : ""}`}
                onClick={() => setRol(r.value)}
              >
                {r.label}
              </button>
            ))}
          </div>

          <label className="field">
            <span className="field__label">{rolActivo.hint}</span>
            <input
              className="field__input"
              value={identificacion}
              onChange={(e) => setIdentificacion(e.target.value)}
              autoComplete="username"
              required
            />
          </label>

          <label className="field">
            <span className="field__label">Contraseña</span>
            <input
              className="field__input"
              type="password"
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          {error && <p className="login__error">{error}</p>}

          <button className="button button--primary button--block" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
