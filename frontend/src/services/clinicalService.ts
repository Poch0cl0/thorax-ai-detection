import type { ModelsInfo, Patient, Prediction, ScanResult, Study } from '../types/api'
import { apiFetch, getApiBase } from './api'

export async function listPatients(): Promise<Patient[]> {
  return apiFetch<Patient[]>('/api/v1/patients?limit=200')
}

export async function createPatient(body: {
  display_name: string
  external_ref?: string | null
  birth_date?: string | null
  notes?: string | null
}): Promise<Patient> {
  return apiFetch<Patient>('/api/v1/patients', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function listStudiesByPatient(
  patientId: number,
): Promise<Study[]> {
  return apiFetch<Study[]>(`/api/v1/studies/patient/${patientId}`)
}

export async function createStudy(body: {
  patient_id: number
  study_instance_uid?: string | null
  modality?: string
  description?: string | null
}): Promise<Study> {
  return apiFetch<Study>('/api/v1/studies', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function runPrediction(studyId: number): Promise<Prediction> {
  return apiFetch<Prediction>('/api/v1/predictions', {
    method: 'POST',
    body: JSON.stringify({ study_id: studyId }),
  })
}

export async function listPredictionsForStudy(
  studyId: number,
): Promise<Prediction[]> {
  return apiFetch<Prediction[]>(`/api/v1/predictions/study/${studyId}`)
}

/**
 * Analiza una imagen de radiografía de tórax usando los modelos ML.
 * Este endpoint es público (no requiere autenticación).
 */
export async function analyzeScan(
  file: File,
  modelType: string = 'random_forest',
): Promise<ScanResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('model_type', modelType)

  const base = getApiBase()
  const res = await fetch(`${base}/api/v1/scan/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      const err = (await res.json()) as { detail?: unknown }
      if (typeof err.detail === 'string') detail = err.detail
      else if (Array.isArray(err.detail)) detail = JSON.stringify(err.detail)
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }

  return res.json() as Promise<ScanResult>
}

/**
 * Obtiene la lista de modelos ML disponibles.
 * Este endpoint es público (no requiere autenticación).
 */
export async function getAvailableModels(): Promise<ModelsInfo> {
  const base = getApiBase()
  const res = await fetch(`${base}/api/v1/scan/models`)
  if (!res.ok) throw new Error('Error al obtener modelos disponibles')
  return res.json() as Promise<ModelsInfo>
}
