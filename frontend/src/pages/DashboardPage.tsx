import { Link } from 'react-router-dom'
import {
  AlertCircle,
  Calendar,
  ChevronRight,
  Clock,
  TrendingUp,
  UserPlus,
  Users,
} from 'lucide-react'
import { useClinicalViewModel } from '../hooks/useClinicalViewModel'
import { StatCard } from '../components/ui/StatCard'
import { AppBadge } from '../components/ui/AppBadge'
import { patientAgeYears } from '../utils/age'
import {
  appointmentsTodayCount,
  criticalCasesCount,
  predictionsPendingCount,
  patientRowStatus,
} from '../utils/clinicalStats'
import { useAuth } from '../context/useAuth'
import { mapUserRoleToAppRole } from '../services/clinicalRepository'
export function DashboardPage() {
  const { vm, loading } = useClinicalViewModel()
  const { user, effectiveApiRole } = useAuth()
  const role = user
    ? mapUserRoleToAppRole(user.email, user.role, effectiveApiRole)
    : 'especialista'

  if (loading || !vm) {
    return (
      <div className="rounded-xl border border-thorax-border bg-thorax-card p-8 text-thorax-muted">
        Cargando panel…
      </div>
    )
  }

  if (role === 'secretaria') {
    const upcoming = [...vm.appointments]
      .filter((a) => a.status !== 'cancelado')
      .sort(
        (a, b) =>
          new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
      )
      .slice(0, 5)
    const patientById = new Map(vm.patients.map((p) => [p.id, p]))

    return (
      <div className="mx-auto max-w-6xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-thorax-text">
            Dashboard
          </h1>
          <p className="mt-2 text-sm text-thorax-muted">
            Gestión de citas y pacientes • ThoraxAI
          </p>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-thorax-text">
                Próximas citas
              </h2>
              <Link
                to="/appointments"
                className="text-sm font-medium text-thorax-accent hover:underline"
              >
                Ver todas
              </Link>
            </div>
            <ul className="mt-4 space-y-4">
              {upcoming.map((a) => {
                const p = patientById.get(a.patient_id)
                const t = new Date(a.scheduled_at)
                const line = `${t.toLocaleDateString('es-PE')} · ${t.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })}`
                return (
                  <li
                    key={a.id}
                    className="flex items-start gap-3 border-b border-thorax-border/60 pb-3 last:border-0 last:pb-0"
                  >
                    <Calendar className="mt-0.5 h-4 w-4 text-thorax-accent" strokeWidth={1.75} />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-thorax-text">
                        {p?.full_name ?? 'Paciente'}
                      </p>
                      <p className="text-sm text-thorax-muted">{line}</p>
                      {a.notes && (
                        <p className="mt-1 text-xs text-thorax-muted">{a.notes}</p>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>
            {upcoming.length === 0 && (
              <p className="mt-6 text-sm text-thorax-muted">Sin citas programadas.</p>
            )}
          </div>
          <div className="flex flex-col gap-4">
            <Link
              to="/appointments"
              className="flex items-center justify-center gap-2 rounded-xl bg-thorax-accent px-4 py-4 text-center text-sm font-semibold text-slate-900 shadow hover:bg-thorax-accent-hover"
            >
              <UserPlus className="h-5 w-5" strokeWidth={1.75} />
              Nueva cita
            </Link>
            <StatCard label="Pacientes registrados" value={vm.patients.length} icon={Users} />
          </div>
        </div>
      </div>
    )
  }

  const totalPatients = vm.patients.length
  const pend = predictionsPendingCount(vm)
  const critical = criticalCasesCount(vm)
  const today = appointmentsTodayCount(vm)

  const recent = [...vm.patients].slice(-5).reverse()

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-thorax-text">
          Dashboard
        </h1>
        <p className="mt-2 text-sm text-thorax-muted">
          Bienvenido, Doctor. Sistema de Diagnóstico Torácico con IA.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total de Pacientes"
          value={totalPatients}
          icon={Users}
          className="ring-1 ring-thorax-accent/40"
        />
        <StatCard
          label="Predicciones Pendientes"
          value={pend}
          icon={Clock}
          variant="danger"
        />
        <StatCard
          label="Casos Críticos"
          value={critical}
          icon={AlertCircle}
          variant="dangerBorder"
        />
        <StatCard
          label="Citas Hoy"
          value={today}
          icon={TrendingUp}
          variant="accent"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_minmax(0,1fr)]">
        <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-thorax-text">
              Pacientes recientes
            </h2>
            <Link
              to="/patients"
              className="text-sm font-medium text-thorax-accent hover:underline"
            >
              Ver todos
            </Link>
          </div>
          <ul className="mt-4 divide-y divide-thorax-border/60">
            {recent.map((p) => {
              const age = patientAgeYears(p.birth_date)
              const condBits =
                p.conditions_summary?.split(',').map((x) => x.trim()).filter(Boolean)
                  .length ?? 0
              const st = patientRowStatus(vm, p.id)
              return (
                <li key={p.id}>
                  <Link
                    to="/patients"
                    className="flex items-center gap-4 py-4 text-left hover:bg-thorax-bg-deep/60"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-thorax-text">{p.full_name}</p>
                      <p className="mt-1 text-xs text-thorax-muted">
                        DNI: {p.dni ?? '—'}
                        {age != null ? ` · Edad: ${age} años` : ''}
                        {condBits > 0 ? ` · ${condBits} condiciones` : ''}
                      </p>
                    </div>
                    <AppBadge
                      variant={
                        st.kind === 'done'
                          ? 'success'
                          : st.kind === 'pending'
                            ? 'warning'
                            : 'neutral'
                      }
                    >
                      {st.label}
                    </AppBadge>
                    <ChevronRight className="h-5 w-5 shrink-0 text-thorax-muted" strokeWidth={1.75} />
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
            <h2 className="text-lg font-semibold text-thorax-text">
              Acciones rápidas
            </h2>
            <div className="mt-4 flex flex-col gap-3">
              <Link
                to="/predictions"
                className="flex items-center gap-3 rounded-xl border border-thorax-border bg-thorax-bg-deep/40 px-4 py-3 text-sm font-medium text-thorax-text hover:border-thorax-accent"
              >
                <Clock className="h-5 w-5 text-thorax-accent" strokeWidth={1.75} />
                Revisiones pendientes
              </Link>
              <Link
                to="/patients"
                className="flex items-center gap-3 rounded-xl border border-thorax-border bg-thorax-bg-deep/40 px-4 py-3 text-sm font-medium text-thorax-text hover:border-thorax-accent"
              >
                <UserPlus className="h-5 w-5 text-thorax-accent" strokeWidth={1.75} />
                Nuevo paciente
              </Link>
            </div>
          </div>
          <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
            <h2 className="text-sm font-semibold text-thorax-text">
              Información del sistema
            </h2>
            <p className="mt-2 text-xs leading-relaxed text-thorax-muted">
              Los resultados de IA son de apoyo y no sustituyen el juicio clínico.
              Modelo en versión demostración con datos simulados cuando el modo
              mock está activo.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
