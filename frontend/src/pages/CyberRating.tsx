import { useEffect, useState } from 'react'
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell
} from 'recharts'
import { RefreshCw, Clock, AlertTriangle, Shield } from 'lucide-react'
import api from '../api/client'
import PQCBadge from '../components/PQCBadge'
import HNDLCountdown from '../components/HNDLCountdown'

function ScoreRing({ score }: { score: number }) {
  const pct = Math.min(score / 1000, 1)
  const r = 70
  const circ = 2 * Math.PI * r
  const dash = pct * circ
  const tier = score >= 850 ? 'Elite-PQC' : score >= 700 ? 'Standard' : score >= 400 ? 'Legacy' : 'Critical'
  const color = { 'Elite-PQC': '#16A34A', 'Standard': '#2563EB', 'Legacy': '#D97706', 'Critical': '#DC2626' }[tier]

  return (
    <div className="flex flex-col items-center">
      <svg width={180} height={180} className="drop-shadow-xl">
        <circle cx={90} cy={90} r={r} fill="none" stroke="#1E293B" strokeWidth={14} />
        <circle
          cx={90} cy={90} r={r}
          fill="none"
          stroke={color}
          strokeWidth={14}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 90 90)"
          style={{ transition: 'stroke-dasharray 1s ease-out' }}
        />
        <text x={90} y={84} textAnchor="middle" fill="white" fontSize={32} fontWeight="bold" fontFamily="monospace">
          {score}
        </text>
        <text x={90} y={105} textAnchor="middle" fill="#64748B" fontSize={12}>
          / 1000
        </text>
        <text x={90} y={124} textAnchor="middle" fill={color} fontSize={13} fontWeight="600">
          {tier}
        </text>
      </svg>
    </div>
  )
}

const RISK_BAR_COLORS: Record<string, string> = {
  'SAFE': '#16A34A',
  'LOW': '#2563EB',
  'MEDIUM': '#D97706',
  'HIGH': '#EA580C',
  'CRITICAL': '#DC2626',
}

export default function CyberRating() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [selectedAsset, setSelectedAsset] = useState<any>(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.getCyberRating()
      setData(res.data.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => <div key={i} className="h-32 shimmer rounded-xl" />)}
    </div>
  )

  const enterprise = data?.enterprise || {}
  const assets: any[] = data?.assets || []
  const tierCriteria = data?.tier_criteria || []

  // Score breakdown radar for selected asset
  const breakdownData = selectedAsset?.breakdown
    ? Object.entries(selectedAsset.breakdown).map(([key, v]: [string, any]) => ({
        subject: key.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
        score: v.score,
        max: v.max,
        fullMark: v.max,
      }))
    : []

  return (
    <div className="space-y-5">
      {/* Enterprise Score */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1 bg-slate-800/60 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center justify-center">
          <div className="text-slate-400 text-xs font-medium mb-3 text-center">
            Consolidated Enterprise PQC Cyber Rating
          </div>
          <ScoreRing score={enterprise.total_score || 0} />
          <div className="mt-3 text-center">
            <div className="text-slate-400 text-xs">{enterprise.asset_count || 0} assets assessed</div>
            <div className="text-slate-500 text-xs mt-1">{enterprise.tier_description}</div>
          </div>
        </div>

        <div className="col-span-2 space-y-3">
          {/* Tier criteria table */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-700/50">
              <h3 className="text-slate-300 text-sm font-semibold">PQC Tier Compliance Criteria</h3>
            </div>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/40">
                  {['Tier', 'Score Range', 'TLS Version', 'Action Required'].map(h => (
                    <th key={h} className="text-slate-500 font-medium text-left px-4 py-2.5">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tierCriteria.map((t: any, i: number) => (
                  <tr key={i} className="border-b border-slate-700/20">
                    <td className="px-4 py-2.5"><PQCBadge status={t.tier} size="sm" /></td>
                    <td className="px-4 py-2.5 text-slate-400 font-mono">{t.range}</td>
                    <td className="px-4 py-2.5 text-slate-400">{t.tls}</td>
                    <td className="px-4 py-2.5 text-slate-400">{t.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Enterprise distribution */}
          <div className="grid grid-cols-4 gap-2">
            {[
              { label: 'Elite-PQC', count: enterprise.tier_distribution?.['Elite-PQC'] || 0, color: 'text-green-400 bg-green-950/30 border-green-800/30' },
              { label: 'Standard', count: enterprise.tier_distribution?.['Standard'] || 0, color: 'text-blue-400 bg-blue-950/30 border-blue-800/30' },
              { label: 'Legacy', count: enterprise.tier_distribution?.['Legacy'] || 0, color: 'text-amber-400 bg-amber-950/30 border-amber-800/30' },
              { label: 'Critical', count: enterprise.tier_distribution?.['Critical'] || 0, color: 'text-red-400 bg-red-950/30 border-red-800/30' },
            ].map(({ label, count, color }) => (
              <div key={label} className={`rounded-xl p-3 border ${color} text-center`}>
                <div className="text-xl font-bold">{count}</div>
                <div className="text-xs opacity-70 mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* HNDL Risk Timeline — THE SIGNATURE FEATURE */}
      <div className="bg-slate-800/60 border border-red-900/20 rounded-xl overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-3 border-b border-slate-700/50 bg-red-950/10">
          <Clock size={14} className="text-red-400" />
          <h3 className="text-red-300 text-sm font-semibold">HNDL Risk Timeline — Harvest Now, Decrypt Later</h3>
          <span className="text-slate-500 text-xs ml-auto">
            Intercepted encrypted traffic becomes decryptable when CRQC arrives (est. 2030–2035)
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700/50">
                {['Asset', 'Type', 'Score', 'Tier', 'HNDL Risk', 'Years Remaining', 'Breach Year', 'Urgency'].map(h => (
                  <th key={h} className="text-slate-500 font-medium text-left px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {assets.map((asset: any, i: number) => {
                const riskLevel = asset.hndl_risk_level || 'MEDIUM'
                const years = asset.years_until_threat
                const breachYear = asset.estimated_breach_year
                const barFill = riskLevel === 'SAFE' ? 5 : Math.min(asset.hndl_risk_score || 50, 100)
                const barColor = RISK_BAR_COLORS[riskLevel] || '#D97706'

                return (
                  <tr
                    key={i}
                    className={`border-b border-slate-700/20 table-row-hover cursor-pointer
                      ${selectedAsset?.asset_id === asset.asset_id ? 'bg-slate-700/30' : ''}`}
                    onClick={() => setSelectedAsset(selectedAsset?.asset_id === asset.asset_id ? null : asset)}
                  >
                    <td className="px-4 py-3">
                      <div className="text-slate-200 font-medium">{asset.hostname}</div>
                      <div className="text-slate-500 font-mono text-xs">{asset.ip_address}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{asset.asset_type}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-200 font-bold font-mono">{asset.total_score}</span>
                        <div className="w-16 bg-slate-700/50 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full"
                            style={{
                              width: `${(asset.total_score / 1000) * 100}%`,
                              background: { 'Elite-PQC': '#16A34A', 'Standard': '#2563EB', 'Legacy': '#D97706', 'Critical': '#DC2626' }[asset.tier as string] || '#64748B'
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <PQCBadge status={asset.tier} size="sm" />
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-bold text-xs px-2 py-1 rounded-full border
                        ${riskLevel === 'SAFE' ? 'bg-green-900/30 text-green-400 border-green-700/30' :
                          riskLevel === 'CRITICAL' ? 'bg-red-900/30 text-red-400 border-red-700/30 pulse-red' :
                          riskLevel === 'HIGH' ? 'bg-orange-900/30 text-orange-400 border-orange-700/30' :
                          'bg-amber-900/30 text-amber-400 border-amber-700/30'}`}
                      >
                        {riskLevel === 'SAFE' ? '✓ SAFE' : `⚠ ${riskLevel}`}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {riskLevel !== 'SAFE' && years !== undefined ? (
                        <div>
                          <div className="text-slate-200 font-bold">{years} years</div>
                          <div className="w-24 bg-slate-700/50 rounded-full h-1.5 mt-1">
                            <div
                              className="h-1.5 rounded-full transition-all"
                              style={{ width: `${barFill}%`, background: barColor }}
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="text-green-400 font-semibold">Quantum-Safe</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {breachYear && riskLevel !== 'SAFE' ? (
                        <div>
                          <span className={`font-bold font-mono text-sm ${riskLevel === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'}`}>
                            ~{breachYear}
                          </span>
                          <div className="text-slate-500 text-xs mt-0.5">
                            Intercept risk window open
                          </div>
                        </div>
                      ) : '—'}
                    </td>
                    <td className="px-4 py-3 text-slate-400 max-w-[180px]">
                      <span className={`text-xs ${riskLevel === 'CRITICAL' ? 'text-red-400 font-semibold' : 'text-slate-400'}`}>
                        {asset.urgency || '—'}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Score Breakdown for selected asset */}
      {selectedAsset && breakdownData.length > 0 && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-slate-300 text-sm font-semibold">Score Breakdown — {selectedAsset.hostname}</h3>
              <button onClick={() => setSelectedAsset(null)} className="text-slate-500 hover:text-slate-300 text-xs">✕</button>
            </div>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={breakdownData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94A3B8', fontSize: 10 }} />
                <Radar name="Score" dataKey="score" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.2} />
                <Radar name="Max" dataKey="max" stroke="#334155" fill="#334155" fillOpacity={0.1} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-slate-300 text-sm font-semibold mb-3">Dimension Scores</h3>
            <div className="space-y-2">
              {breakdownData.map((d, i) => (
                <div key={i}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">{d.subject}</span>
                    <span className="text-slate-300 font-mono">{d.score}/{d.max}</span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full bg-amber-500"
                      style={{ width: `${(d.score / d.max) * 100}%` }}
                    />
                  </div>
                  <div className="text-slate-500 text-xs mt-0.5">
                    {selectedAsset.breakdown?.[Object.keys(selectedAsset.breakdown)[i]]?.detail}
                  </div>
                </div>
              ))}
            </div>

            {/* HNDL detail */}
            {selectedAsset.hndl_risk_level && (
              <div className="mt-4">
                <HNDLCountdown
                  hndl={{
                    hndl_risk_level: selectedAsset.hndl_risk_level,
                    hndl_risk_score: selectedAsset.hndl_risk_score,
                    years_until_threat: selectedAsset.years_until_threat,
                    estimated_breach_year: selectedAsset.estimated_breach_year,
                    urgency: selectedAsset.urgency,
                    risk_description: selectedAsset.harvest_warning,
                  }}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
