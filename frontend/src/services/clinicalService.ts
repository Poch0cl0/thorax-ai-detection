import type { Patient, Prediction, Study } from '../types/api'
import { apiFetch } from './api'

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
