import { useMemo, useState } from 'react'
import { ArrowRight, Search } from 'lucide-react'
import { useClinicalViewModel } from '../hooks/useClinicalViewModel'
import { patientAgeYears } from '../utils/age'
import { patientRowStatus } from '../utils/clinicalStats'
import { AppBadge } from '../components/ui/AppBadge'
import { Link } from 'react-router-dom'

export function PatientsPage() {
  const { vm, loading, createPatient } = useClinicalViewModel()
  const [query, setQuery] = useState('')
  const [fullName, setFullName] = useState('')
  const [dni, setDni] = useState('')
  const [email, setEmail] = useState('')
  const [birthDate, setBirthDate] = useState('')
  const [conditions, setConditions] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const filtered = useMemo(() => {
    if (!vm) return []
    const q = query.trim().toLowerCase()
    if (!q) return vm.patients
    return vm.patients.filter((p) => {
      const blob = [p.full_name, p.dni ?? '', p.email ?? ''].join(' ').toLowerCase()
      return blob.includes(q)
    })
  }, [vm, query])

  if (loading || !vm) {
    return (
      <div className="rounded-xl border border-thorax-border bg-thorax-card p-8 text-thorax-muted">
        Cargando pacientes…
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-thorax-text">
          Gestión de Pacientes
        </h1>
        <p className="mt-2 text-sm text-thorax-muted">
          Consulta y gestiona todos tus pacientes.
        </p>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-thorax-muted" strokeWidth={1.75} />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar por nombre, DNI o email…"
          className="w-full rounded-xl border border-thorax-border bg-thorax-card py-3 pl-10 pr-4 text-sm text-thorax-text placeholder:text-thorax-muted outline-none ring-thorax-accent focus:ring-1"
        />
      </div>

      <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
        <h2 className="text-lg font-semibold text-thorax-text">Nuevo paciente</h2>
        <form
          className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
          onSubmit={(e) => {
            e.preventDefault()
            setError(null)
            setBusy(true)
            void (async () => {
              try {
                if (dni && !/^\d{8}$/.test(dni)) {
                  throw new Error('DNI debe tener 8 dígitos numéricos.')
                }
                await createPatient({
                  full_name: fullName,
                  dni: dni || null,
                  email: email || null,
                  birth_date: birthDate || null,
                  conditions_summary: conditions || null,
                })
                setFullName('')
                setDni('')
                setEmail('')
                setBirthDate('')
                setConditions('')
              } catch (err) {
                setError(err instanceof Error ? err.message : 'Error al guardar')
              } finally {
                setBusy(false)
              }
            })()
          }}
        >
          <label className="flex flex-col gap-1 text-sm text-thorax-muted">
            Nombre completo
            <input
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-thorax-muted">
            DNI (8 dígitos)
            <input
              value={dni}
              onChange={(e) => setDni(e.target.value)}
              maxLength={8}
              className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-thorax-muted">
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-thorax-muted">
            Fecha de nacimiento
            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
            />
          </label>
          <label className="col-span-full flex flex-col gap-1 text-sm text-thorax-muted sm:col-span-2 lg:col-span-3">
            Condiciones (separadas por coma)
            <input
              value={conditions}
              onChange={(e) => setConditions(e.target.value)}
              placeholder="Ej: Hipertensión, Diabetes tipo 2"
              className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
            />
          </label>
          {error && <p className="col-span-full text-sm text-thorax-danger">{error}</p>}
          <div className="col-span-full">
            <button
              type="submit"
              disabled={busy}
              className="rounded-xl bg-thorax-accent px-5 py-2.5 text-sm font-semibold text-slate-900 hover:bg-thorax-accent-hover disabled:opacity-60"
            >
              {busy ? 'Guardando…' : 'Registrar paciente'}
            </button>
          </div>
        </form>
      </div>

      <div className="overflow-hidden rounded-xl border border-thorax-border bg-thorax-card">
        <div className="thorax-scroll max-w-full overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead>
              <tr className="border-b border-thorax-border bg-thorax-bg-deep/80 text-thorax-muted">
                <th className="px-4 py-3 font-medium">Nombre</th>
                <th className="px-4 py-3 font-medium">DNI</th>
                <th className="px-4 py-3 font-medium">Edad</th>
                <th className="px-4 py-3 font-medium">Condiciones</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => {
                const age = patientAgeYears(p.birth_date)
                const st = patientRowStatus(vm, p.id)
                return (
                  <tr
                    key={p.id}
                    className="border-b border-thorax-border/60 last:border-0 hover:bg-thorax-bg-deep/40"
                  >
                    <td className="px-4 py-4">
                      <p className="font-medium text-thorax-text">{p.full_name}</p>
                      <p className="text-xs text-thorax-muted">{p.email ?? ''}</p>
                    </td>
                    <td className="px-4 py-4 text-thorax-text">{p.dni ?? '—'}</td>
                    <td className="px-4 py-4 text-thorax-muted">
                      {age != null ? `${age} años` : '—'}
                    </td>
                    <td className="max-w-[200px] truncate px-4 py-4 text-thorax-muted">
                      {p.conditions_summary ?? '—'}
                    </td>
                    <td className="px-4 py-4">
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
                    </td>
                    <td className="px-4 py-4">
                      <Link
                        to="/predictions"
                        className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-thorax-border text-thorax-accent hover:bg-thorax-bg-deep"
                        aria-label="Ver predicciones"
                      >
                        <ArrowRight className="h-4 w-4" strokeWidth={1.75} />
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <p className="p-6 text-sm text-thorax-muted">
            No hay pacientes que coincidan con la búsqueda.
          </p>
        )}
      </div>
    </div>
  )
}
