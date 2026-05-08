import { createContext } from 'react'
import type { User } from '../types/api'

export type AuthContextValue = {
  user: User | null
  /** Rol API activo (clinician | secretaria | admin) para navegación y RoleGate */
  effectiveApiRole: string
  setEffectiveApiRole: (role: string) => void
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
