export type User = {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  role: string
  roles: string[]
  created_at: string
}

export type UserBrief = {
  id: number
  email: string
  full_name: string | null
  roles: string[]
}

export type AppointmentApi = {
  id: number
  patient_id: number
  attending_user_id: number | null
  scheduled_at: string
  status: string
  notes: string | null
  created_by_id: number | null
  created_at: string
  updated_at: string
}

export type Patient = {
  id: number
  external_ref: string | null
  display_name: string
  birth_date: string | null
  notes: string | null
  created_at: string
}

export type Study = {
  id: number
  patient_id: number
  appointment_id?: number | null
  study_instance_uid: string | null
  modality: string
  description: string | null
  image_storage_key: string | null
  created_at?: string
}

export type Prediction = {
  id: number
  study_id: number
  created_by_id: number | null
  model_version: string
  risk_score: number | null
  finding_label: string
  details: Record<string, unknown> | null
  created_at: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}
