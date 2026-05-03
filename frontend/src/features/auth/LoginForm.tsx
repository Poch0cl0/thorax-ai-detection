import { useState } from 'react'

type Props = {
  onSubmit: (email: string, password: string) => Promise<void>
  error: string | null
  loading: boolean
}

export function LoginForm({ onSubmit, error, loading }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  return (
    <form
      className="form-card"
      onSubmit={(e) => {
        e.preventDefault()
        void onSubmit(email, password)
      }}
    >
      <label>
        Correo
        <input
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      <label>
        Contraseña
        <input
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
      </label>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? 'Entrando…' : 'Iniciar sesión'}
      </button>
    </form>
  )
}
