// Cliente HTTP central. Todas las páginas llaman a la API a través de estas
// funciones en vez de usar fetch directamente, así el manejo del token y
// de los errores queda en un solo lugar.

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "feedback_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Lanza este error cuando la respuesta no fue exitosa, para que las
 * páginas puedan mostrar el mensaje real que manda el backend
 * (el `detail` de FastAPI/HTTPException).
 */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let payload = body;
  if (body && !isForm) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: payload,
    });
  } catch (networkError) {
    throw new ApiError(
      "No se pudo conectar con el servidor. Verifica que el backend esté corriendo.",
      0
    );
  }

  // 204 No Content u otras respuestas sin body
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message =
      (data && (data.detail || data.message)) ||
      `Error inesperado (código ${response.status})`;
    throw new ApiError(
      typeof message === "string" ? message : JSON.stringify(message),
      response.status
    );
  }

  return data;
}

export const api = {
  // ---------- Auth ----------
  login: (rol, identificacion, contrasena) =>
    request("/api/auth/login", {
      method: "POST",
      body: { rol, identificacion, contrasena },
    }),

  // ---------- Aprendiz ----------
  aprendizDashboard: () => request("/api/aprendiz/dashboard"),
  enviarEvaluacion: (instructor_id, ratings, comentario) =>
    request("/api/aprendiz/evaluar", {
      method: "POST",
      body: { instructor_id, ratings, comentario },
    }),

  // ---------- Instructor ----------
  instructorDashboard: () => request("/api/instructor/dashboard"),

  // ---------- Admin ----------
  adminDashboard: () => request("/api/admin/dashboard"),
  listarInstructores: () => request("/api/admin/instructores"),
  listarFichas: () => request("/api/admin/fichas"),
  crearFicha: (datos) =>
    request("/api/admin/crear-ficha", { method: "POST", body: datos }),
  listarProgramas: () => request("/api/admin/programas"),
  crearPrograma: (datos) =>
    request("/api/admin/crear-programa", { method: "POST", body: datos }),
  listarCompetencias: () => request("/api/admin/competencias"),
  listarAsignaciones: () => request("/api/admin/asignaciones"),
  crearAprendiz: (datos) =>
    request("/api/admin/crear-aprendiz", { method: "POST", body: datos }),
  crearInstructor: (formData) =>
    request("/api/admin/crear-instructor", {
      method: "POST",
      body: formData,
      isForm: true,
    }),
  asignarInstructor: (datos) =>
    request("/api/admin/asignar-instructor", { method: "POST", body: datos }),
  eliminarAsignacion: (id) =>
    request(`/api/admin/eliminar-asignacion/${id}`, { method: "DELETE" }),
};
