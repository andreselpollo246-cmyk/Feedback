import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const ROLE_LABEL = {
  aprendiz: "Aprendiz",
  instructor: "Instructor",
  admin: "Administrador",
};

export default function DashboardShell({ title, children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="shell">
      <aside className="shell__sidebar">
        <div className="shell__brand">
          <span className="shell__brand-mark">SENA</span>
          <span className="shell__brand-sub">Evaluación de instructores</span>
        </div>

        <div className="shell__user">
          <div className="shell__user-avatar">
            {user?.nombre?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div>
            <div className="shell__user-name">{user?.nombre}</div>
            <div className="shell__user-role">{ROLE_LABEL[user?.rol]}</div>
          </div>
        </div>

        <button className="shell__logout" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </aside>

      <main className="shell__content">
        <h1 className="shell__title">{title}</h1>
        {children}
      </main>
    </div>
  );
}
