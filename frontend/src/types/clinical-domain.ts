export type AppointmentStatus =
  | 'pendiente'
  | 'en_proceso'
  | 'atendido'
  | 'cancelado'

export type PredictionResult = 'positivo' | 'negativo'

export type SeverityLevel = 'leve' | 'moderado' | 'grave'

export type AppRole = 'especialista' | 'secretaria' | 'admin'

export type PatientRecord = {
  id: string
  full_name: string
  dni: string | null
  birth_date: string | null
  gender: string | null
  phone: string | null
  email: string | null
  conditions_summary: string | null
}

export type SpecialistRecord = {
  id: string
  user_id: string
  cmp: string
  specialty: string
  display_name: string
  email_hint: string | null
}

export type AppointmentRecord = {
  id: string
  patient_id: string
  /** Usuario médico asignado (API: attending_user_id) */
  specialist_id: string | null
  scheduled_at: string
  status: AppointmentStatus
  notes: string | null
}

export type StudyRecord = {
  id: string
  /** Paciente dueño del estudio (necesario si no hay cita enlazada) */
  patient_id: string | null
  appointment_id: string | null
  image_url: string
  study_type: string
  description: string | null
}

export type PredictionRecord = {
  id: string
  study_id: string
  model_version: string
  probability: number
  result: PredictionResult
  finding_label: string
  reviewed: boolean
}

export type DiagnosisRecord = {
  id: string
  appointment_id: string
  specialist_id: string
  prediction_id: string | null
  severity: SeverityLevel | null
}

export type PredictionListRow = {
  prediction: PredictionRecord
  patientName: string
  studySummary: string
  studyDate: string
}

export type DemoUsersMap = Record<
  string,
  { app_role: AppRole; full_name: string }
>

export type DemoClinicalSeed = {
  demo_users: DemoUsersMap
  patients: PatientRecord[]
  specialists: SpecialistRecord[]
  appointments: AppointmentRecord[]
  studies: StudyRecord[]
  predictions: PredictionRecord[]
  diagnoses: DiagnosisRecord[]
}

export type ClinicalViewModel = {
  patients: PatientRecord[]
  specialists: SpecialistRecord[]
  appointments: AppointmentRecord[]
  studies: StudyRecord[]
  predictions: PredictionRecord[]
  diagnoses: DiagnosisRecord[]
  predictionRows: PredictionListRow[]
}
