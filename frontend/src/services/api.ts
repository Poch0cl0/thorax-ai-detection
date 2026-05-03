/** Base URL del API. En build de producción sin variable, se usan rutas relativas (p. ej. nginx). */
export function getApiBase(): string {
  const v = import.meta.env.VITE_API_BASE_URL
  if (typeof v === 'string' && v.length > 0) return v
  if (import.meta.env.DEV) return 'http://127.0.0.1:8000'
  return ''
}

export function getToken(): string | null {
  return localStorage.getItem('thorax_token')
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem('thorax_token', token)
  else localStorage.removeItem('thorax_token')
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const base = getApiBase()
  const url = path.startsWith('http') ? path : `${base}${path}`
  const headers = new Headers(options.headers)
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json')
  }

  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const err = (await res.json()) as { detail?: unknown }
      if (typeof err.detail === 'string') detail = err.detail
      else if (Array.isArray(err.detail)) detail = JSON.stringify(err.detail)
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}
