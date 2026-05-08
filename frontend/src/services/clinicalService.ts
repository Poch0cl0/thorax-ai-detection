import type { ModelsInfo,
  AppointmentApi,
  Patient,
  Prediction, ScanResult,
  Study,
  UserBrief,
} from '../types/api'
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

export async function listClinicians(): Promise<UserBrief[]> {
  return apiFetch<UserBrief[]>('/api/v1/users/specialists-clinicians')
}

export async function listAppointments(params?: {
  scheduled_from?: string
  scheduled_to?: string
}): Promise<AppointmentApi[]> {
  const sp = new URLSearchParams()
  if (params?.scheduled_from) sp.set('scheduled_from', params.scheduled_from)
  if (params?.scheduled_to) sp.set('scheduled_to', params.scheduled_to)
  const q = sp.toString()
  return apiFetch<AppointmentApi[]>(
    `/api/v1/appointments${q ? `?${q}` : ''}`,
  )
}

export async function createAppointment(body: {
  patient_id: number
  attending_user_id: number
  scheduled_at: string
  notes?: string | null
  status?: string
}): Promise<AppointmentApi> {
  return apiFetch<AppointmentApi>('/api/v1/appointments', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function updateAppointment(
  id: number,
  body: Partial<{
    patient_id: number
    attending_user_id: number | null
    scheduled_at: string
    notes: string | null
    status: string
  }>,
): Promise<AppointmentApi> {
  return apiFetch<AppointmentApi>(`/api/v1/appointments/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}

export async function deleteAppointment(id: number): Promise<void> {
  return apiFetch<void>(`/api/v1/appointments/${id}`, {
    method: 'DELETE',
  })
}

export async function listStudiesByPatient(
  patientId: number,
): Promise<Study[]> {
  return apiFetch<Study[]>(`/api/v1/studies/patient/${patientId}`)
}

export async function createStudy(body: {
  patient_id: number
  appointment_id?: number | null
  study_instance_uid?: string | null
  modality?: string
  description?: string | null
}): Promise<Study> {
  return apiFetch<Study>('/api/v1/studies', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

/** Sube imagen (RX/PNG/JPEG) y crea estudio vinculado. */
export async function createStudyWithImage(body: {
  patient_id: number
  appointment_id?: number | null
  modality?: string
  description?: string | null
  file: File
}): Promise<Study> {
  const fd = new FormData()
  fd.set('patient_id', String(body.patient_id))
  if (body.appointment_id != null)
    fd.set('appointment_id', String(body.appointment_id))
  fd.set('modality', body.modality ?? 'radiografia')
  if (body.description) fd.set('description', body.description)
  fd.set('file', body.file)
  return apiFetch<Study>('/api/v1/studies/with-image', {
    method: 'POST',
    body: fd,
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
