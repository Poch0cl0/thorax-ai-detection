import { useMemo, useState } from 'react'
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock,
  Play,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useClinicalViewModel } from '../hooks/useClinicalViewModel'
import { StatCard } from '../components/ui/StatCard'
import { AppBadge } from '../components/ui/AppBadge'
import { isClinicalMock } from '../services/clinicalRepository'
import { criticalCasesCount } from '../utils/clinicalStats'

export function PredictionsPage() {
  const {
    vm,
    loading,
    mode,
    runPredictionApi,
    runPredictionDemo,
  } = useClinicalViewModel()

  const [studyId, setStudyId] = useState('')
  const [findingLabel, setFindingLabel] = useState('Hallazgo sospechoso')
  const [runBusy, setRunBusy] = useState(false)
  const [runError, setRunError] = useState<string | null>(null)

  const stats = useMemo(() => {
    if (!vm)
      return {
        total: 0,
        pending: 0,
        reviewed: 0,
        critical: 0,
      }
    const total = vm.predictions.length
    const pending = vm.predictions.filter((p) => !p.reviewed).length
    const reviewed = vm.predictions.filter((p) => p.reviewed).length
    const critical = criticalCasesCount(vm)
    return { total, pending, reviewed, critical }
  }, [vm])

  if (loading || !vm) {
    return (
      <div className="rounded-xl border border-thorax-border bg-thorax-card p-8 text-thorax-muted">
        Cargando predicciones…
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-thorax-text">
          Predicciones IA
        </h1>
        <p className="mt-2 text-sm text-thorax-muted">
          Análisis de Inteligencia Artificial de estudios radiológicos.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total"
          value={stats.total}
          icon={Activity}
          className="ring-1 ring-thorax-accent/40"
        />
        <StatCard
          label="Pendientes"
          value={stats.pending}
          icon={Clock}
          variant="danger"
        />
        <StatCard label="Revisados" value={stats.reviewed} icon={CheckCircle2} />
        <StatCard
          label="Críticos"
          value={stats.critical}
          icon={AlertCircle}
          variant="danger"
        />
      </div>

      <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
        <h2 className="text-lg font-semibold text-thorax-text">
          Ejecutar inferencia
        </h2>
        <p className="mt-1 text-sm text-thorax-muted">
          {mode === 'mock'
            ? 'Modo demo: añade una predicción al estudio seleccionado.'
            : 'Usa tu API FastAPI para generar una predicción sobre un estudio existente.'}
        </p>
        <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-end">
          <label className="flex min-w-[200px] flex-1 flex-col gap-1 text-sm text-thorax-muted">
            Estudio
            <select
              value={studyId}
              onChange={(e) => setStudyId(e.target.value)}
              className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
            >
              <option value="">Seleccionar estudio…</option>
              {vm.studies.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.description ?? s.study_type} (#{s.id.slice(0, 8)})
                </option>
              ))}
            </select>
          </label>
          {mode === 'mock' && (
            <label className="flex min-w-[200px] flex-1 flex-col gap-1 text-sm text-thorax-muted">
              Hallazgo (etiqueta)
              <input
                value={findingLabel}
                onChange={(e) => setFindingLabel(e.target.value)}
                className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2 text-thorax-text outline-none focus:ring-1 focus:ring-thorax-accent"
              />
            </label>
          )}
          <button
            type="button"
            disabled={runBusy || studyId === ''}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-thorax-accent px-5 py-2.5 text-sm font-semibold text-slate-900 hover:bg-thorax-accent-hover disabled:opacity-50"
            onClick={() => {
              setRunError(null)
              setRunBusy(true)
              void (async () => {
                try {
                  if (mode === 'mock') {
                    runPredictionDemo(studyId, findingLabel.trim() || 'Hallazgo')
                  } else {
                    await runPredictionApi(Number(studyId))
                  }
                } catch (e) {
                  setRunError(
                    e instanceof Error ? e.message : 'No se pudo ejecutar',
                  )
                } finally {
                  setRunBusy(false)
                }
              })()
            }}
          >
            <Play className="h-4 w-4 fill-current" />
            {runBusy ? 'Procesando…' : 'Ejecutar inferencia'}
          </button>
        </div>
        {runError && (
          <p className="mt-3 text-sm text-thorax-danger">{runError}</p>
        )}
      </div>

      <div className="space-y-3">
        {[...vm.predictionRows].map((row) => {
          const pct = Math.round(row.prediction.probability * 100)
          const pending = !row.prediction.reviewed
          return (
            <div
              key={row.prediction.id}
              className="flex flex-col gap-4 rounded-xl border border-thorax-border bg-thorax-card p-4 sm:flex-row sm:items-center"
            >
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-thorax-text">{row.patientName}</p>
                <p className="mt-1 text-xs text-thorax-muted">
                  {row.studySummary}
                </p>
                <p className="mt-2 text-sm text-thorax-text">
                  <span className="text-thorax-muted">IA: </span>
                  {row.prediction.finding_label} ({pct}%)
                </p>
              </div>
              <div className="flex flex-col items-stretch gap-2 sm:items-end">
                {pending ? (
                  <AppBadge variant="danger">Pendiente</AppBadge>
                ) : (
                  <span className="inline-flex items-center gap-1 text-sm text-emerald-300">
                    <CheckCircle2 className="h-4 w-4" strokeWidth={1.75} />
                    Revisado
                  </span>
                )}
                <p className="text-right text-lg font-semibold text-thorax-text">
                  {pct}%
                  <span className="ml-1 text-xs font-normal text-thorax-muted">
                    prob. máx.
                  </span>
                </p>
                <Link
                  to="/patients"
                  className="inline-flex items-center justify-end gap-1 text-thorax-accent hover:underline"
                >
                  Detalle
                  <ChevronRight className="h-4 w-4" strokeWidth={1.75} />
                </Link>
              </div>
            </div>
          )
        })}
        {vm.predictionRows.length === 0 && (
          <p className="text-sm text-thorax-muted">Sin predicciones todavía.</p>
        )}
      </div>

      {!isClinicalMock() && (
        <p className="text-xs text-thorax-muted">
          Las citas y el calendario avanzado requieren el modo mock o un backend
          ampliado.
        </p>
      )}
    </div>
  )
}
