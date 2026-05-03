import { useEffect, useState } from 'react'
import * as clinical from '../services/clinicalService'
import type { Patient, Prediction, Study } from '../types/api'

export function PredictPage() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [studies, setStudies] = useState<Study[]>([])
  const [patientId, setPatientId] = useState<number | ''>('')
  const [studyId, setStudyId] = useState<number | ''>('')
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [last, setLast] = useState<Prediction | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const list = await clinical.listPatients()
        if (!cancelled) setPatients(list)
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : 'Error al cargar')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const handlePatientChange = (value: string) => {
    setError(null)
    setLast(null)
    if (!value) {
      setPatientId('')
      setStudies([])
      setStudyId('')
      setPredictions([])
      return
    }
    const id = Number(value)
    setPatientId(id)
    void clinical
      .listStudiesByPatient(id)
      .then((s) => {
        setStudies(s)
        if (s.length > 0) {
          const first = s[0].id
          setStudyId(first)
          return clinical.listPredictionsForStudy(first)
        }
        setStudyId('')
        setPredictions([])
        return Promise.resolve([])
      })
      .then(setPredictions)
      .catch((e: Error) => setError(e.message))
  }

  const handleStudyChange = (value: string) => {
    setError(null)
    if (!value) {
      setStudyId('')
      setPredictions([])
      return
    }
    const id = Number(value)
    setStudyId(id)
    void clinical
      .listPredictionsForStudy(id)
      .then(setPredictions)
      .catch((e: Error) => setError(e.message))
  }

  return (
    <div className="page-card">
      <h1>Predicción asistida</h1>
      <p className="muted">
        Ejecuta el pipeline de IA (simulado si no hay MODEL_PATH). Los
        resultados son de apoyo clínico y requieren validación profesional.
      </p>
      <div className="field-row">
        <label>
          Paciente
          <select
            value={patientId === '' ? '' : String(patientId)}
            onChange={(e) => handlePatientChange(e.target.value)}
          >
            <option value="">— Elegir —</option>
            {patients.map((p) => (
              <option key={p.id} value={p.id}>
                {p.display_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Estudio
          <select
            value={studyId === '' ? '' : String(studyId)}
            onChange={(e) => handleStudyChange(e.target.value)}
            disabled={studies.length === 0}
          >
            <option value="">
              {studies.length === 0 ? 'Sin estudios' : '— Elegir —'}
            </option>
            {studies.map((s) => (
              <option key={s.id} value={s.id}>
                #{s.id} · {s.modality}{' '}
                {s.study_instance_uid
                  ? `· ${s.study_instance_uid.slice(0, 12)}…`
                  : ''}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="btn-primary"
          disabled={busy || studyId === ''}
          onClick={() => {
            setBusy(true)
            setError(null)
            void clinical
              .runPrediction(Number(studyId))
              .then((pred) => {
                setLast(pred)
                return clinical.listPredictionsForStudy(Number(studyId))
              })
              .then(setPredictions)
              .catch((e: Error) => setError(e.message))
              .finally(() => setBusy(false))
          }}
        >
          {busy ? 'Procesando…' : 'Ejecutar inferencia'}
        </button>
      </div>
      {error && <p className="form-error">{error}</p>}
      {last && (
        <section className="section result-box">
          <h2>Última predicción</h2>
          <p>
            <strong>Etiqueta:</strong> {last.finding_label}
          </p>
          <p>
            <strong>Puntuación:</strong>{' '}
            {last.risk_score != null ? last.risk_score : '—'}
          </p>
          <p className="muted">
            <strong>Modelo:</strong> {last.model_version}
          </p>
        </section>
      )}
      <section className="section">
        <h2>Historial del estudio</h2>
        {predictions.length === 0 ? (
          <p className="muted">Sin predicciones todavía.</p>
        ) : (
          <ul className="data-list plain">
            {predictions.map((p) => (
              <li key={p.id}>
                <span className="title">
                  #{p.id} · {p.finding_label}
                </span>
                <span className="meta">
                  score {p.risk_score ?? '—'} · {p.created_at}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
