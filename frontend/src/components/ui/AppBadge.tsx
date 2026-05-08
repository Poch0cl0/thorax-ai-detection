type Props = {
  children: React.ReactNode
  variant?: 'neutral' | 'success' | 'warning' | 'danger'
  className?: string
}

const variants: Record<NonNullable<Props['variant']>, string> = {
  neutral: 'bg-thorax-border/50 text-thorax-text',
  success: 'bg-emerald-500/15 text-emerald-300',
  warning: 'bg-amber-500/15 text-amber-200',
  danger: 'bg-thorax-danger/20 text-rose-200',
}

export function AppBadge({
  children,
  variant = 'neutral',
  className = '',
}: Props) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  )
}
