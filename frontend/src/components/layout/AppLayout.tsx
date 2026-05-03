import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import './AppLayout.css'

export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="brand">
          Thorax AI
        </Link>
        <nav className="nav">
          <NavLink to="/" end>
            Inicio
          </NavLink>
          <NavLink to="/patients">Pacientes</NavLink>
          <NavLink to="/studies">Estudios</NavLink>
          <NavLink to="/predict">Predicción</NavLink>
        </nav>
        <div className="user-area">
          {user && (
            <span className="user-email" title={user.email}>
              {user.email}
            </span>
          )}
          <button type="button" className="btn-ghost" onClick={() => logout()}>
            Salir
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
