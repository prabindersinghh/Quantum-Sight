import { useEffect, useState } from 'react'
import { FileText, Download, Award, Calendar, Mail, RefreshCw, CheckCircle } from 'lucide-react'
import api from '../api/client'
import type { Asset } from '../types'
import PQCBadge from '../components/PQCBadge'

function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

export default function Reporting() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loadingAssets, setLoadingAssets] = useState(true)
  const [certLoading, setCertLoading] = useState<Record<string, boolean>>({})
  const [reportLoading, setReportLoading] = useState(false)
  const [format, setFormat] = useState('pdf')
  const [schedFreq, setSchedFreq] = useState('weekly')
  const [schedEmail, setSchedEmail] = useState('')
  const [schedType, setSchedType] = useState('Executive Summary')
  const [scheduled, setScheduled] = useState(false)
  const [toast, setToast] = useState('')

  useEffect(() => {
    api.getAssets().then(res => {
      setAssets(res.data.data)
      setLoadingAssets(false)
    }).catch(() => setLoadingAssets(false))
  }, [])

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(''), 3000)
  }

  const downloadReport = async () => {
    setReportLoading(true)
    try {
      const res = await api.exportReport('executive', format)
      const ext = format
      saveBlob(new Blob([res.data]), `QuantumSight_Report.${ext}`)
      showToast(`Report downloaded as ${ext.toUpperCase()}`)
    } catch (e) {
      console.error(e)
      showToast('Failed to generate report')
    } finally {
      setReportLoading(false)
    }
  }

  const downloadCertificate = async (asset: Asset) => {
    setCertLoading(prev => ({ ...prev, [asset.id]: true }))
    try {
      const res = await api.downloadCertificate(asset.id)
      const hostname = asset.hostname.replace(/\./g, '_')
      saveBlob(new Blob([res.data], { type: 'application/pdf' }), `PQC_Certificate_${hostname}.pdf`)
      showToast(`Certificate downloaded for ${asset.hostname}`)
    } catch (e) {
      console.error(e)
      showToast('Failed to download certificate')
    } finally {
      setCertLoading(prev => ({ ...prev, [asset.id]: false }))
    }
  }

  const scheduleReport = () => {
    setScheduled(true)
    showToast(`${schedFreq} ${schedType} report scheduled${schedEmail ? ` → ${schedEmail}` : ''}`)
    setTimeout(() => setScheduled(false), 4000)
  }

  // Elite-PQC assets eligible for certificates
  const eliteAssets = assets.filter(a =>
    a.pqc_ready || a.pqc_status === 'Elite-PQC' || a.tier === 'Elite-PQC'
  )

  return (
    <div className="space-y-5">
      {/* Toast */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-green-900 border border-green-700 rounded-xl text-green-200 text-sm shadow-xl fade-up">
          <CheckCircle size={14} className="text-green-400" />
          {toast}
        </div>
      )}

      {/* Three report type cards */}
      <div className="grid grid-cols-3 gap-4">
        {/* Executive Report */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-blue-900/40 border border-blue-700/30 flex items-center justify-center">
              <FileText size={16} className="text-blue-400" />
            </div>
            <div>
              <div className="text-slate-200 font-semibold text-sm">Executive Report</div>
              <div className="text-slate-500 text-xs">Full PQC posture summary</div>
            </div>
          </div>
          <p className="text-slate-400 text-xs mb-4">
            Comprehensive executive summary including enterprise score, HNDL risk assessment,
            CBOM inventory, and NIST compliance status for all scanned assets.
          </p>
          <div className="space-y-3">
            <div>
              <label className="text-slate-400 text-xs block mb-1.5">Export Format</label>
              <select
                value={format}
                onChange={e => setFormat(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
              >
                <option value="pdf">PDF — Executive Report</option>
                <option value="json">JSON — Machine Readable</option>
                <option value="csv">CSV — CBOM Spreadsheet</option>
                <option value="xml">XML — CERT-IN Format</option>
              </select>
            </div>
            <button
              onClick={downloadReport}
              disabled={reportLoading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-500 transition-colors disabled:opacity-50"
            >
              {reportLoading ? (
                <><RefreshCw size={13} className="animate-spin" /> Generating...</>
              ) : (
                <><Download size={13} /> Download {format.toUpperCase()}</>
              )}
            </button>
          </div>
        </div>

        {/* Scheduled Reporting */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-amber-900/40 border border-amber-700/30 flex items-center justify-center">
              <Calendar size={16} className="text-amber-400" />
            </div>
            <div>
              <div className="text-slate-200 font-semibold text-sm">Scheduled Reporting</div>
              <div className="text-slate-500 text-xs">Automated delivery</div>
            </div>
          </div>
          <div className="space-y-3">
            <div>
              <label className="text-slate-400 text-xs block mb-1.5">Report Type</label>
              <select
                value={schedType}
                onChange={e => setSchedType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 text-xs focus:outline-none focus:border-amber-500"
              >
                <option>Executive Summary</option>
                <option>CBOM Report</option>
                <option>PQC Posture Report</option>
                <option>HNDL Risk Report</option>
                <option>Certificate Expiry Report</option>
              </select>
            </div>
            <div>
              <label className="text-slate-400 text-xs block mb-1.5">Frequency</label>
              <select
                value={schedFreq}
                onChange={e => setSchedFreq(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 text-xs focus:outline-none focus:border-amber-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
              </select>
            </div>
            <div>
              <label className="text-slate-400 text-xs block mb-1.5">Delivery Email</label>
              <input
                type="email"
                value={schedEmail}
                onChange={e => setSchedEmail(e.target.value)}
                placeholder="ciso@pnb.bank.in"
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 text-xs placeholder-slate-600 focus:outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="text-slate-400 text-xs block mb-1.5">Include Sections</label>
              <div className="space-y-1">
                {['CBOM Summary', 'HNDL Risk Timeline', 'PQC Score Breakdown', 'Expiring Certificates', 'AI Recommendations'].map(s => (
                  <label key={s} className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded" />
                    {s}
                  </label>
                ))}
              </div>
            </div>
            <button
              onClick={scheduleReport}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-500 transition-colors"
            >
              {scheduled ? (
                <><CheckCircle size={13} className="text-green-300" /> Scheduled!</>
              ) : (
                <><Mail size={13} /> Schedule Report</>
              )}
            </button>
          </div>
        </div>

        {/* On-Demand */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-green-900/40 border border-green-700/30 flex items-center justify-center">
              <Download size={16} className="text-green-400" />
            </div>
            <div>
              <div className="text-slate-200 font-semibold text-sm">On-Demand Report</div>
              <div className="text-slate-500 text-xs">Instant download</div>
            </div>
          </div>
          <div className="space-y-3">
            <div>
              <label className="text-slate-400 text-xs block mb-2">Report Types to Include</label>
              <div className="space-y-1">
                {[
                  'Executive Summary',
                  'Asset Inventory',
                  'CBOM (Annexure-A)',
                  'PQC Posture Assessment',
                  'HNDL Risk Report',
                  'Cyber Rating Scorecard',
                  'Migration Recommendations',
                ].map(s => (
                  <label key={s} className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded" />
                    {s}
                  </label>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-700/30 rounded p-2">
                <input type="checkbox" defaultChecked />
                Include Charts
              </label>
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-700/30 rounded p-2">
                <input type="checkbox" />
                Password Protect
              </label>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {['pdf', 'json', 'csv', 'xml'].map(f => (
                <button
                  key={f}
                  onClick={() => { setFormat(f); downloadReport() }}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-700 text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-600 transition-colors"
                >
                  <Download size={11} /> {f.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* PQC Certificate Section */}
      <div className="bg-slate-800/60 border border-green-700/20 rounded-xl overflow-hidden">
        <div className="flex items-center gap-3 px-5 py-3 border-b border-slate-700/50 bg-green-950/10">
          <Award size={16} className="text-green-400" />
          <div>
            <h3 className="text-green-400 text-sm font-semibold">PQC-Ready Digital Certificates</h3>
            <p className="text-slate-400 text-xs">
              Issue downloadable PDF certificates for Elite-PQC compliant assets
            </p>
          </div>
        </div>

        {loadingAssets ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading assets...</div>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700/40">
                {['Asset', 'Type', 'TLS Version', 'PQC Status', 'Score', 'Cert Expiry', 'Action'].map(h => (
                  <th key={h} className="text-slate-500 font-medium text-left px-5 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(eliteAssets.length > 0 ? eliteAssets : assets).map(asset => {
                const tier = asset.tier || asset.pqc_status || 'Standard'
                const isElite = tier === 'Elite-PQC'
                return (
                  <tr key={asset.id} className={`border-b border-slate-700/20 table-row-hover ${isElite ? '' : 'opacity-60'}`}>
                    <td className="px-5 py-3">
                      <div className="text-slate-200 font-medium">{asset.hostname}</div>
                      <div className="text-slate-500 font-mono text-xs">{asset.ip_address}</div>
                    </td>
                    <td className="px-5 py-3 text-slate-400">{asset.asset_type}</td>
                    <td className="px-5 py-3">
                      <span className={`font-mono ${asset.tls_version?.includes('1.3') ? 'text-green-400' : 'text-blue-400'}`}>
                        {asset.tls_version || '—'}
                      </span>
                    </td>
                    <td className="px-5 py-3"><PQCBadge status={tier} size="sm" /></td>
                    <td className="px-5 py-3">
                      <span className={`font-mono font-bold ${isElite ? 'text-green-400' : 'text-slate-300'}`}>
                        {asset.total_score || '—'}/1000
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      {asset.is_expired ? (
                        <span className="text-red-400 font-bold">EXPIRED</span>
                      ) : (
                        <span className={asset.days_until_expiry && asset.days_until_expiry < 30 ? 'text-amber-400' : 'text-slate-400'}>
                          {asset.days_until_expiry ? `${asset.days_until_expiry}d` : '—'}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3">
                      <button
                        onClick={() => downloadCertificate(asset)}
                        disabled={certLoading[asset.id]}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                          ${isElite
                            ? 'bg-green-700/30 text-green-400 border border-green-700/30 hover:bg-green-700/50'
                            : 'bg-slate-700/30 text-slate-400 border border-slate-700/30 hover:bg-slate-700/50'
                          } ${certLoading[asset.id] ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        {certLoading[asset.id] ? (
                          <RefreshCw size={11} className="animate-spin" />
                        ) : (
                          <Award size={11} />
                        )}
                        {isElite ? 'Issue Certificate' : 'Download Assessment'}
                      </button>
                    </td>
                  </tr>
                )
              })}
              {assets.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">
                    No assets found. Run a scan to assess cryptographic posture.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {/* Certificate info */}
        <div className="px-5 py-3 border-t border-slate-700/30 bg-slate-900/30">
          <div className="flex gap-6 text-xs text-slate-500">
            <span>Certificate Type: <span className="text-slate-400">Quantum-Safe / PQC-Ready / Fully-Quantum-Safe</span></span>
            <span>Standard: <span className="text-slate-400">NIST FIPS 203/204/205</span></span>
            <span>Format: <span className="text-slate-400">PDF (digitally provenance-stamped)</span></span>
            <span>Authority: <span className="text-slate-400">QuantumSight — PNB Cybersecurity Hackathon 2026</span></span>
          </div>
        </div>
      </div>
    </div>
  )
}
