import type { TokenResponse, User } from '../types/api'
import { apiFetch, getApiBase, setToken } from './api'

export async function loginWithPassword(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)

  const res = await fetch(`${getApiBase()}/api/v1/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })
  if (!res.ok) {
    let detail = 'No se pudo iniciar sesión'
    try {
      const j = (await res.json()) as { detail?: string }
      if (j.detail) detail = j.detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  const data = (await res.json()) as TokenResponse
  setToken(data.access_token)
  return data
}

export function logout() {
  setToken(null)
}

export async function fetchCurrentUser(): Promise<User> {
  return apiFetch<User>('/api/v1/users/me')
}
