export default function Footer() {
  return (
    <footer className="feedback-footer">
      <div className="container">
        <div className="row py-4" style={{ display: "flex", flexWrap: "wrap", gap: "1.5rem" }}>
          <div className="mb-3" style={{ flex: "1 1 260px" }}>
            <div className="footer-marca">
              <img src="/img/logo-feedback.png" alt="Feedback" />
              <img src="/img/cgmlti.jpg" alt="CGMLTI" />
            </div>
            <p className="footer-desc mt-2">
              Sistema de Evaluación Virtual para Aprendices del SENA
            </p>
          </div>
          <div className="mb-3" style={{ flex: "1 1 220px" }}>
            <h6 className="footer-titulo">Dirección</h6>
            <p className="footer-info">
              <i className="bi bi-geo-alt-fill me-2"></i>
              Calle 52 N° 13 – 65, Bogotá D.C., Colombia
            </p>
            <p className="footer-info">
              <i className="bi bi-building me-2"></i>
              SENA Centro de Gestión de Mercados, Logística y Tecnologías de la Información
            </p>
          </div>
          <div className="mb-3" style={{ flex: "1 1 220px" }}>
            <h6 className="footer-titulo">Contacto</h6>
            <p className="footer-info">
              <i className="bi bi-telephone-fill me-2"></i>+(57) 601 594 1301
            </p>
            <p className="footer-info">
              <i className="bi bi-envelope-fill me-2"></i>info@sena.edu.co
            </p>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2026 SENA - Servicio Nacional de Aprendizaje. Todos los derechos reservados.</span>
        </div>
      </div>
    </footer>
  );
}
