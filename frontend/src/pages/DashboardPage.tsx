import { Link } from 'react-router-dom'

export function DashboardPage() {
  return (
    <div className="page-card">
      <h1>Panel principal</h1>
      <p className="lead">
        Flujo sugerido: registrar un paciente, crear un estudio asociado y
        ejecutar una predicción de apoyo (modelo simulado hasta montar el
        artefacto real).
      </p>
      <ul className="link-grid">
        <li>
          <Link to="/patients">Pacientes</Link>
          <span className="muted">Alta y listado</span>
        </li>
        <li>
          <Link to="/studies">Estudios</Link>
          <span className="muted">Por paciente</span>
        </li>
        <li>
          <Link to="/predict">Predicción IA</Link>
          <span className="muted">Inferencia sobre estudio</span>
        </li>
      </ul>
    </div>
  )
}
