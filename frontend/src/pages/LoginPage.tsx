import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { LoginForm } from '../features/auth/LoginForm'
import { useAuth } from '../context/useAuth'

export function LoginPage() {
  const { user, login, loading } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const nav = useNavigate()
  const loc = useLocation()
  const from =
    (loc.state as { from?: { pathname: string } } | null)?.from?.pathname ??
    '/'

  if (loading) {
    return (
      <div className="login-wrap">
        <p className="muted">Cargando…</p>
      </div>
    )
  }
  if (user) {
    return <Navigate to={from} replace />
  }

  return (
    <div className="login-wrap">
      <div className="page-card narrow">
        <h1>Ingreso clínico</h1>
        <p className="muted">
          Sistema de apoyo para detección temprana (demostración).
        </p>
        <LoginForm
          error={error}
          loading={busy}
          onSubmit={async (email, password) => {
            setBusy(true)
            setError(null)
            try {
              await login(email, password)
              nav(from, { replace: true })
            } catch (e) {
              setError(e instanceof Error ? e.message : 'Error de acceso')
            } finally {
              setBusy(false)
            }
          }}
        />
      </div>
    </div>
  )
}
