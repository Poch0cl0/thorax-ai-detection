export type User = {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  role: string
  created_at: string
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
  study_instance_uid: string | null
  modality: string
  description: string | null
  image_storage_key: string | null
  created_at: string
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

export type ScanResult = {
  prediction: string
  probability_cancer: number
  probability_normal: number
  risk_level: string
  model_used: string
  model_display_name: string
  model_version: string
  confidence_percent: number
  recommendation: string
  disclaimer: string
}

export type ModelOption = {
  value: string
  label: string
  description: string
}

export type ModelsInfo = {
  available_models: string[]
  model_options: ModelOption[]
}
