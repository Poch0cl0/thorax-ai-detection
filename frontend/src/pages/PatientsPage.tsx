import { useEffect, useState } from 'react'
import { PatientList } from '../features/patients/PatientList'
import * as clinical from '../services/clinicalService'
import type { Patient } from '../types/api'

export function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [externalRef, setExternalRef] = useState('')

  useEffect(() => {
    let cancelled = false
    void (async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await clinical.listPatients()
        if (!cancelled) setPatients(data)
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : 'Error al cargar')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="page-card">
      <h1>Pacientes</h1>
      <section className="section">
        <h2>Nuevo paciente</h2>
        <form
          className="inline-form"
          onSubmit={(e) => {
            e.preventDefault()
            setError(null)
            void clinical
              .createPatient({
                display_name: name,
                external_ref: externalRef || null,
              })
              .then(() => {
                setName('')
                setExternalRef('')
                return clinical.listPatients()
              })
              .then(setPatients)
              .catch((err: Error) => setError(err.message))
          }}
        >
          <input
            placeholder="Nombre (pseudónimo clínico)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            placeholder="Ref. externa HIS (opcional)"
            value={externalRef}
            onChange={(e) => setExternalRef(e.target.value)}
          />
          <button type="submit" className="btn-primary">
            Guardar
          </button>
        </form>
      </section>
      <section className="section">
        <h2>Listado</h2>
        {loading && <p className="muted">Cargando…</p>}
        {error && <p className="form-error">{error}</p>}
        <PatientList patients={patients} selectedId={null} />
      </section>
    </div>
  )
}
