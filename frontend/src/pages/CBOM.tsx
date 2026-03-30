import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { Download, RefreshCw } from 'lucide-react'
import api from '../api/client'
import type { CBOMEntry } from '../types'

const WEAK_CIPHERS = ['RC4', 'DES', 'SSLv3', 'NULL', 'EXPORT', 'MD5', 'TLS_RSA_WITH_DES']

function isWeak(cipher: string) {
  return WEAK_CIPHERS.some(w => (cipher || '').toUpperCase().includes(w))
}

function extractCA(issuer: string) {
  if (!issuer) return 'Unknown'
  const cas = [
    ['digicert', 'DigiCert'],
    ["let's encrypt", "Let's Encrypt"],
    ['comodo', 'COMODO'],
    ['sectigo', 'Sectigo'],
    ['globalsign', 'GlobalSign'],
    ['entrust', 'Entrust'],
    ['symantec', 'Symantec'],
    ['thawte', 'Thawte'],
    ['geotrust', 'GeoTrust'],
  ]
  const lower = issuer.toLowerCase()
  for (const [key, name] of cas) {
    if (lower.includes(key)) return name
  }
  return 'Other'
}

export default function CBOM() {
  const [entries, setEntries] = useState<CBOMEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [exportFormat, setExportFormat] = useState('json')

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.getCBOM()
      setEntries(res.data.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const exportCBOM = async () => {
    try {
      const res = await api.exportCBOM(exportFormat)
      const ext = exportFormat === 'json' ? 'json' : exportFormat === 'csv' ? 'csv' : exportFormat === 'xml' ? 'xml' : 'pdf'
      const blob = new Blob([res.data], { type: res.headers['content-type'] || 'application/octet-stream' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `quantumsight_cbom.${ext}`; a.click()
    } catch (e) {
      console.error(e)
    }
  }

  // Stats
  const total = entries.length
  const active = entries.filter(e => e.key_state === 'active').length
  const expired = entries.filter(e => e.key_state === 'expired' || e.is_expired).length
  const weakCount = entries.filter(e => isWeak(e.algo_name || '')).length

  // Key length distribution
  const keySizes: Record<string, number> = {}
  entries.forEach(e => {
    if (e.key_size) {
      const k = String(e.key_size)
      keySizes[k] = (keySizes[k] || 0) + 1
    }
  })
  const keySizeData = Object.entries(keySizes)
    .sort(([a], [b]) => Number(b) - Number(a))
    .map(([name, value]) => ({ name, value }))

  // Cipher usage
  const cipherCounts: Record<string, number> = {}
  entries.forEach(e => {
    const c = e.algo_name || e.protocol_cipher_suites || 'Unknown'
    const short = c.length > 35 ? c.slice(0, 35) + '…' : c
    cipherCounts[short] = (cipherCounts[short] || 0) + 1
  })
  const cipherData = Object.entries(cipherCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }))

  // Protocol distribution
  const protoCount: Record<string, number> = {}
  entries.forEach(e => {
    const p = e.protocol_version || 'Unknown'
    protoCount[p] = (protoCount[p] || 0) + 1
  })
  const protoData = Object.entries(protoCount).map(([name, value]) => ({ name, value }))
  const PROTO_COLORS = ['#16A34A', '#2563EB', '#D97706', '#DC2626', '#7C3AED']

  // CA distribution
  const caCount: Record<string, number> = {}
  entries.forEach(e => {
    const ca = extractCA(e.cert_issuer_name || '')
    caCount[ca] = (caCount[ca] || 0) + 1
  })
  const caData = Object.entries(caCount).sort(([, a], [, b]) => b - a).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-5">
      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Applications', value: total, color: 'text-slate-100' },
          { label: 'Active Certificates', value: active, color: 'text-green-400' },
          { label: 'Weak Cryptography', value: weakCount, color: 'text-red-400', highlight: true },
          { label: 'Cert Issues (Expired)', value: expired, color: 'text-amber-400' },
        ].map(({ label, value, color, highlight }) => (
          <div key={label} className={`rounded-xl p-4 border ${highlight ? 'bg-red-950/30 border-red-800/30' : 'bg-slate-800/60 border-slate-700/50'}`}>
            <div className="text-slate-400 text-xs mb-1">{label}</div>
            <div className={`text-2xl font-bold ${color}`}>{value}</div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Key Length Distribution */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Key Length Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={keySizeData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
              <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9', fontSize: 12 }} />
              <Bar dataKey="value" fill="#2563EB" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Encryption Protocols */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Encryption Protocols</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={protoData} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                paddingAngle={3} dataKey="value">
                {protoData.map((_, i) => (
                  <Cell key={i} fill={PROTO_COLORS[i % PROTO_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9', fontSize: 12 }} />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11, color: '#94A3B8' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cipher usage + CA */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Cipher Suite Usage</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={cipherData} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 0 }}>
              <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94A3B8', fontSize: 9 }} axisLine={false} tickLine={false} width={180} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9', fontSize: 12 }} />
              <Bar dataKey="value" fill="#F59E0B" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Top Certificate Authorities</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={caData} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 0 }}>
              <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94A3B8', fontSize: 11 }} axisLine={false} tickLine={false} width={100} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9', fontSize: 12 }} />
              <Bar dataKey="value" fill="#7C3AED" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CBOM Table */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/50">
          <h3 className="text-slate-300 text-sm font-semibold">CBOM — CERT-IN Annexure-A</h3>
          <div className="flex items-center gap-2">
            <select
              value={exportFormat}
              onChange={e => setExportFormat(e.target.value)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-2 py-1.5 text-slate-300 text-xs focus:outline-none"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="xml">XML</option>
              <option value="pdf">PDF</option>
            </select>
            <button
              onClick={exportCBOM}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-pnb-red text-white rounded-lg text-xs font-medium hover:bg-red-800 transition-colors"
            >
              <Download size={12} /> Export
            </button>
            <button onClick={load} className="p-1.5 text-slate-400 hover:text-slate-200">
              <RefreshCw size={13} />
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700/50">
                {['Hostname', 'Cipher Suite', 'Primitive', 'Key Size (bits)', 'TLS Version', 'Cert Authority', 'Sig Algorithm', 'Cert Status', 'SHA256'].map(h => (
                  <th key={h} className="text-slate-500 font-medium text-left px-4 py-3 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? [...Array(6)].map((_, i) => (
                <tr key={i} className="border-b border-slate-700/20">
                  {[...Array(9)].map((_, j) => <td key={j} className="px-4 py-3"><div className="h-3 shimmer rounded w-20" /></td>)}
                </tr>
              )) : entries.length === 0 ? (
                <tr><td colSpan={9} className="text-center py-8 text-slate-500">No CBOM entries. Run a scan to populate.</td></tr>
              ) : entries.map((e, i) => {
                const weak = isWeak(e.algo_name || e.protocol_cipher_suites || '')
                const ca = extractCA(e.cert_issuer_name || '')
                return (
                  <tr
                    key={i}
                    className={`border-b border-slate-700/20 table-row-hover ${weak ? 'bg-red-950/20' : ''}`}
                  >
                    <td className="px-4 py-3">
                      <span className="text-slate-200 font-medium">{e.cert_name || e.hostname}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-mono ${weak ? 'text-red-400 font-bold' : 'text-slate-300'}`}>
                        {(e.algo_name || e.protocol_cipher_suites || '').slice(0, 32)}
                        {weak && ' ⚠'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{e.algo_primitive || '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`font-mono ${(e.key_size || 0) < 2048 ? 'text-red-400' : (e.key_size || 0) >= 4096 ? 'text-green-400' : 'text-slate-300'}`}>
                        {e.key_size || '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-mono ${e.protocol_version?.includes('1.3') ? 'text-green-400' : e.protocol_version?.includes('1.2') ? 'text-blue-400' : 'text-red-400'}`}>
                        {e.protocol_version || '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{ca}</td>
                    <td className="px-4 py-3 text-slate-400 font-mono">{e.cert_signature_algorithm_ref || '—'}</td>
                    <td className="px-4 py-3">
                      {e.is_expired ? (
                        <span className="text-red-400 font-bold">EXPIRED</span>
                      ) : e.key_state === 'active' ? (
                        <span className="text-green-400">Active</span>
                      ) : (
                        <span className="text-slate-400">{e.key_state || '—'}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-600 font-mono text-xs max-w-[100px] truncate">
                      {e.cert_sha256_fingerprint?.slice(0, 16)}…
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
