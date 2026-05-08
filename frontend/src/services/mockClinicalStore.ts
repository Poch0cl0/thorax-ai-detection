import type {
  AppointmentRecord,
  DemoClinicalSeed,
  PatientRecord,
} from '../types/clinical-domain'
import seed from '../mocks/demo-clinical.json'

const STORAGE_KEY = 'thorax_clinical_demo_v1'

const listeners = new Set<() => void>()

function cloneSeed(): DemoClinicalSeed {
  return structuredClone(seed) as DemoClinicalSeed
}

function loadFromStorage(): DemoClinicalSeed | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as DemoClinicalSeed
  } catch {
    return null
  }
}

let snapshot: DemoClinicalSeed = loadFromStorage() ?? cloneSeed()

function persist() {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot))
  } catch {
    /* ignore quota */
  }
}

function emit() {
  persist()
  listeners.forEach((l) => l())
}

export function subscribeMockClinical(fn: () => void) {
  listeners.add(fn)
  return () => listeners.delete(fn)
}

export function getMockClinicalSnapshot(): DemoClinicalSeed {
  return snapshot
}

export function resetMockClinical() {
  snapshot = cloneSeed()
  emit()
}

export function addMockPatient(patient: PatientRecord) {
  snapshot = {
    ...snapshot,
    patients: [...snapshot.patients, patient],
  }
  emit()
}

export function addMockAppointment(record: AppointmentRecord) {
  snapshot = {
    ...snapshot,
    appointments: [...snapshot.appointments, record],
  }
  emit()
}

export function addMockPrediction(
  prediction: DemoClinicalSeed['predictions'][number],
) {
  snapshot = {
    ...snapshot,
    predictions: [...snapshot.predictions, prediction],
  }
  emit()
}
