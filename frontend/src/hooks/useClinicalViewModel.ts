import {
  useMemo,
  useState,
  useCallback,
  useEffect,
  useSyncExternalStore,
} from 'react'
import type {
  AppointmentRecord,
  ClinicalViewModel,
} from '../types/clinical-domain'
import {
  deriveViewModel,
  loadClinicalViewModelFromApi,
  isClinicalMock,
} from '../services/clinicalRepository'
import {
  subscribeMockClinical,
  getMockClinicalSnapshot,
  resetMockClinical,
  addMockPatient,
  addMockAppointment,
  addMockPrediction,
} from '../services/mockClinicalStore'
import * as clinicalService from '../services/clinicalService'

export function useClinicalViewModel() {
  const mock = isClinicalMock()
  const snap = useSyncExternalStore(
    mock ? subscribeMockClinical : () => () => {},
    () => getMockClinicalSnapshot(),
    () => getMockClinicalSnapshot(),
  )

  const mockVm = useMemo(
    () => (mock ? deriveViewModel(snap) : null),
    [mock, snap],
  )

  const [apiVm, setApiVm] = useState<ClinicalViewModel | null>(null)
  const [apiLoading, setApiLoading] = useState(!mock)

  const refreshApi = useCallback(async () => {
    if (mock) return
    setApiLoading(true)
    try {
      setApiVm(await loadClinicalViewModelFromApi())
    } catch {
      setApiVm(null)
    } finally {
      setApiLoading(false)
    }
  }, [mock])

  useEffect(() => {
    if (mock) return
    const t = window.setTimeout(() => {
      void refreshApi()
    }, 0)
    return () => window.clearTimeout(t)
  }, [mock, refreshApi])

  const vm = mock ? mockVm : apiVm
  const loading = mock ? false : apiLoading

  const createPatientDemo = useCallback(
    (input: {
      full_name: string
      dni?: string | null
      birth_date?: string | null
      email?: string | null
      conditions_summary?: string | null
    }) => {
      if (!mock) return
      addMockPatient({
        id: crypto.randomUUID(),
        full_name: input.full_name,
        dni: input.dni && /^\d{8}$/.test(input.dni) ? input.dni : null,
        birth_date: input.birth_date ?? null,
        gender: null,
        phone: null,
        email: input.email ?? null,
        conditions_summary: input.conditions_summary?.trim() || null,
      })
    },
    [mock],
  )

  const createPatientApi = useCallback(
    async (input: {
      full_name: string
      dni?: string | null
      birth_date?: string | null
      email?: string | null
      conditions_summary?: string | null
    }) => {
      await clinicalService.createPatient({
        display_name: input.full_name,
        external_ref: input.dni && input.dni.length > 0 ? input.dni : null,
        birth_date: input.birth_date ?? null,
        notes: input.conditions_summary ?? null,
      })
      await refreshApi()
    },
    [refreshApi],
  )

  const createAppointmentDemo = useCallback(
    (
      input: Omit<AppointmentRecord, 'id' | 'status'> & {
        status?: AppointmentRecord['status']
      },
    ) => {
      if (!mock) return
      addMockAppointment({
        id: crypto.randomUUID(),
        patient_id: input.patient_id,
        specialist_id: input.specialist_id,
        scheduled_at: input.scheduled_at,
        status: input.status ?? 'pendiente',
        notes: input.notes ?? null,
      })
    },
    [mock],
  )

  const runPredictionDemo = useCallback(
    (studyId: string, finding_label: string) => {
      if (!mock) return
      addMockPrediction({
        id: crypto.randomUUID(),
        study_id: studyId,
        model_version: 'thorax-demo',
        probability: Math.round(55 + Math.random() * 40) / 100,
        result: 'positivo',
        finding_label,
        reviewed: false,
      })
    },
    [mock],
  )

  const runPredictionApi = useCallback(
    async (studyId: number, modelType?: string) => {
      await clinicalService.runPrediction(studyId, modelType)
      await refreshApi()
    },
    [refreshApi],
  )

  const resetDemo = useCallback(() => {
    if (mock) resetMockClinical()
  }, [mock])

  const createPatient = useCallback(
    async (input: {
      full_name: string
      dni?: string | null
      birth_date?: string | null
      email?: string | null
      conditions_summary?: string | null
    }) => {
      if (mock) {
        createPatientDemo(input)
        return
      }
      await createPatientApi(input)
    },
    [mock, createPatientDemo, createPatientApi],
  )

  return {
    mode: mock ? ('mock' as const) : ('api' as const),
    vm,
    loading,
    refreshApi,
    resetDemo,
    createPatient,
    createAppointmentDemo,
    runPredictionApi,
    runPredictionDemo,
  }
}
