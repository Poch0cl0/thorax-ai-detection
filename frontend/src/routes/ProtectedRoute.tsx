import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const loc = useLocation()

  if (loading) {
    return (
      <div className="page-card">
        <p className="muted">Cargando sesión…</p>
      </div>
    )
  }
  if (!user) {
    return <Navigate to="/login" replace state={{ from: loc }} />
  }
  return <>{children}</>
}
