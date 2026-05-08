import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { User } from '../types/api'
import * as authService from '../services/authService'
import { setToken } from '../services/api'
import { AuthContext, type AuthContextValue } from './authContext'
import { isClinicalMock } from '../services/clinicalRepository'
import { getMockClinicalSnapshot } from '../services/mockClinicalStore'
import {
  clearStoredEffectiveRole,
  defaultEffectiveRole,
  persistEffectiveRole,
  readStoredEffectiveRole,
} from '../utils/effectiveRole'

function demoUserFromEmail(email: string): User {
  const e = email.trim().toLowerCase()
  let full_name = 'Usuario demo'
  let role = 'clinician'
  let roles: string[] = ['clinician']
  if (isClinicalMock()) {
    const demo = getMockClinicalSnapshot().demo_users[e]
    if (demo) {
      full_name = demo.full_name
      const ar = demo.app_role
      if (ar === 'secretaria') {
        role = 'secretaria'
        roles = ['secretaria']
      } else if (ar === 'admin') {
        role = 'admin'
        roles = ['admin']
      } else {
        role = 'clinician'
        roles = ['clinician']
      }
    }
  } else if (e === 'secretaria@hospital.com') {
    full_name = 'Ana Torres'
    role = 'secretaria'
    roles = ['secretaria']
  } else if (e === 'dual@hospital.com') {
    full_name = 'Demo Secretaría / Médico'
    role = 'clinician'
    roles = ['clinician', 'secretaria']
  } else if (e.includes('demo') || e === 'demo@hospital.com') {
    full_name = 'Dr. Carlos Mendez'
    role = 'clinician'
    roles = ['clinician']
  }
  return {
    id: 0,
    email: e,
    full_name,
    is_active: true,
    role,
    roles,
    created_at: new Date().toISOString(),
  }
}

function initialSkipAuthUser(): User {
  const email =
    (import.meta.env.VITE_DEMO_LOGIN_EMAIL ||
      'demo@hospital.com') as string
  return demoUserFromEmail(email)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [effectiveApiRole, setEffectiveApiRoleState] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const skipAuth = import.meta.env.VITE_SKIP_AUTH === 'true'

  const setEffectiveApiRole = useCallback((role: string) => {
    const r = role.trim().toLowerCase()
    setEffectiveApiRoleState(r)
    persistEffectiveRole(r)
  }, [])

  const syncEffectiveWithUser = useCallback((u: User | null) => {
    if (!u) {
      setEffectiveApiRoleState('')
      return
    }
    const allowed = Array.isArray(u.roles) ? u.roles.map((x) => x.toLowerCase()) : [u.role.toLowerCase()]
    const stored = readStoredEffectiveRole(u)
    let next =
      stored && allowed.includes(stored)
        ? stored
        : defaultEffectiveRole(u)
    if (!allowed.includes(next))
      next = defaultEffectiveRole(u)
    setEffectiveApiRoleState(next)
    persistEffectiveRole(next)
  }, [])

  const refreshUser = useCallback(async () => {
    if (skipAuth) {
      const u = initialSkipAuthUser()
      setUser(u)
      syncEffectiveWithUser(u)
      return
    }
    setError(null)
    try {
      const u = await authService.fetchCurrentUser()
      setUser(u)
      syncEffectiveWithUser(u)
    } catch {
      setUser(null)
      syncEffectiveWithUser(null)
    }
  }, [skipAuth, syncEffectiveWithUser])

  useEffect(() => {
    let cancelled = false
    void (async () => {
      if (skipAuth) {
        const u = initialSkipAuthUser()
        if (!cancelled) {
          setUser(u)
          syncEffectiveWithUser(u)
          setLoading(false)
        }
        return
      }
      if (!localStorage.getItem('thorax_token')) {
        if (!cancelled) setLoading(false)
        return
      }
      await refreshUser()
      if (!cancelled) setLoading(false)
    })()
    return () => {
      cancelled = true
    }
  }, [refreshUser, skipAuth, syncEffectiveWithUser])

  const login = useCallback(
    async (email: string, _password: string) => {
      if (skipAuth) {
        setError(null)
        const u = demoUserFromEmail(email)
        setUser(u)
        syncEffectiveWithUser(u)
        return
      }
      setError(null)
      await authService.loginWithPassword(email, _password)
      const u = await authService.fetchCurrentUser()
      setUser(u)
      syncEffectiveWithUser(u)
    },
    [skipAuth, syncEffectiveWithUser],
  )

  const logout = useCallback(() => {
    if (!skipAuth) {
      authService.logout()
      setToken(null)
    }
    clearStoredEffectiveRole()
    setUser(null)
    setEffectiveApiRoleState('')
  }, [skipAuth])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      effectiveApiRole: effectiveApiRole || (
        user ? defaultEffectiveRole(user) : ''
      ),
      setEffectiveApiRole,
      loading,
      error,
      login,
      logout,
      refreshUser,
    }),
    [
      user,
      effectiveApiRole,
      setEffectiveApiRole,
      loading,
      error,
      login,
      logout,
      refreshUser,
    ],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
