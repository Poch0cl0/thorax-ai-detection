import { useMemo, useState } from 'react'
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock,
  Info,
  Loader2,
  Play,
  Trash2,
  X,
} from 'lucide-react'
import { useClinicalViewModel } from '../hooks/useClinicalViewModel'
import { StatCard } from '../components/ui/StatCard'
import { AppBadge } from '../components/ui/AppBadge'
import { isClinicalMock } from '../services/clinicalRepository'
import { criticalCasesCount } from '../utils/clinicalStats'
import * as clinicalService from '../services/clinicalService'
import type { Prediction } from '../types/api'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function riskLabel(level: string | undefined | null): string {
  if (level === 'alto') return 'Alto'
  if (level === 'moderado') return 'Moderado'
  if (level === 'bajo') return 'Bajo'
  return level ?? '—'
}

function riskColor(level: string | undefined | null): string {
  if (level === 'alto') return 'text-red-400'
  if (level === 'moderado') return 'text-yellow-400'
  if (level === 'bajo') return 'text-emerald-400'
  return 'text-thorax-muted'
}

function findingDisplay(label: string): string {
  if (label === 'cancer_detected') return 'Anomalía detectada'
  if (label === 'no_cancer') return 'Sin anomalías significativas'
  if (label === 'review_recommended') return 'Revisión recomendada'
  if (label === 'low_suspicion') return 'Baja sospecha'
  return label
}

// ---------------------------------------------------------------------------
// Detail Modal
// ---------------------------------------------------------------------------
function DetailModal({
  prediction,
  onClose,
}: {
  prediction: Prediction
  onClose: () => void
}) {
  const d = prediction.details as Record<string, unknown> | null
  const mode = d?.mode as string | undefined
  const isReal = mode === 'real'

  const probCancer = isReal
    ? (prediction.risk_score ?? 0)
    : null
  const probNormal = isReal
    ? (d?.probability_normal as number | null) ?? null
    : null
  const riskLevel = isReal ? (d?.risk_level as string | undefined) : undefined
  const confidence = isReal ? (d?.confidence_percent as number | undefined) : undefined
  const modelUsed = isReal ? (d?.model_used as string | undefined) : undefined
  const recommendation = isReal
    ? (d?.recommendation as string | undefined)
    : undefined

  const modelDisplayName: Record<string, string> = {
    random_forest: 'Random Forest',
    logistic_regression: 'Regresión Logística',
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Cerrar"
        className="absolute inset-0 z-10 bg-black/60"
        onClick={onClose}
      />
      <div className="relative z-20 w-full max-w-lg rounded-2xl border border-thorax-border bg-thorax-card-alt p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-thorax-text">
            <Info className="h-5 w-5 text-thorax-accent" />
            Detalle del análisis IA
          </h3>
          <button
            type="button"
            className="text-thorax-muted hover:text-thorax-text"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-5 space-y-4">
          {/* Resultado principal */}
          <div className={[
            'rounded-xl border px-4 py-3',
            prediction.finding_label === 'cancer_detected'
              ? 'border-red-500/30 bg-red-500/10'
              : 'border-emerald-500/30 bg-emerald-500/10',
          ].join(' ')}>
            <p className="text-xs font-medium uppercase tracking-wide text-thorax-muted">
              Resultado
            </p>
            <p className={[
              'mt-1 text-base font-semibold',
              prediction.finding_label === 'cancer_detected'
                ? 'text-red-400'
                : 'text-emerald-400',
            ].join(' ')}>
              {findingDisplay(prediction.finding_label)}
            </p>
          </div>

          {/* Probabilidades (solo modo real) */}
          {isReal && probCancer !== null && probNormal !== null && (
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-wide text-thorax-muted">
                Distribución de probabilidad
              </p>
              <div className="space-y-2">
                <div>
                  <div className="mb-1 flex justify-between text-xs text-thorax-muted">
                    <span>Probabilidad de anomalía</span>
                    <span className="font-semibold text-red-400">
                      {(probCancer * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-thorax-bg-deep">
                    <div
                      className="h-full rounded-full bg-red-500"
                      style={{ width: `${probCancer * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="mb-1 flex justify-between text-xs text-thorax-muted">
                    <span>Probabilidad normal</span>
                    <span className="font-semibold text-emerald-400">
                      {(probNormal * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-thorax-bg-deep">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${probNormal * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Chips de metadata */}
          <div className="grid grid-cols-2 gap-2">
            {riskLevel && (
              <div className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2">
                <p className="text-xs text-thorax-muted">Nivel de riesgo</p>
                <p className={['mt-0.5 text-sm font-semibold', riskColor(riskLevel)].join(' ')}>
                  {riskLabel(riskLevel)}
                </p>
              </div>
            )}
            {confidence !== undefined && (
              <div className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2">
                <p className="text-xs text-thorax-muted">Confianza</p>
                <p className="mt-0.5 text-sm font-semibold text-thorax-text">
                  {confidence.toFixed(1)}%
                </p>
              </div>
            )}
            {modelUsed && (
              <div className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2">
                <p className="text-xs text-thorax-muted">Modelo usado</p>
                <p className="mt-0.5 text-sm font-semibold text-thorax-text">
                  {modelDisplayName[modelUsed] ?? modelUsed}
                </p>
              </div>
            )}
            <div className="rounded-lg border border-thorax-border bg-thorax-bg-deep px-3 py-2">
              <p className="text-xs text-thorax-muted">Versión</p>
              <p className="mt-0.5 text-sm font-semibold text-thorax-text">
                {prediction.model_version}
              </p>
            </div>
          </div>

          {/* Recomendación */}
          {recommendation && (
            <div className="rounded-xl border border-thorax-accent/20 bg-thorax-accent/5 px-4 py-3">
              <p className="text-xs font-medium uppercase tracking-wide text-thorax-accent">
                Recomendación clínica
              </p>
              <p className="mt-1.5 text-sm leading-relaxed text-thorax-text/90">
                {recommendation}
              </p>
            </div>
          )}

          {/* Modo stub */}
          {!isReal && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3">
              <p className="text-xs font-medium uppercase tracking-wide text-amber-400">
                Modo simulado
              </p>
              <p className="mt-1 text-sm text-thorax-muted">
                Este resultado fue generado por el modo de compatibilidad
                (stub) porque no había imagen o el modelo no estaba disponible
                al momento del análisis.
              </p>
            </div>
          )}

          {/* Disclaimer */}
          <p className="text-xs text-thorax-muted/70 leading-relaxed">
            Este sistema es una herramienta de apoyo académico y NO sustituye
            el diagnóstico médico profesional. Los resultados deben ser
            interpretados por personal de salud calificado.
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="mt-5 w-full rounded-xl border border-thorax-border py-2.5 text-sm font-medium text-thorax-text hover:bg-thorax-bg-deep"
        >
          Cerrar
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export function PredictionsPage() {
  const {
    vm,
    loading,
    mode,
    refreshApi,
    runPredictionApi,
    runPredictionDemo,
  } = useClinicalViewModel()

  const [studyId, setStudyId] = useState('')
  const [findingLabel, setFindingLabel] = useState('Hallazgo sospechoso')
  const [runBusy, setRunBusy] = useState(false)
  const [runError, setRunError] = useState<string | null>(null)

  const [clearing, setClearing] = useState(false)
  const [clearError, setClearError] = useState<string | null>(null)

  const [detailPrediction, setDetailPrediction] = useState<Prediction | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  const stats = useMemo(() => {
    if (!vm) return { total: 0, pending: 0, reviewed: 0, critical: 0 }
    return {
      total: vm.predictions.length,
      pending: vm.predictions.filter((p) => !p.reviewed).length,
      reviewed: vm.predictions.filter((p) => p.reviewed).length,
      critical: criticalCasesCount(vm),
    }
  }, [vm])

  async function handleClearAll() {
    if (!window.confirm('¿Eliminar todas las predicciones? Esta acción no se puede deshacer.')) return
    setClearing(true)
    setClearError(null)
    try {
      await clinicalService.clearAllPredictions()
      await refreshApi()
    } catch {
      setClearError('No se pudo limpiar. Comprueba permisos de médico o administrador.')
    } finally {
      setClearing(false)
    }
  }

  async function handleOpenDetail(predictionId: string) {
    setDetailLoading(true)
    try {
      const full = await clinicalService.getPrediction(Number(predictionId))
      setDetailPrediction(full)
    } catch {
      // no-op
    } finally {
      setDetailLoading(false)
    }
  }

  if (loading || !vm) {
    return (
      <div className="rounded-xl border border-thorax-border bg-thorax-card p-8 text-thorax-muted">
        Cargando predicciones…
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-thorax-text">
            Predicciones IA
          </h1>
          <p className="mt-2 text-sm text-thorax-muted">
            Análisis de Inteligencia Artificial de estudios radiológicos.
          </p>
        </div>
        {mode === 'api' && vm.predictions.length > 0 && (
          <button
            type="button"
            disabled={clearing}
            onClick={() => void handleClearAll()}
            className="inline-flex items-center gap-2 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-400 hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {clearing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
            Limpiar todo
          </button>
        )}
      </div>

      {clearError && (
        <p className="rounded-xl border border-thorax-border bg-thorax-card px-4 py-3 text-sm text-thorax-danger">
          {clearError}
        </p>
      )}

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total"
          value={stats.total}
          icon={Activity}
          className="ring-1 ring-thorax-accent/40"
        />
        <StatCard label="Pendientes" value={stats.pending} icon={Clock} variant="danger" />
        <StatCard label="Revisados" value={stats.reviewed} icon={CheckCircle2} />
        <StatCard label="Críticos" value={stats.critical} icon={AlertCircle} variant="danger" />
      </div>

      {/* Ejecutar inferencia */}
      <div className="rounded-xl border border-thorax-border bg-thorax-card p-6">
        <h2 className="text-lg font-semibold text-thorax-text">Ejecutar inferencia</h2>
        <p className="mt-1 text-sm text-thorax-muted">
          {mode === 'mock'
            ? 'Modo demo: añade una predicción al estudio seleccionado.'
            : 'Genera una predicción sobre un estudio existente.'}
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
                  setRunError(e instanceof Error ? e.message : 'No se pudo ejecutar')
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
        {runError && <p className="mt-3 text-sm text-thorax-danger">{runError}</p>}
      </div>

      {/* Lista de predicciones */}
      <div className="space-y-3">
        {[...vm.predictionRows].map((row) => {
          const pct = Math.round(row.prediction.probability * 100)
          const pending = !row.prediction.reviewed
          const isAnomaly =
            row.prediction.finding_label === 'cancer_detected' ||
            row.prediction.finding_label === 'review_recommended'

          return (
            <div
              key={row.prediction.id}
              className="flex flex-col gap-4 rounded-xl border border-thorax-border bg-thorax-card p-4 sm:flex-row sm:items-center"
            >
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-thorax-text">{row.patientName}</p>
                <p className="mt-1 text-xs text-thorax-muted">{row.studySummary}</p>
                <p className={[
                  'mt-2 text-sm font-medium',
                  isAnomaly ? 'text-red-400' : 'text-emerald-400',
                ].join(' ')}>
                  {findingDisplay(row.prediction.finding_label)}
                  <span className="ml-2 font-normal text-thorax-muted">
                    ({pct}% prob.)
                  </span>
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
                  <span className="ml-1 text-xs font-normal text-thorax-muted">prob. máx.</span>
                </p>
                <button
                  type="button"
                  disabled={detailLoading && mode === 'api'}
                  onClick={() => {
                    if (mode === 'api') {
                      void handleOpenDetail(row.prediction.id)
                    }
                  }}
                  className="inline-flex items-center justify-end gap-1 text-thorax-accent hover:underline disabled:opacity-50"
                >
                  {detailLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      Detalle
                      <ChevronRight className="h-4 w-4" strokeWidth={1.75} />
                    </>
                  )}
                </button>
              </div>
            </div>
          )
        })}
        {vm.predictionRows.length === 0 && (
          <p className="rounded-xl border border-dashed border-thorax-border/60 bg-thorax-card-alt/60 px-4 py-10 text-center text-sm text-thorax-muted">
            Sin predicciones todavía. Los resultados aparecen aquí al atender una cita con análisis IA.
          </p>
        )}
      </div>

      {!isClinicalMock() && vm.predictionRows.length === 0 && (
        <p className="text-xs text-thorax-muted">
          Para generar predicciones, inicia una cita desde "Atender citas" y sube una radiografía.
        </p>
      )}

      {/* Modal de detalle */}
      {detailPrediction && (
        <DetailModal
          prediction={detailPrediction}
          onClose={() => setDetailPrediction(null)}
        />
      )}
    </div>
  )
}
