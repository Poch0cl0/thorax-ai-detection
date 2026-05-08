import type { ClinicalViewModel } from '../types/clinical-domain'

function patientStudyIds(vm: ClinicalViewModel, patientId: string): Set<string> {
  const apptIds = new Set(
    vm.appointments
      .filter((a) => a.patient_id === patientId)
      .map((a) => a.id),
  )
  return new Set(
    vm.studies
      .filter(
        (s) =>
          s.appointment_id != null &&
          apptIds.has(s.appointment_id),
      )
      .map((s) => s.id),
  )
}

/** Estado de fila tipo mockup: revisado / pendiente / sin análisis */
export function patientRowStatus(vm: ClinicalViewModel, patientId: string): {
  label: string
  kind: 'done' | 'pending' | 'none'
} {
  const ids = patientStudyIds(vm, patientId)
  const preds = vm.predictions.filter((p) => ids.has(p.study_id))
  if (preds.length === 0) return { label: 'Sin análisis', kind: 'none' }
  const pending = preds.some((p) => !p.reviewed)
  if (pending) return { label: 'Pendiente', kind: 'pending' }
  return { label: 'Revisado', kind: 'done' }
}

export function appointmentsTodayCount(vm: ClinicalViewModel): number {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth()
  const d = now.getDate()
  return vm.appointments.filter((a) => {
    const t = new Date(a.scheduled_at)
    return (
      t.getFullYear() === y &&
      t.getMonth() === m &&
      t.getDate() === d &&
      a.status !== 'cancelado'
    )
  }).length
}

export function predictionsPendingCount(vm: ClinicalViewModel): number {
  return vm.predictions.filter((p) => !p.reviewed).length
}

export function criticalCasesCount(vm: ClinicalViewModel): number {
  const graveDx = vm.diagnoses.filter((x) => x.severity === 'grave').length
  const urgentPred = vm.predictions.filter(
    (p) =>
      !p.reviewed &&
      p.result === 'positivo' &&
      p.probability >= 0.9,
  ).length
  return graveDx + urgentPred
}
