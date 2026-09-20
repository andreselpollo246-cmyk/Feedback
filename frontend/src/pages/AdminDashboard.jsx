import { useEffect, useState } from "react";
import DashboardShell from "../components/DashboardShell";
import { api, ApiError } from "../api/client";

const TABS = [
  { key: "resumen", label: "Resumen" },
  { key: "instructores", label: "Instructores" },
  { key: "fichas", label: "Fichas" },
  { key: "asignaciones", label: "Asignaciones" },
  { key: "crear-aprendiz", label: "Nuevo aprendiz" },
  { key: "crear-instructor", label: "Nuevo instructor" },
];

export default function AdminDashboard() {
  const [tab, setTab] = useState("resumen");

  return (
    <DashboardShell title="Administración">
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`tabs__item ${tab === t.key ? "tabs__item--active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "resumen" && <ResumenTab />}
      {tab === "instructores" && <InstructoresTab />}
      {tab === "fichas" && <FichasTab />}
      {tab === "asignaciones" && <AsignacionesTab />}
      {tab === "crear-aprendiz" && <CrearAprendizTab />}
      {tab === "crear-instructor" && <CrearInstructorTab />}
    </DashboardShell>
  );
}

// ---------------------------------------------------------------------

function ResumenTab() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminDashboard()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Error al cargar."));
  }, []);

  if (error) return <p className="state-message state-message--error">{error}</p>;
  if (!data) return <p className="state-message">Cargando...</p>;

  return (
    <div className="stat-grid">
      <div className="stat-card">
        <span className="stat-card__number">{data.total_aprendices}</span>
        <span className="stat-card__label">Aprendices</span>
      </div>
      <div className="stat-card">
        <span className="stat-card__number">{data.total_instructores}</span>
        <span className="stat-card__label">Instructores</span>
      </div>
      <div className="stat-card">
        <span className="stat-card__number">{data.total_evaluaciones}</span>
        <span className="stat-card__label">Evaluaciones recibidas</span>
      </div>
    </div>
  );
}

function InstructoresTab() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listarInstructores()
      .then(setItems)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Error al cargar."));
  }, []);

  if (error) return <p className="state-message state-message--error">{error}</p>;
  if (!items) return <p className="state-message">Cargando...</p>;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Documento</th>
          <th>Correo</th>
        </tr>
      </thead>
      <tbody>
        {items.map((i) => (
          <tr key={i.id}>
            <td>{i.nombre}</td>
            <td>{i.numDoc}</td>
            <td>{i.correo || "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function FichasTab() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listarFichas()
      .then(setItems)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Error al cargar."));
  }, []);

  if (error) return <p className="state-message state-message--error">{error}</p>;
  if (!items) return <p className="state-message">Cargando...</p>;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Ficha</th>
          <th>Programa</th>
          <th>Nivel</th>
          <th>Modalidad</th>
        </tr>
      </thead>
      <tbody>
        {items.map((f) => (
          <tr key={f.id}>
            <td>{f.numero}</td>
            <td>{f.programa}</td>
            <td>{f.nivel}</td>
            <td>{f.modalidad}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function AsignacionesTab() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [ok, setOk] = useState("");
  const [form, setForm] = useState({
    idInstructor: "",
    numeroFicha: "",
    idCompetencia: "",
    idTrimestre: "",
    habilitado: true,
  });

  function cargar() {
    api
      .listarAsignaciones()
      .then(setItems)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Error al cargar."));
  }

  useEffect(cargar, []);

  async function eliminar(id) {
    try {
      await api.eliminarAsignacion(id);
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo eliminar.");
    }
  }

  async function crear(e) {
    e.preventDefault();
    setFormError("");
    setOk("");
    try {
      await api.asignarInstructor({
        idInstructor: Number(form.idInstructor),
        numeroFicha: form.numeroFicha,
        idCompetencia: Number(form.idCompetencia),
        idTrimestre: Number(form.idTrimestre),
        habilitado: form.habilitado,
      });
      setOk("Asignación guardada correctamente.");
      cargar();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "No se pudo guardar.");
    }
  }

  return (
    <>
      <form className="inline-form" onSubmit={crear}>
        <label className="field field--compact">
          <span className="field__label">Id instructor</span>
          <input
            className="field__input"
            value={form.idInstructor}
            onChange={(e) => setForm((f) => ({ ...f, idInstructor: e.target.value }))}
            required
          />
        </label>
        <label className="field field--compact">
          <span className="field__label">Número de ficha</span>
          <input
            className="field__input"
            value={form.numeroFicha}
            onChange={(e) => setForm((f) => ({ ...f, numeroFicha: e.target.value }))}
            required
          />
        </label>
        <label className="field field--compact">
          <span className="field__label">Id competencia</span>
          <input
            className="field__input"
            value={form.idCompetencia}
            onChange={(e) => setForm((f) => ({ ...f, idCompetencia: e.target.value }))}
            required
          />
        </label>
        <label className="field field--compact">
          <span className="field__label">Id trimestre</span>
          <input
            className="field__input"
            value={form.idTrimestre}
            onChange={(e) => setForm((f) => ({ ...f, idTrimestre: e.target.value }))}
            required
          />
        </label>
        <button className="button button--primary" type="submit">
          Asignar
        </button>
      </form>
      {formError && <p className="state-message state-message--error">{formError}</p>}
      {ok && <p className="state-message state-message--ok">{ok}</p>}

      {error && <p className="state-message state-message--error">{error}</p>}
      {!items && !error && <p className="state-message">Cargando...</p>}

      {items && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Instructor</th>
              <th>Ficha</th>
              <th>Programa</th>
              <th>Competencia</th>
              <th>Trimestre</th>
              <th>Habilitado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((a) => (
              <tr key={a.id}>
                <td>{a.instructor}</td>
                <td>{a.ficha}</td>
                <td>{a.programa}</td>
                <td>{a.competencia}</td>
                <td>{a.trimestre}</td>
                <td>{a.habilitado ? "Sí" : "No"}</td>
                <td>
                  <button className="button button--danger" onClick={() => eliminar(a.id)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

function CrearAprendizTab() {
  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    fechaNacimiento: "",
    correo: "",
    password: "",
    tipoDocumento: "CC",
    numeroDocumento: "",
    ficha: "",
  });
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    setOk("");
    try {
      const res = await api.crearAprendiz(form);
      setOk(res.message);
      setForm((f) => ({ ...f, numeroDocumento: "", correo: "", password: "" }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear el aprendiz.");
    }
  }

  return (
    <form className="stack-form" onSubmit={submit}>
      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Nombre</span>
          <input className="field__input" value={form.nombre}
            onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Apellido</span>
          <input className="field__input" value={form.apellido}
            onChange={(e) => setForm((f) => ({ ...f, apellido: e.target.value }))} required />
        </label>
      </div>

      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Fecha de nacimiento</span>
          <input type="date" className="field__input" value={form.fechaNacimiento}
            onChange={(e) => setForm((f) => ({ ...f, fechaNacimiento: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Tipo de documento</span>
          <select className="field__input" value={form.tipoDocumento}
            onChange={(e) => setForm((f) => ({ ...f, tipoDocumento: e.target.value }))}>
            <option value="CC">CC</option>
            <option value="TI">TI</option>
            <option value="CE">CE</option>
            <option value="PPT">PPT</option>
          </select>
        </label>
        <label className="field">
          <span className="field__label">Número de documento</span>
          <input className="field__input" value={form.numeroDocumento}
            onChange={(e) => setForm((f) => ({ ...f, numeroDocumento: e.target.value }))} required />
        </label>
      </div>

      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Correo</span>
          <input type="email" className="field__input" value={form.correo}
            onChange={(e) => setForm((f) => ({ ...f, correo: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Contraseña</span>
          <input type="password" className="field__input" value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Número de ficha</span>
          <input className="field__input" value={form.ficha}
            onChange={(e) => setForm((f) => ({ ...f, ficha: e.target.value }))} required />
        </label>
      </div>

      {error && <p className="state-message state-message--error">{error}</p>}
      {ok && <p className="state-message state-message--ok">{ok}</p>}

      <button className="button button--primary" type="submit">Crear aprendiz</button>
    </form>
  );
}

function CrearInstructorTab() {
  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    fechaNacimiento: "",
    correo: "",
    password: "",
    tipoDocumento: "CC",
    numeroDocumento: "",
    competencia: "",
    ficha: "",
  });
  const [foto, setFoto] = useState(null);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    setOk("");
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => fd.append(k, v));
    if (foto) fd.append("foto", foto);

    try {
      const res = await api.crearInstructor(fd);
      setOk(res.message);
      setForm((f) => ({ ...f, numeroDocumento: "", correo: "", password: "" }));
      setFoto(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear el instructor.");
    }
  }

  return (
    <form className="stack-form" onSubmit={submit}>
      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Nombre</span>
          <input className="field__input" value={form.nombre}
            onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Apellido</span>
          <input className="field__input" value={form.apellido}
            onChange={(e) => setForm((f) => ({ ...f, apellido: e.target.value }))} required />
        </label>
      </div>

      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Fecha de nacimiento</span>
          <input type="date" className="field__input" value={form.fechaNacimiento}
            onChange={(e) => setForm((f) => ({ ...f, fechaNacimiento: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Tipo de documento</span>
          <select className="field__input" value={form.tipoDocumento}
            onChange={(e) => setForm((f) => ({ ...f, tipoDocumento: e.target.value }))}>
            <option value="CC">CC</option>
            <option value="TI">TI</option>
            <option value="CE">CE</option>
            <option value="PPT">PPT</option>
          </select>
        </label>
        <label className="field">
          <span className="field__label">Número de documento</span>
          <input className="field__input" value={form.numeroDocumento}
            onChange={(e) => setForm((f) => ({ ...f, numeroDocumento: e.target.value }))} required />
        </label>
      </div>

      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Correo</span>
          <input type="email" className="field__input" value={form.correo}
            onChange={(e) => setForm((f) => ({ ...f, correo: e.target.value }))} required />
        </label>
        <label className="field">
          <span className="field__label">Contraseña</span>
          <input type="password" className="field__input" value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} required />
        </label>
      </div>

      <div className="stack-form__row">
        <label className="field">
          <span className="field__label">Competencia (opcional)</span>
          <input className="field__input" value={form.competencia}
            onChange={(e) => setForm((f) => ({ ...f, competencia: e.target.value }))} />
        </label>
        <label className="field">
          <span className="field__label">Ficha (opcional, si asignas competencia)</span>
          <input className="field__input" value={form.ficha}
            onChange={(e) => setForm((f) => ({ ...f, ficha: e.target.value }))} />
        </label>
      </div>

      <label className="field">
        <span className="field__label">Foto (PNG, opcional, máx. 2MB)</span>
        <input type="file" accept="image/png" onChange={(e) => setFoto(e.target.files[0])} />
      </label>

      {error && <p className="state-message state-message--error">{error}</p>}
      {ok && <p className="state-message state-message--ok">{ok}</p>}

      <button className="button button--primary" type="submit">Crear instructor</button>
    </form>
  );
}
