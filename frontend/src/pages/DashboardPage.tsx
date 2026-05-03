import { Link } from 'react-router-dom'

export function DashboardPage() {
  return (
    <div className="page-card">
      <h1>Panel principal</h1>
      <p className="lead">
        Sistema de detección de cáncer de tórax con IA. Sube una
        radiografía para obtener un análisis inmediato, o gestiona
        pacientes y estudios con el flujo clínico completo.
      </p>
      <ul className="link-grid">
        <li>
          <Link to="/scan">🔬 Análisis IA</Link>
          <span className="muted">
            Subir radiografía y obtener predicción inmediata
          </span>
        </li>
        <li>
          <Link to="/patients">Pacientes</Link>
          <span className="muted">Alta y listado</span>
        </li>
        <li>
          <Link to="/studies">Estudios</Link>
          <span className="muted">Por paciente</span>
        </li>
        <li>
          <Link to="/predict">Predicción clínica</Link>
          <span className="muted">Inferencia sobre estudio registrado</span>
        </li>
      </ul>
    </div>
  )
}
