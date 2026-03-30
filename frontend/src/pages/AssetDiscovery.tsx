import { useEffect, useState } from 'react'
import { Globe, Shield, Network, Package, RefreshCw } from 'lucide-react'
import api from '../api/client'
import NetworkGraph from '../components/NetworkGraph'

type Tab = 'domains' | 'ssl' | 'ips' | 'software'
type Filter = 'All' | 'Confirmed' | 'New' | 'False Positive'

export default function AssetDiscovery() {
  const [tab, setTab] = useState<Tab>('domains')
  const [filter, setFilter] = useState<Filter>('All')
  const [domains, setDomains] = useState<any[]>([])
  const [ssl, setSSL] = useState<any[]>([])
  const [ips, setIPs] = useState<any[]>([])
  const [software, setSoftware] = useState<any[]>([])
  const [graph, setGraph] = useState<{ nodes: any[], links: any[] }>({ nodes: [], links: [] })
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [d, s, i, sw, g] = await Promise.all([
        api.getDiscoveryDomains(),
        api.getDiscoverySSL(),
        api.getDiscoveryIPs(),
        api.getDiscoverySoftware(),
        api.getNetworkGraph(),
      ])
      setDomains(d.data.data)
      setSSL(s.data.data)
      setIPs(i.data.data)
      setSoftware(sw.data.data)
      setGraph(g.data.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const applyFilter = (items: any[]) =>
    filter === 'All' ? items : items.filter(i => i.status === filter)

  const TABS = [
    { id: 'domains' as Tab, label: 'Domains', icon: Globe, data: domains },
    { id: 'ssl' as Tab, label: 'SSL Certificates', icon: Shield, data: ssl },
    { id: 'ips' as Tab, label: 'IP Address / Subnets', icon: Network, data: ips },
    { id: 'software' as Tab, label: 'Software', icon: Package, data: software },
  ]

  return (
    <div className="space-y-5">
      {/* Tab header */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="flex items-center border-b border-slate-700/50 px-4">
          {TABS.map(({ id, label, icon: Icon, data }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-2 px-4 py-3.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
                ${tab === id
                  ? 'border-pnb-red text-red-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'}`}
            >
              <Icon size={14} />
              {label}
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${tab === id ? 'bg-red-900/40 text-red-400' : 'bg-slate-700 text-slate-500'}`}>
                {data.length}
              </span>
            </button>
          ))}
          <div className="ml-auto">
            <button onClick={load} className="flex items-center gap-1.5 px-3 py-2 text-slate-400 hover:text-slate-200 text-xs">
              <RefreshCw size={12} />
            </button>
          </div>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/30">
          {(['All', 'New', 'Confirmed', 'False Positive'] as Filter[]).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                ${filter === f
                  ? 'bg-pnb-red text-white'
                  : 'bg-slate-700/50 text-slate-400 hover:text-slate-200'}`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="overflow-x-auto">
          {tab === 'domains' && (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/40">
                  {['Detection Date', 'Domain Name', 'IP Address', 'Asset Type', 'Owner', 'Status'].map(h => (
                    <th key={h} className="text-slate-500 text-left px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-slate-700/20">
                    {[...Array(6)].map((_, j) => <td key={j} className="px-4 py-3"><div className="h-3 shimmer rounded w-24" /></td>)}
                  </tr>
                )) : applyFilter(domains).map((d, i) => (
                  <tr key={i} className="border-b border-slate-700/20 table-row-hover">
                    <td className="px-4 py-3 text-slate-500">{d.detection_date}</td>
                    <td className="px-4 py-3 text-slate-200 font-medium font-mono">{d.domain_name}</td>
                    <td className="px-4 py-3 text-slate-400 font-mono">{d.ip_address || '—'}</td>
                    <td className="px-4 py-3 text-slate-400">{d.type}</td>
                    <td className="px-4 py-3 text-slate-400 max-w-[150px] truncate">{d.owner}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full bg-green-900/30 text-green-400 text-xs border border-green-700/30">{d.status}</span>
                    </td>
                  </tr>
                ))}
                {!loading && applyFilter(domains).length === 0 && (
                  <tr><td colSpan={6} className="text-center py-8 text-slate-500">No domains found.</td></tr>
                )}
              </tbody>
            </table>
          )}

          {tab === 'ssl' && (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/40">
                  {['Detection Date', 'SHA256 Fingerprint', 'Valid From', 'Valid Until', 'Common Name', 'Issuer/CA', 'TLS', 'Key Size', 'Status'].map(h => (
                    <th key={h} className="text-slate-500 text-left px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-slate-700/20">
                    {[...Array(9)].map((_, j) => <td key={j} className="px-4 py-3"><div className="h-3 shimmer rounded w-20" /></td>)}
                  </tr>
                )) : applyFilter(ssl).map((s, i) => (
                  <tr key={i} className={`border-b border-slate-700/20 table-row-hover ${s.is_expired ? 'bg-red-950/10' : ''}`}>
                    <td className="px-4 py-3 text-slate-500">{s.detection_date}</td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-xs max-w-[150px] truncate">{s.sha256_fingerprint}</td>
                    <td className="px-4 py-3 text-slate-400">{s.valid_from}</td>
                    <td className="px-4 py-3">
                      <span className={s.is_expired ? 'text-red-400 font-bold' : s.days_until_expiry < 30 ? 'text-amber-400' : 'text-slate-400'}>
                        {s.is_expired ? 'EXPIRED' : s.valid_until}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-200 font-medium">{s.common_name}</td>
                    <td className="px-4 py-3 text-slate-400">{s.issuer}</td>
                    <td className="px-4 py-3">
                      <span className={`font-mono ${s.tls_version?.includes('1.3') ? 'text-green-400' : s.tls_version?.includes('1.2') ? 'text-blue-400' : 'text-red-400'}`}>
                        {s.tls_version}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{s.key_size}b</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full bg-green-900/30 text-green-400 text-xs border border-green-700/30">{s.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {tab === 'ips' && (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/40">
                  {['Detection Date', 'IP Address', 'Ports', 'Subnet', 'ASN', 'Netname', 'Location', 'Company', 'Status'].map(h => (
                    <th key={h} className="text-slate-500 text-left px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-slate-700/20">
                    {[...Array(9)].map((_, j) => <td key={j} className="px-4 py-3"><div className="h-3 shimmer rounded w-20" /></td>)}
                  </tr>
                )) : applyFilter(ips).map((ip, i) => (
                  <tr key={i} className="border-b border-slate-700/20 table-row-hover">
                    <td className="px-4 py-3 text-slate-500">{ip.detection_date}</td>
                    <td className="px-4 py-3 text-slate-200 font-mono font-medium">{ip.ip_address}</td>
                    <td className="px-4 py-3 text-slate-400">{(ip.ports || []).join(', ')}</td>
                    <td className="px-4 py-3 text-slate-400 font-mono">{ip.subnet}</td>
                    <td className="px-4 py-3 text-slate-400">{ip.asn}</td>
                    <td className="px-4 py-3 text-slate-400">{ip.netname}</td>
                    <td className="px-4 py-3 text-slate-400">{ip.location}</td>
                    <td className="px-4 py-3 text-slate-400 max-w-[120px] truncate">{ip.company}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full bg-green-900/30 text-green-400 text-xs border border-green-700/30">{ip.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {tab === 'software' && (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/40">
                  {['Detection Date', 'Product', 'Version', 'Type', 'Port', 'Host', 'Company', 'Status'].map(h => (
                    <th key={h} className="text-slate-500 text-left px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-slate-700/20">
                    {[...Array(8)].map((_, j) => <td key={j} className="px-4 py-3"><div className="h-3 shimmer rounded w-24" /></td>)}
                  </tr>
                )) : applyFilter(software).map((s, i) => (
                  <tr key={i} className="border-b border-slate-700/20 table-row-hover">
                    <td className="px-4 py-3 text-slate-500">{s.detection_date}</td>
                    <td className="px-4 py-3 text-slate-200 font-medium">{s.product}</td>
                    <td className="px-4 py-3 text-slate-400 font-mono">{s.version}</td>
                    <td className="px-4 py-3 text-slate-400">{s.type}</td>
                    <td className="px-4 py-3 text-slate-400">{s.port}</td>
                    <td className="px-4 py-3 text-slate-300 font-mono">{s.host}</td>
                    <td className="px-4 py-3 text-slate-400 max-w-[120px] truncate">{s.company}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full bg-green-900/30 text-green-400 text-xs border border-green-700/30">{s.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Network Graph */}
      {graph.nodes.length > 0 && (
        <NetworkGraph nodes={graph.nodes} links={graph.links} height={440} />
      )}
    </div>
  )
}
