import { Navigate } from 'react-router-dom'
import type { AppRole } from '../../types/clinical-domain'
import { useAuth } from '../../context/useAuth'
import { mapUserRoleToAppRole } from '../../services/clinicalRepository'

type Props = {
  allow: AppRole[]
  children: React.ReactNode
  fallback?: string
}

export function RoleGate({ allow, children, fallback = '/' }: Props) {
  const { user, effectiveApiRole } = useAuth()
  if (!user) return null
  const role = mapUserRoleToAppRole(
    user.email,
    user.role,
    effectiveApiRole,
  )
  if (!allow.includes(role)) {
    return <Navigate to={fallback} replace />
  }
  return <>{children}</>
}
