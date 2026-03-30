interface PQCBadgeProps {
  status: string
  size?: 'sm' | 'md' | 'lg'
}

const STATUS_STYLES: Record<string, string> = {
  'Elite-PQC': 'bg-green-500/15 text-green-400 border border-green-500/30',
  'Standard': 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
  'Legacy': 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  'Critical': 'bg-red-500/15 text-red-400 border border-red-500/30',
  'SAFE': 'bg-green-500/15 text-green-400 border border-green-500/30',
  'LOW': 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
  'MEDIUM': 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  'HIGH': 'bg-orange-500/15 text-orange-400 border border-orange-500/30',
  'CRITICAL': 'bg-red-500/15 text-red-400 border border-red-500/30',
}

const SIZE_STYLES = {
  sm: 'text-xs px-1.5 py-0.5',
  md: 'text-xs px-2.5 py-1',
  lg: 'text-sm px-3 py-1.5',
}

export default function PQCBadge({ status, size = 'md' }: PQCBadgeProps) {
  const style = STATUS_STYLES[status] || 'bg-slate-500/15 text-slate-400 border border-slate-500/30'
  const sizeStyle = SIZE_STYLES[size]

  return (
    <span className={`inline-flex items-center font-semibold rounded-full whitespace-nowrap ${style} ${sizeStyle}`}>
      {status === 'Elite-PQC' && <span className="mr-1">✓</span>}
      {(status === 'Critical' || status === 'CRITICAL') && <span className="mr-1">⚠</span>}
      {status}
    </span>
  )
}
