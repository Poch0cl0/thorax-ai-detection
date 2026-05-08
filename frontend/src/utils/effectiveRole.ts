import type { User } from '../types/api'

const LS_KEY = 'thorax_effective_api_role'

function normalizeRoles(user: User | null): string[] {
  if (!user) return []
  if (Array.isArray(user.roles) && user.roles.length > 0) {
    return user.roles.map((r) => r.toLowerCase())
  }
  return user.role ? [user.role.toLowerCase()] : []
}

export function readStoredEffectiveRole(user: User): string | null {
  try {
    const stored = localStorage.getItem(LS_KEY)?.trim().toLowerCase()
    if (!stored) return null
    const allowed = normalizeRoles(user)
    if (!allowed.includes(stored)) return null
    return stored
  } catch {
    return null
  }
}

export function defaultEffectiveRole(user: User): string {
  const allowed = normalizeRoles(user)
  if (allowed.includes('clinician')) return 'clinician'
  if (allowed.includes('secretaria')) return 'secretaria'
  if (allowed.includes('admin')) return 'admin'
  return allowed[0] ?? 'clinician'
}

export function initEffectiveRoleForUser(user: User): string {
  const fromLs = readStoredEffectiveRole(user)
  if (fromLs) return fromLs
  return defaultEffectiveRole(user)
}

export function persistEffectiveRole(role: string) {
  try {
    localStorage.setItem(LS_KEY, role.toLowerCase())
  } catch {
    /* ignore */
  }
}

export function clearStoredEffectiveRole() {
  try {
    localStorage.removeItem(LS_KEY)
  } catch {
    /* ignore */
  }
}
