import type { HNDLRisk } from '../types'

interface HNDLCountdownProps {
  hndl: Partial<HNDLRisk>
  compact?: boolean
}

const RISK_COLORS: Record<string, { bg: string; text: string; bar: string; border: string }> = {
  SAFE: { bg: 'bg-green-950/40', text: 'text-green-400', bar: 'bg-green-500', border: 'border-green-700/30' },
  LOW: { bg: 'bg-blue-950/40', text: 'text-blue-400', bar: 'bg-blue-500', border: 'border-blue-700/30' },
  MEDIUM: { bg: 'bg-amber-950/40', text: 'text-amber-400', bar: 'bg-amber-500', border: 'border-amber-700/30' },
  HIGH: { bg: 'bg-orange-950/40', text: 'text-orange-400', bar: 'bg-orange-500', border: 'border-orange-700/30' },
  CRITICAL: { bg: 'bg-red-950/40', text: 'text-red-400', bar: 'bg-red-500', border: 'border-red-700/30' },
}

export default function HNDLCountdown({ hndl, compact = false }: HNDLCountdownProps) {
  const level = hndl?.hndl_risk_level || 'MEDIUM'
  const colors = RISK_COLORS[level] || RISK_COLORS.MEDIUM
  const years = hndl?.years_until_threat
  const breachYear = hndl?.estimated_breach_year
  const score = hndl?.hndl_risk_score || 0

  // Bar fill: inverse of score for SAFE=full-green, CRITICAL=full-red
  const barFill = level === 'SAFE' ? 100 : Math.min(score, 100)

  if (compact) {
    return (
      <div className={`flex items-center gap-2 px-2 py-1 rounded ${colors.bg} border ${colors.border}`}>
        <span className={`text-xs font-bold ${colors.text}`}>{level}</span>
        {breachYear && level !== 'SAFE' && (
          <span className="text-xs text-slate-400">~{breachYear}</span>
        )}
      </div>
    )
  }

  return (
    <div className={`rounded-lg p-3 border ${colors.bg} ${colors.border}`}>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-sm font-bold ${colors.text}`}>
          {level === 'SAFE' ? '✓ HNDL SAFE' : `⚠ HNDL ${level}`}
        </span>
        {breachYear && level !== 'SAFE' && (
          <span className={`text-sm font-mono font-bold ${colors.text}`}>
            ~{breachYear}
          </span>
        )}
      </div>

      {level !== 'SAFE' && years !== undefined && years !== null && (
        <div className="text-xs text-slate-300 mb-2">
          <span className="font-semibold">{years} years</span> until CRQC quantum threat
        </div>
      )}

      {hndl?.risk_description && !compact && (
        <div className="text-xs text-slate-400 mb-2 line-clamp-2">
          {hndl.risk_description}
        </div>
      )}

      {/* Urgency bar */}
      <div className="w-full bg-slate-700/50 rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all ${colors.bar}`}
          style={{ width: `${barFill}%` }}
        />
      </div>

      {hndl?.urgency && (
        <div className={`mt-1.5 text-xs font-medium ${colors.text}`}>
          {hndl.urgency}
        </div>
      )}
    </div>
  )
}
