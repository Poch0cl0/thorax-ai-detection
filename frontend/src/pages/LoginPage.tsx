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
      <div className="flex min-h-screen items-center justify-center bg-thorax-bg-deep text-thorax-muted">
        <p>Cargando…</p>
      </div>
    )
  }
  if (user) {
    return <Navigate to={from} replace />
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-thorax-bg-deep via-thorax-bg to-slate-950 px-4 py-10">
      <div className="w-full max-w-md rounded-2xl border border-thorax-border bg-thorax-card-alt px-8 py-10 shadow-2xl shadow-cyan-950/20">
        <div className="flex flex-col items-center text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-sky-600 text-lg font-bold text-slate-900 shadow-lg">
            TX
          </div>
          <h1 className="mt-5 text-2xl font-bold tracking-tight text-thorax-text">
            ThoraxAI
          </h1>
          <p className="mt-2 max-w-xs text-sm leading-relaxed text-thorax-muted">
            Sistema de Inteligencia Artificial para Diagnóstico Torácico
          </p>
        </div>
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
