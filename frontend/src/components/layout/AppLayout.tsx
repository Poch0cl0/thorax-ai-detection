import { NavLink, Outlet } from 'react-router-dom'
import type { LucideIcon } from 'lucide-react'
import {
  Activity,
  CalendarDays,
  CalendarCheck2,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  Users,
} from 'lucide-react'
import { useAuth } from '../../context/useAuth'
import { mapUserRoleToAppRole } from '../../services/clinicalRepository'
import type { AppRole } from '../../types/clinical-domain'

type NavLinkItem = {
  to: string
  end?: boolean
  label: string
  icon: LucideIcon
}

const roleLabel: Record<AppRole, string> = {
  especialista: 'Especialista',
  secretaria: 'Secretaria',
  admin: 'Administrador',
}

const apiRoleLabel: Record<string, string> = {
  clinician: 'Especialista (médico)',
  secretaria: 'Secretaría',
  admin: 'Administrador',
}

export function AppLayout() {
  const { user, logout, effectiveApiRole, setEffectiveApiRole } = useAuth()
  const role = user
    ? mapUserRoleToAppRole(user.email, user.role, effectiveApiRole)
    : 'especialista'

  const apiRoles = Array.isArray(user?.roles)
    ? [...new Set(user!.roles.map((r) => r.toLowerCase()))]
    : []

  const navEspecialista: NavLinkItem[] = [
    { to: '/', end: true, label: 'Dashboard', icon: LayoutDashboard },
    { to: '/patients', label: 'Pacientes', icon: Users },
    { to: '/attend-queue', label: 'Atender citas', icon: CalendarCheck2 },
    { to: '/predictions', label: 'Predicciones IA', icon: Activity },
  ]

  const navSecretaria: NavLinkItem[] = [
    { to: '/', end: true, label: 'Dashboard', icon: LayoutDashboard },
    { to: '/appointments', label: 'Citas', icon: CalendarDays },
  ]

  let links: NavLinkItem[]
  if (role === 'secretaria') links = navSecretaria
  else if (role === 'admin')
    links = [
      { to: '/', end: true, label: 'Dashboard', icon: LayoutDashboard },
      { to: '/appointments', label: 'Citas', icon: CalendarDays },
      { to: '/attend-queue', label: 'Atender citas', icon: CalendarCheck2 },
      { to: '/patients', label: 'Pacientes', icon: Users },
      { to: '/predictions', label: 'Predicciones IA', icon: Activity },
    ]
  else links = navEspecialista

  return (
    <div className="flex min-h-screen bg-thorax-bg-deep text-thorax-text">
      <aside className="flex w-60 shrink-0 flex-col border-r border-thorax-border bg-thorax-sidebar">
        <div className="flex items-center gap-3 border-b border-thorax-border/80 px-4 py-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-sky-600 text-sm font-bold text-slate-900 shadow">
            TX
          </div>
          <div className="min-w-0">
            <p className="truncate font-semibold leading-tight text-thorax-text">
              ThoraxAI
            </p>
            <p className="text-xs text-thorax-muted">Versión 1.0</p>
          </div>
        </div>

        <nav className="flex flex-1 flex-col gap-1 p-3">
          {links.map(({ to, end, label, icon: Icon }) => (
            <NavLink
              key={`${to}:${end ? '1' : '0'}`}
              to={to}
              end={end === true}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-thorax-accent/15 text-white ring-1 ring-thorax-accent/30'
                    : 'text-thorax-muted hover:bg-thorax-card hover:text-thorax-text',
                ].join(' ')
              }
            >
              <Icon className="h-4 w-4 shrink-0 text-thorax-accent" strokeWidth={1.75} />
              {label}
            </NavLink>
          ))}
          <NavLink
            to="/scan"
            className={({ isActive }) =>
              [
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-thorax-accent/15 text-white ring-1 ring-thorax-accent/30'
                  : 'text-thorax-muted hover:bg-thorax-card hover:text-thorax-text',
              ].join(' ')
            }
          >
            <Activity className="h-4 w-4 shrink-0 text-thorax-accent" strokeWidth={1.75} />
            Análisis IA
          </NavLink>
        </nav>

        <div className="border-t border-thorax-border/80 p-4">
          <p className="truncate text-sm font-medium text-thorax-text">
            {user?.full_name || 'Usuario'}
          </p>
          <p className="mt-1 truncate text-xs text-thorax-muted" title={user?.email}>
            {user?.email}
          </p>
          <p className="mt-3 inline-flex rounded-full border border-thorax-border bg-thorax-card px-3 py-1 text-xs font-medium text-thorax-text">
            Vista: {roleLabel[role]}
          </p>
          {apiRoles.length >= 2 && (
            <label className="mt-3 block text-xs text-thorax-muted">
              Actuar como
              <select
                value={effectiveApiRole}
                onChange={(e) => setEffectiveApiRole(e.target.value)}
                className="mt-1 w-full rounded-lg border border-thorax-border bg-thorax-bg-deep px-2 py-2 text-xs text-thorax-text"
              >
                {apiRoles.map((r) => (
                  <option key={r} value={r}>
                    {apiRoleLabel[r] ?? r}
                  </option>
                ))}
              </select>
            </label>
          )}
          <button
            type="button"
            onClick={() => logout()}
            className="mt-4 flex w-full items-center gap-2 text-left text-sm text-thorax-muted hover:text-thorax-accent"
          >
            <LogOut className="h-4 w-4" strokeWidth={1.75} />
            Cerrar sesión
            <ChevronRight className="ml-auto h-4 w-4 opacity-70" strokeWidth={1.75} />
          </button>
        </div>
      </aside>

      <main className="thorax-scroll min-h-0 flex-1 overflow-y-auto p-6 lg:p-10">
        <Outlet />
      </main>
    </div>
  )
}
