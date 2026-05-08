import { useEffect, useState } from 'react'
import * as clinical from '../services/clinicalService'
import type { Patient, Study } from '../types/api'

export function StudiesPage() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [patientId, setPatientId] = useState<number | ''>('')
  const [studies, setStudies] = useState<Study[]>([])
  const [modality, setModality] = useState('CT')
  const [uid, setUid] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const list = await clinical.listPatients()
        if (!cancelled) setPatients(list)
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : 'Error al cargar pacientes')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const handlePatientChange = (value: string) => {
    setError(null)
    if (!value) {
      setPatientId('')
      setStudies([])
      return
    }
    const id = Number(value)
    setPatientId(id)
    void clinical
      .listStudiesByPatient(id)
      .then(setStudies)
      .catch((e: Error) => setError(e.message))
  }

  return (
    <div className="page-card mx-auto max-w-4xl border-thorax-border bg-thorax-card">
      <h1 className="text-2xl font-bold text-thorax-text">Estudios</h1>
      <p className="mt-2 text-sm text-thorax-muted">
        Seleccione un paciente para ver estudios o crear uno nuevo (metadatos;
        imágenes reales vía PACS/almacén según despliegue).
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
                {p.display_name} (ID {p.id})
              </option>
            ))}
          </select>
        </label>
      </div>
      {patientId !== '' && (
        <section className="section">
          <h2>Nuevo estudio</h2>
          <form
            className="inline-form"
            onSubmit={(e) => {
              e.preventDefault()
              setError(null)
              void clinical
                .createStudy({
                  patient_id: Number(patientId),
                  modality,
                  study_instance_uid: uid || null,
                })
                .then(() =>
                  clinical
                    .listStudiesByPatient(Number(patientId))
                    .then(setStudies),
                )
                .catch((err: Error) => setError(err.message))
            }}
          >
            <input
              placeholder="Study UID (opcional)"
              value={uid}
              onChange={(e) => setUid(e.target.value)}
            />
            <input
              placeholder="Modalidad"
              value={modality}
              onChange={(e) => setModality(e.target.value)}
            />
            <button type="submit" className="btn-primary">
              Crear estudio
            </button>
          </form>
        </section>
      )}
      {error && <p className="form-error">{error}</p>}
      <section className="section">
        <h2>Estudios del paciente</h2>
        {studies.length === 0 ? (
          <p className="muted">Sin estudios para este paciente.</p>
        ) : (
          <ul className="data-list plain">
            {studies.map((s) => (
              <li key={s.id}>
                <span className="title">
                  Estudio #{s.id} · {s.modality}
                </span>
                <span className="meta">
                  {s.study_instance_uid ?? 'sin UID'}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
