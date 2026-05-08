import type { LucideIcon } from 'lucide-react'

type Props = {
  label: string
  value: string | number
  icon: LucideIcon
  variant?: 'default' | 'accent' | 'danger' | 'dangerBorder'
  className?: string
}

export function StatCard({
  label,
  value,
  icon: Icon,
  variant = 'default',
  className = '',
}: Props) {
  const valueColor =
    variant === 'danger' || variant === 'dangerBorder'
      ? 'text-thorax-danger'
      : variant === 'accent'
        ? 'text-thorax-accent'
        : 'text-thorax-text'
  const border =
    variant === 'dangerBorder' ? 'ring-1 ring-thorax-danger/40' : ''

  return (
    <div
      className={`rounded-xl border border-thorax-border bg-thorax-card p-4 shadow-sm ${border} ${className}`}
    >
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-thorax-muted">{label}</p>
        <Icon
          className={`h-5 w-5 shrink-0 ${variant === 'danger' || variant === 'dangerBorder' ? 'text-thorax-danger' : 'text-thorax-accent'}`}
          strokeWidth={1.75}
        />
      </div>
      <p className={`mt-2 text-3xl font-semibold tabular-nums ${valueColor}`}>
        {value}
      </p>
    </div>
  )
}
