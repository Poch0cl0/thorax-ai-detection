import type { Patient } from '../../types/api'

type Props = {
  patients: Patient[]
  onSelect?: (p: Patient) => void
  selectedId: number | null
}

export function PatientList({ patients, onSelect, selectedId }: Props) {
  if (patients.length === 0) {
    return <p className="muted">No hay pacientes registrados aún.</p>
  }
  return (
    <ul className="data-list">
      {patients.map((p) => (
        <li key={p.id}>
          <button
            type="button"
            className={
              selectedId === p.id ? 'list-item active' : 'list-item'
            }
            onClick={() => onSelect?.(p)}
          >
            <span className="title">{p.display_name}</span>
            <span className="meta">
              ID {p.id}
              {p.external_ref ? ` · Ref: ${p.external_ref}` : ''}
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
