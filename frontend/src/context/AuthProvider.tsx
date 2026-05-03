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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshUser = useCallback(async () => {
    setError(null)
    try {
      const u = await authService.fetchCurrentUser()
      setUser(u)
    } catch {
      setUser(null)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    void (async () => {
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
  }, [refreshUser])

  const login = useCallback(async (email: string, password: string) => {
    setError(null)
    await authService.loginWithPassword(email, password)
    const u = await authService.fetchCurrentUser()
    setUser(u)
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      error,
      login,
      logout,
      refreshUser,
    }),
    [user, loading, error, login, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
