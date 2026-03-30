import { useEffect, useState, useMemo } from 'react'
import { Search, Filter, Download, RefreshCw, ChevronUp, ChevronDown } from 'lucide-react'
import api from '../api/client'
import type { Asset } from '../types'
import PQCBadge from '../components/PQCBadge'

type SortKey = keyof Asset
type SortDir = 'asc' | 'desc'

export default function AssetInventory() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('All')
  const [tierFilter, setTierFilter] = useState('All')
  const [sortKey, setSortKey] = useState<SortKey>('hostname')
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [selected, setSelected] = useState<Asset | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.getAssets()
      setAssets(res.data.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const types = ['All', ...Array.from(new Set(assets.map(a => a.asset_type).filter(Boolean)))]
  const tiers = ['All', 'Elite-PQC', 'Standard', 'Legacy', 'Critical']

  const filtered = useMemo(() => {
    let list = assets
    if (search) {
      const q = search.toLowerCase()
      list = list.filter(a =>
        a.hostname?.toLowerCase().includes(q) ||
        a.ip_address?.includes(q) ||
        a.owner?.toLowerCase().includes(q) ||
        a.asset_type?.toLowerCase().includes(q)
      )
    }
    if (typeFilter !== 'All') list = list.filter(a => a.asset_type === typeFilter)
    if (tierFilter !== 'All') list = list.filter(a =>
      (a.tier || a.rating?.tier || a.pqc_status) === tierFilter
    )
    list = [...list].sort((a, b) => {
      const av = String(a[sortKey] ?? '')
      const bv = String(b[sortKey] ?? '')
      return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
    })
    return list
  }, [assets, search, typeFilter, tierFilter, sortKey, sortDir])

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const exportCSV = () => {
    const headers = 'Hostname,URL,IPv4,IPv6,Type,Owner,Tier,TLS Version,Key Size,Days Expiry\n'
    const rows = filtered.map(a =>
      `${a.hostname},${a.url || ''},${a.ip_address || ''},${a.ipv6_address || ''},${a.asset_type},${a.owner},${a.tier || ''},${a.tls_version || ''},${a.cert_key_size || ''},${a.days_until_expiry ?? ''}`
    ).join('\n')
    const blob = new Blob([headers + rows], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'assets.csv'; a.click()
  }

  const SortIcon = ({ col }: { col: SortKey }) => (
    sortKey === col
      ? sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
      : <ChevronUp size={11} className="opacity-20" />
  )

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search assets..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-slate-200 text-sm placeholder-slate-600 focus:outline-none focus:border-amber-500"
          />
        </div>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-amber-500"
        >
          {types.map(t => <option key={t}>{t}</option>)}
        </select>
        <select
          value={tierFilter}
          onChange={e => setTierFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-amber-500"
        >
          {tiers.map(t => <option key={t}>{t}</option>)}
        </select>
        <div className="ml-auto flex gap-2">
          <button onClick={load} className="flex items-center gap-1.5 px-3 py-2 bg-slate-700 text-slate-300 rounded-lg text-xs hover:bg-slate-600 transition-colors">
            <RefreshCw size={12} /> Refresh
          </button>
          <button onClick={exportCSV} className="flex items-center gap-1.5 px-3 py-2 bg-slate-700 text-slate-300 rounded-lg text-xs hover:bg-slate-600 transition-colors">
            <Download size={12} /> Export CSV
          </button>
        </div>
      </div>

      <div className="flex gap-4">
        {/* Table */}
        <div className="flex-1 bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/50">
            <span className="text-slate-300 text-sm font-semibold">
              {filtered.length} of {assets.length} assets
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/50">
                  {([
                    ['hostname', 'Asset Name'],
                    ['ip_address', 'IPv4'],
                    ['ipv6_address', 'IPv6'],
                    ['asset_type', 'Type'],
                    ['owner', 'Owner'],
                    ['tier', 'Tier'],
                    ['tls_version', 'TLS'],
                    ['cert_key_size', 'Key Size'],
                    ['days_until_expiry', 'Cert Expiry'],
                  ] as [SortKey, string][]).map(([key, label]) => (
                    <th
                      key={key}
                      className="text-slate-500 font-medium text-left px-4 py-3 cursor-pointer hover:text-slate-300 select-none whitespace-nowrap"
                      onClick={() => toggleSort(key)}
                    >
                      <div className="flex items-center gap-1">{label} <SortIcon col={key} /></div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  [...Array(6)].map((_, i) => (
                    <tr key={i} className="border-b border-slate-700/20">
                      {[...Array(9)].map((_, j) => (
                        <td key={j} className="px-4 py-3"><div className="h-3 shimmer rounded w-20" /></td>
                      ))}
                    </tr>
                  ))
                ) : filtered.length === 0 ? (
                  <tr><td colSpan={9} className="text-center py-10 text-slate-500">No assets match filters.</td></tr>
                ) : filtered.map(asset => {
                  const tier = asset.tier || asset.rating?.tier || asset.pqc_status || 'Standard'
                  return (
                    <tr
                      key={asset.id}
                      className={`border-b border-slate-700/20 table-row-hover ${selected?.id === asset.id ? 'bg-slate-700/40' : ''}`}
                      onClick={() => setSelected(selected?.id === asset.id ? null : asset)}
                    >
                      <td className="px-4 py-3">
                        <div className="text-slate-200 font-medium">{asset.hostname}</div>
                      </td>
                      <td className="px-4 py-3 text-slate-400 font-mono">{asset.ip_address || '—'}</td>
                      <td className="px-4 py-3 text-slate-500 font-mono text-xs">{asset.ipv6_address || '—'}</td>
                      <td className="px-4 py-3 text-slate-400">{asset.asset_type}</td>
                      <td className="px-4 py-3 text-slate-400 max-w-[120px] truncate">{asset.owner}</td>
                      <td className="px-4 py-3"><PQCBadge status={tier} size="sm" /></td>
                      <td className="px-4 py-3">
                        <span className={`font-mono ${asset.tls_version?.includes('1.3') ? 'text-green-400' : asset.tls_version?.includes('1.2') ? 'text-blue-400' : 'text-red-400'}`}>
                          {asset.tls_version || '—'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400">{asset.cert_key_size ? `${asset.cert_key_size}b` : '—'}</td>
                      <td className="px-4 py-3">
                        {asset.is_expired ? (
                          <span className="text-red-400 font-bold">EXPIRED</span>
                        ) : asset.days_until_expiry !== undefined ? (
                          <span className={asset.days_until_expiry < 30 ? 'text-amber-400 font-semibold' : 'text-slate-400'}>
                            {asset.days_until_expiry}d
                          </span>
                        ) : '—'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail Panel */}
        {selected && (
          <div className="w-72 bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 shrink-0 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-slate-200 font-semibold text-sm">Asset Details</h3>
              <button onClick={() => setSelected(null)} className="text-slate-500 hover:text-slate-300 text-xs">✕</button>
            </div>
            <div className="space-y-2 text-xs">
              {[
                ['Hostname', selected.hostname],
                ['IP Address', selected.ip_address],
                ['IPv6', selected.ipv6_address],
                ['Type', selected.asset_type],
                ['Owner', selected.owner],
                ['TLS Version', selected.tls_version],
                ['Cipher Suite', selected.cipher_suite],
                ['Key Size', selected.cert_key_size ? `${selected.cert_key_size} bits` : undefined],
                ['Cert Expiry', selected.is_expired ? 'EXPIRED' : `${selected.days_until_expiry} days`],
                ['PQC Status', selected.pqc_status],
                ['HNDL Risk', selected.hndl_risk_level],
                ['Breach Year', selected.estimated_breach_year ? `~${selected.estimated_breach_year}` : undefined],
                ['Score', selected.total_score !== undefined ? `${selected.total_score}/1000` : undefined],
                ['Last Scan', selected.updated_at?.slice(0, 10)],
              ].filter(([_, v]) => v !== undefined && v !== null && v !== '').map(([label, value]) => (
                <div key={label as string} className="flex justify-between gap-2">
                  <span className="text-slate-500 shrink-0">{label}</span>
                  <span className="text-slate-300 text-right truncate">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
