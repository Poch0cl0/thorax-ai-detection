import { useState } from 'react'
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  Stethoscope,
  Trash2,
  User,
  X,
} from 'lucide-react'
import { useClinicalViewModel } from '../hooks/useClinicalViewModel'
import * as clinicalService from '../services/clinicalService'
import type {
  PatientRecord,
  SpecialistRecord,
} from '../types/clinical-domain'

const MONTHS = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

const WEEKDAYS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

const TIME_SLOTS = [
  '08:00',
  '08:30',
  '09:00',
  '09:30',
  '10:00',
  '10:30',
  '11:00',
  '11:30',
  '14:00',
  '14:30',
  '15:00',
  '15:30',
  '16:00',
  '16:30',
]

function startOfMonth(d: Date) {
  return new Date(d.getFullYear(), d.getMonth(), 1)
}

function addMonths(d: Date, n: number) {
  return new Date(d.getFullYear(), d.getMonth() + n, 1)
}

/** Lunes = 0 … Domingo = 6 (es-PE) */
function mondayIndex(jsDay: number) {
  const v = jsDay - 1
  return v < 0 ? 6 : v
}

export function AppointmentsPage() {
  const {
    vm,
    loading,
    mode,
    refreshApi,
    createAppointmentDemo,
  } = useClinicalViewModel()

  const [viewMonth, setViewMonth] = useState(() =>
    startOfMonth(new Date()),
  )
  const [selectedDay, setSelectedDay] = useState<number | null>(() => {
    const t = new Date()
    return t.getDate()
  })

  const [showForm, setShowForm] = useState(false)
  const [patientId, setPatientId] = useState('')
  const [specialistId, setSpecialistId] = useState('')
  const [dateStr, setDateStr] = useState('')
  const [timeStr, setTimeStr] = useState('')
  const [notes, setNotes] = useState('')

  const calYear = viewMonth.getFullYear()
  const calMonth = viewMonth.getMonth()
  const first = new Date(calYear, calMonth, 1)
  const last = new Date(calYear, calMonth + 1, 0)
  const startPad = mondayIndex(first.getDay())
  const daysInMonth = last.getDate()

  const appointmentsInMonth = !vm
    ? []
    : vm.appointments.filter((a) => {
        const t = new Date(a.scheduled_at)
        return t.getFullYear() === calYear && t.getMonth() === calMonth
      })

  const dotDays = new Set<number>()
  appointmentsInMonth.forEach((a) => {
    dotDays.add(new Date(a.scheduled_at).getDate())
  })

  const specialistById = new Map<string, SpecialistRecord>(
    vm ? vm.specialists.map((s) => [s.id, s]) : [],
  )

  const patientById = new Map<string, PatientRecord>(
    vm ? vm.patients.map((p) => [p.id, p]) : [],
  )

  const listItems = !vm
    ? []
    : [...appointmentsInMonth].sort(
        (a, b) =>
          new Date(a.scheduled_at).getTime() -
          new Date(b.scheduled_at).getTime(),
      )

  if (loading || !vm) {
    return (
      <div className="rounded-xl border border-thorax-border bg-thorax-card p-8 text-thorax-muted">
        Cargando citas…
      </div>
    )
  }

  const today = new Date()
  const viewingCurrentMonth =
    today.getFullYear() === calYear && today.getMonth() === calMonth
  const hasAppointmentToday =
    viewingCurrentMonth &&
    appointmentsInMonth.some(
      (a) => new Date(a.scheduled_at).getDate() === today.getDate(),
    )
  const footerText = viewingCurrentMonth
    ? hasAppointmentToday
      ? 'Citas programadas para hoy'
      : 'Sin citas hoy'
    : 'Los días con cita muestran un indicador bajo el número'

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-thorax-text">
          Gestión de Citas
        </h1>
        <p className="mt-2 text-sm text-thorax-muted">
          Programa y gestiona las citas de los pacientes.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-thorax-border bg-thorax-card p-5">
          <div className="flex items-center justify-between">
            <button
              type="button"
              aria-label="Mes anterior"
              className="rounded-lg p-2 text-thorax-muted hover:bg-thorax-bg-deep hover:text-thorax-text"
              onClick={() => setViewMonth((d) => addMonths(d, -1))}
            >
              <ChevronLeft className="h-5 w-5" strokeWidth={1.75} />
            </button>
            <p className="text-sm font-semibold capitalize text-thorax-text">
              {MONTHS[calMonth]} {calYear}
            </p>
            <button
              type="button"
              aria-label="Mes siguiente"
              className="rounded-lg p-2 text-thorax-muted hover:bg-thorax-bg-deep hover:text-thorax-text"
              onClick={() => setViewMonth((d) => addMonths(d, 1))}
            >
              <ChevronRight className="h-5 w-5" strokeWidth={1.75} />
            </button>
          </div>
          <div className="mt-4 grid grid-cols-7 gap-1 text-center text-xs text-thorax-muted">
            {WEEKDAYS.map((d) => (
              <div key={d} className="py-2 font-medium">
                {d}
              </div>
            ))}
            {Array.from({ length: startPad }).map((_, i) => (
              <div key={`pad-${i}`} />
            ))}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1
              const isSel = selectedDay === day
              const hasDot = dotDays.has(day)
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => setSelectedDay(day)}
                  className={[
                    'relative flex flex-col items-center justify-center rounded-lg py-2 text-sm font-medium transition-colors',
                    isSel
                      ? 'bg-thorax-accent text-slate-900'
                      : 'text-thorax-text hover:bg-thorax-bg-deep',
                  ].join(' ')}
                >
                  {day}
                  {hasDot && (
                    <span
                      className={[
                        'mt-1 block h-1.5 w-1.5 rounded-full',
                        isSel ? 'bg-slate-900' : 'bg-thorax-accent',
                      ].join(' ')}
                    />
                  )}
                </button>
              )
            })}
          </div>
          <p className="mt-4 text-center text-xs text-thorax-muted">{footerText}</p>
        </div>

        <div className="flex flex-col rounded-xl border border-thorax-border bg-thorax-card">
          <div className="flex items-center justify-between border-b border-thorax-border px-5 py-4">
            <h2 className="text-lg font-semibold text-thorax-text">Citas</h2>
            <button
              type="button"
              onClick={() => {
                setShowForm(true)
                const d =
                  selectedDay != null
                    ? new Date(calYear, calMonth, selectedDay)
                    : new Date()
                setDateStr(d.toISOString().slice(0, 10))
                if (vm.specialists[0]) setSpecialistId(vm.specialists[0].id)
                if (vm.patients[0]) setPatientId(vm.patients[0].id)
              }}
              className="inline-flex items-center gap-2 rounded-xl bg-thorax-accent px-4 py-2 text-xs font-semibold text-slate-900 hover:bg-thorax-accent-hover"
            >
              + Nueva Cita
            </button>
          </div>
          <ul className="thorax-scroll max-h-[420px] divide-y divide-thorax-border/60 overflow-y-auto px-5 py-3">
            {listItems.map((a) => {
              const p = patientById.get(a.patient_id)
              const sp = a.specialist_id
                ? specialistById.get(a.specialist_id)
                : undefined
              const t = new Date(a.scheduled_at)
              return (
                <li
                  key={a.id}
                  className="flex gap-3 py-4 first:pt-0"
                >
                  <div className="min-w-0 flex-1 space-y-2 text-sm">
                    <p className="flex items-center gap-2 font-medium text-thorax-text">
                      <User className="h-4 w-4 shrink-0 text-thorax-accent" strokeWidth={1.75} />
                      {p?.full_name ?? 'Paciente'}
                    </p>
                    <p className="flex items-center gap-2 text-thorax-muted">
                      <Clock className="h-4 w-4 shrink-0" strokeWidth={1.75} />
                      {t.toLocaleDateString('es-PE')} —{' '}
                      {t.toLocaleTimeString('es-PE', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                    <p className="flex items-center gap-2 text-xs text-thorax-muted">
                      <Stethoscope className="h-4 w-4 shrink-0 text-thorax-muted" strokeWidth={1.75} />
                      {a.notes ?? 'Consulta'} •{' '}
                      {sp?.display_name ?? 'Sin asignar'}
                    </p>
                  </div>
                  {mode === 'api' && a.status === 'pendiente' && (
                    <button
                      type="button"
                      className="self-start text-thorax-muted hover:text-thorax-danger disabled:opacity-40"
                      title="Eliminar cita pendiente"
                      aria-label={`Eliminar cita ${a.id}`}
                      onClick={() =>
                        window.confirm(
                          '¿Eliminar esta cita pendiente?',
                        ) &&
                        void (async () => {
                          await clinicalService.deleteAppointment(
                            Number.parseInt(a.id, 10),
                          ).catch(() => {})
                          await refreshApi()
                        })()
                      }
                    >
                      <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                    </button>
                  )}
                </li>
              )
            })}
            {listItems.length === 0 && (
              <p className="py-8 text-center text-sm text-thorax-muted">
                No hay citas en este mes.
              </p>
            )}
          </ul>
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <button
            type="button"
            className="absolute inset-0 z-10 cursor-default bg-black/55"
            aria-label="Cerrar"
            onClick={() => setShowForm(false)}
          />
          <div className="relative z-20 w-full max-w-md rounded-2xl border border-thorax-border bg-thorax-card-alt p-6 shadow-xl">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-lg font-semibold text-thorax-text">
                Nueva Cita
              </h3>
              <button
                type="button"
                className="rounded-lg p-1 text-thorax-muted hover:bg-thorax-bg-deep hover:text-thorax-text"
                onClick={() => setShowForm(false)}
              >
                <X className="h-5 w-5" strokeWidth={1.75} />
              </button>
            </div>
            <form
              className="mt-4 space-y-4"
              onSubmit={(e) => {
                e.preventDefault()
                if (!patientId || !specialistId || !dateStr || !timeStr) return
                const [hh, mm] = timeStr.split(':').map(Number)
                const dt = new Date(
                  `${dateStr}T${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:00`,
                )
                void (async () => {
                  if (mode === 'mock') {
                    createAppointmentDemo({
                      patient_id: patientId,
                      specialist_id: specialistId,
                      scheduled_at: dt.toISOString(),
                      notes: notes.trim() || 'Consulta de control',
                      status: 'pendiente',
                    })
                  } else {
                    try {
                      await clinicalService.createAppointment({
                        patient_id: Number.parseInt(patientId, 10),
                        attending_user_id: Number.parseInt(
                          specialistId,
                          10,
                        ),
                        scheduled_at: dt.toISOString(),
                        notes: notes.trim() || null,
                        status: 'pendiente',
                      })
                      await refreshApi()
                    } catch {
                      window.alert(
                        'No se pudo crear la cita. Compruebe sesión y permisos de secretaría.',
                      )
                      return
                    }
                  }
                  setShowForm(false)
                  setNotes('')
                })()
              }}
            >
              <label className="flex flex-col gap-1 text-xs font-medium uppercase tracking-wide text-thorax-muted">
                Paciente
                <select
                  required
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  className="rounded-xl border border-thorax-border bg-thorax-bg-deep px-3 py-2.5 text-sm normal-case text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
                >
                  <option value="">Seleccionar paciente…</option>
                  {vm.patients.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.full_name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1 text-xs font-medium uppercase tracking-wide text-thorax-muted">
                Fecha
                <input
                  type="date"
                  required
                  value={dateStr}
                  onChange={(e) => setDateStr(e.target.value)}
                  className="rounded-xl border border-thorax-border bg-thorax-bg-deep px-3 py-2.5 text-sm normal-case text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
                />
              </label>
              <label className="flex flex-col gap-1 text-xs font-medium uppercase tracking-wide text-thorax-muted">
                Hora
                <select
                  required
                  value={timeStr}
                  onChange={(e) => setTimeStr(e.target.value)}
                  className="rounded-xl border border-thorax-border bg-thorax-bg-deep px-3 py-2.5 text-sm normal-case text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
                >
                  <option value="">Seleccionar hora…</option>
                  {TIME_SLOTS.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1 text-xs font-medium uppercase tracking-wide text-thorax-muted">
                Tipo de consulta
                <input
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Ej: Consulta de control, Seguimiento…"
                  className="rounded-xl border border-thorax-border bg-thorax-bg-deep px-3 py-2.5 text-sm normal-case text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
                />
              </label>
              <label className="flex flex-col gap-1 text-xs font-medium uppercase tracking-wide text-thorax-muted">
                Doctor
                <select
                  required
                  value={specialistId}
                  onChange={(e) => setSpecialistId(e.target.value)}
                  className="rounded-xl border border-thorax-border bg-thorax-bg-deep px-3 py-2.5 text-sm normal-case text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
                >
                  <option value="">Seleccionar doctor…</option>
                  {vm.specialists.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.display_name}
                    </option>
                  ))}
                </select>
              </label>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  className="flex-1 rounded-xl bg-thorax-accent py-2.5 text-sm font-semibold text-slate-900 hover:bg-thorax-accent-hover"
                >
                  Agendar cita
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 rounded-xl border border-thorax-border bg-thorax-bg-deep py-2.5 text-sm font-medium text-thorax-text hover:bg-thorax-card"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
