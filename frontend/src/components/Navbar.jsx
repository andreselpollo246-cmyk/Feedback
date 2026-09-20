import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout(e) {
    e.preventDefault();
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <nav className="feedback-navbar">
      <div className="container-fluid px-4">
        <a className="navbar-brand d-flex align-items-center gap-3" href="/">
          <div className="feedback-logo-nav">
            <img src="/img/logo-feedback.png" alt="Feedback" />
            <img src="/img/cgmlti.jpg" alt="CGMLTI" />
          </div>
        </a>

        {user && (
          <div className="ms-auto d-flex align-items-center gap-3">
            <span className="nav-rol-badge">{user.rol?.toUpperCase()}</span>
            <a href="#" className="btn-cerrar-sesion d-inline-flex align-items-center gap-2" onClick={handleLogout}>
              <i className="bi bi-box-arrow-right"></i>Cerrar sesión
            </a>
          </div>
        )}
      </div>
    </nav>
  );
}
