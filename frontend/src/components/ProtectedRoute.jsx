import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ rol, children }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.rol !== rol) {
    // Sesión válida pero de otro rol: lo mandamos a su propio dashboard
    // en vez de dejarlo ver una pantalla que no le corresponde.
    return <Navigate to={`/${user.rol}`} replace />;
  }

  return children;
}
