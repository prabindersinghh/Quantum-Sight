import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { CheckCircle, XCircle, RefreshCw, AlertTriangle } from 'lucide-react'
import api from '../api/client'
import PQCBadge from '../components/PQCBadge'
import RiskMatrix from '../components/RiskMatrix'

export default function PosturePQC() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.getPQCPosture()
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

  const total = data?.total || 0
  const elite = data?.elite_pqc || 0
  const standard = data?.standard || 0
  const legacy = data?.legacy || 0
  const critical = data?.critical || 0

  const barData = [
    { name: 'Elite-PQC', value: elite, fill: '#16A34A' },
    { name: 'Standard', value: standard, fill: '#2563EB' },
    { name: 'Legacy', value: legacy, fill: '#D97706' },
    { name: 'Critical', value: critical, fill: '#DC2626' },
  ]

  const pieData = [
    { name: 'Elite-PQC Ready', value: elite },
    { name: 'Standard', value: standard },
    { name: 'Legacy', value: legacy },
    { name: 'Critical', value: critical },
  ]
  const PIE_COLORS = ['#16A34A', '#2563EB', '#D97706', '#DC2626']

  const recommendations = data?.recommendations || [
    'Migrate critical assets to TLS 1.3 + ML-KEM-768 immediately',
    'Replace deprecated TLS 1.1 endpoints (RFC 8996)',
    'Upgrade RSA-2048 keys to 3072-bit minimum',
    'Implement HSTS headers on all exposed assets',
    'Deploy hybrid classical+PQC mode using OQS-Provider',
  ]

  return (
    <div className="space-y-5">
      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-xl p-4 bg-green-950/30 border border-green-800/30">
          <div className="text-slate-400 text-xs mb-1">Elite-PQC Ready</div>
          <div className="text-2xl font-bold text-green-400">{total ? Math.round(elite / total * 100) : 0}%</div>
          <div className="text-green-600 text-xs mt-1">{elite} assets</div>
        </div>
        <div className="rounded-xl p-4 bg-blue-950/30 border border-blue-800/30">
          <div className="text-slate-400 text-xs mb-1">Standard Tier</div>
          <div className="text-2xl font-bold text-blue-400">{total ? Math.round(standard / total * 100) : 0}%</div>
          <div className="text-blue-600 text-xs mt-1">{standard} assets</div>
        </div>
        <div className="rounded-xl p-4 bg-amber-950/30 border border-amber-800/30">
          <div className="text-slate-400 text-xs mb-1">Legacy Tier</div>
          <div className="text-2xl font-bold text-amber-400">{legacy}</div>
          <div className="text-amber-600 text-xs mt-1">Deprecated protocols</div>
        </div>
        <div className="rounded-xl p-4 bg-red-950/30 border border-red-800/30">
          <div className="text-slate-400 text-xs mb-1">Critical Assets</div>
          <div className="text-2xl font-bold text-red-400">{critical}</div>
          <div className="text-red-600 text-xs mt-1">Immediate action</div>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Assets by Classification Grade</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={barData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
              <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9', fontSize: 12 }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Application Status</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="45%" innerRadius={45} outerRadius={75} paddingAngle={3} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9', fontSize: 12 }} />
              <Legend iconType="circle" iconSize={7} wrapperStyle={{ fontSize: 10, color: '#94A3B8' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Matrix + Recommendations */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <RiskMatrix />
        </div>
        <div className="bg-slate-800/60 border border-amber-700/20 rounded-xl p-4">
          <h3 className="text-amber-400 text-sm font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle size={14} /> Improvement Recommendations
          </h3>
          <ul className="space-y-2">
            {recommendations.map((rec: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="text-amber-400 mt-0.5 shrink-0">→</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Assets Table */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/50">
          <h3 className="text-slate-300 text-sm font-semibold">PQC Asset Assessment</h3>
          <button onClick={load} className="p-1.5 text-slate-400 hover:text-slate-200">
            <RefreshCw size={13} />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700/50">
                {['Asset / IP', 'Type', 'PQC Status', 'PQC Ready', 'TLS Version', 'Vulnerability', 'Recommendation'].map(h => (
                  <th key={h} className="text-slate-500 font-medium text-left px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(data?.assets || []).map((a: any, i: number) => (
                <tr key={i} className="border-b border-slate-700/20 table-row-hover">
                  <td className="px-4 py-3">
                    <div className="text-slate-200 font-medium">{a.hostname}</div>
                    <div className="text-slate-500 font-mono text-xs">{a.ip_address}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{a.asset_type}</td>
                  <td className="px-4 py-3"><PQCBadge status={a.pqc_status} size="sm" /></td>
                  <td className="px-4 py-3">
                    {a.pqc_ready
                      ? <CheckCircle size={16} className="text-green-400" />
                      : <XCircle size={16} className="text-red-400" />}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-mono ${a.tls_version?.includes('1.3') ? 'text-green-400' : a.tls_version?.includes('1.2') ? 'text-blue-400' : 'text-red-400'}`}>
                      {a.tls_version || '—'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400 max-w-[180px] truncate">{a.vulnerability_reason || '—'}</td>
                  <td className="px-4 py-3 text-slate-400 max-w-[160px] truncate">
                    {a.recommended_replacement?.algorithm
                      ? <span className="text-amber-400 font-medium">→ {a.recommended_replacement.algorithm}</span>
                      : '—'
                    }
                  </td>
                </tr>
              ))}
              {!(data?.assets?.length) && (
                <tr><td colSpan={7} className="text-center py-8 text-slate-500">No PQC assessment data available.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
