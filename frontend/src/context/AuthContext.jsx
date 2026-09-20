import { createContext, useContext, useState, useCallback } from "react";
import { api, setToken, clearToken, getToken } from "../api/client";

const AuthContext = createContext(null);

// El JWT trae el payload en la 2a sección, separado por puntos, en base64url.
function decodeJwtPayload(token) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const token = getToken();
    if (!token) return null;
    const payload = decodeJwtPayload(token);
    if (!payload) return null;
    return {
      rol: payload.rol,
      nombre: payload.nombre,
      identificacion: payload.sub,
    };
  });

  const login = useCallback(async (rol, identificacion, contrasena) => {
    const data = await api.login(rol, identificacion, contrasena);
    setToken(data.access_token);
    setUser({
      rol: data.rol,
      nombre: data.nombre,
      identificacion: data.identificacion,
    });
    return data;
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
