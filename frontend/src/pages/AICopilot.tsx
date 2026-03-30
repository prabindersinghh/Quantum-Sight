import { useEffect, useState } from 'react'
import { Bot, Sparkles, ChevronDown, ChevronRight, Copy, Check, AlertTriangle, Shield, Clock } from 'lucide-react'
import api from '../api/client'
import type { Asset, MigrationPlan } from '../types'
import PQCBadge from '../components/PQCBadge'

function CodeBlock({ lines }: { lines: string[] }) {
  const [copied, setCopied] = useState(false)
  const code = lines.join('\n')

  const copy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="relative mt-2 bg-slate-950 rounded-lg border border-slate-700/50 overflow-hidden">
      <button
        onClick={copy}
        className="absolute right-2 top-2 p-1.5 rounded text-slate-500 hover:text-slate-300 bg-slate-800 border border-slate-700"
      >
        {copied ? <Check size={11} className="text-green-400" /> : <Copy size={11} />}
      </button>
      <pre className="text-xs text-slate-300 p-3 overflow-x-auto">
        {lines.map((line, i) => (
          <div key={i} className={line.startsWith('#') ? 'text-slate-500' : ''}>
            {line}
          </div>
        ))}
      </pre>
    </div>
  )
}

function StepCard({ step, expanded, onToggle }: {
  step: MigrationPlan['migration_steps'][0], expanded: boolean, onToggle: () => void
}) {
  return (
    <div className="border border-slate-700/50 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-4 py-3 bg-slate-800/40 hover:bg-slate-800/60 transition-colors text-left"
      >
        <div className="w-6 h-6 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center shrink-0">
          <span className="text-amber-400 text-xs font-bold">{step.step}</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-slate-200 text-sm font-medium">{step.title}</div>
          <div className="text-slate-500 text-xs mt-0.5 flex gap-3">
            <span><Clock size={10} className="inline mr-1" />{step.estimated_time}</span>
            {step.dependencies && <span>Depends: {step.dependencies}</span>}
          </div>
        </div>
        {expanded ? <ChevronDown size={14} className="text-slate-500 shrink-0" /> : <ChevronRight size={14} className="text-slate-500 shrink-0" />}
      </button>
      {expanded && (
        <div className="px-4 py-3 bg-slate-900/30 space-y-3">
          <p className="text-sm text-slate-300">{step.description}</p>
          {step.commands?.length > 0 && <CodeBlock lines={step.commands} />}
        </div>
      )}
    </div>
  )
}

export default function AICopilot() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [selectedHostname, setSelectedHostname] = useState('')
  const [plan, setPlan] = useState<MigrationPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingAssets, setLoadingAssets] = useState(true)
  const [error, setError] = useState('')
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([0]))
  const [dots, setDots] = useState('')

  useEffect(() => {
    api.getAssets().then(res => {
      setAssets(res.data.data)
      setLoadingAssets(false)
    }).catch(() => setLoadingAssets(false))
  }, [])

  useEffect(() => {
    if (!loading) { setDots(''); return }
    const iv = setInterval(() => setDots(d => d.length >= 3 ? '' : d + '.'), 400)
    return () => clearInterval(iv)
  }, [loading])

  const generate = async () => {
    if (!selectedHostname) return
    setLoading(true)
    setError('')
    setPlan(null)
    try {
      const asset = assets.find(a => a.hostname === selectedHostname)
      const res = await api.generateMigrationPlan(selectedHostname, asset?.id)
      if (res.data.data?.success && res.data.data?.plan) {
        setPlan(res.data.data.plan)
        setExpandedSteps(new Set([0]))
      } else {
        setError('Failed to generate migration plan. Try again.')
      }
    } catch (e: any) {
      setError(e?.message || 'An error occurred.')
    } finally {
      setLoading(false)
    }
  }

  const toggleStep = (i: number) => {
    setExpandedSteps(prev => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  const PRIORITY_STYLES: Record<string, string> = {
    'Immediate': 'bg-red-950/40 border-red-700/30 text-red-300',
    'High': 'bg-orange-950/40 border-orange-700/30 text-orange-300',
    'Medium': 'bg-amber-950/40 border-amber-700/30 text-amber-300',
    'Low': 'bg-green-950/40 border-green-700/30 text-green-300',
  }

  // Non-PQC assets for selection
  const vulnAssets = assets.filter(a =>
    !a.pqc_ready && (a.pqc?.pqc_status !== 'Elite-PQC')
  )

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
          <Bot size={20} className="text-amber-400" />
        </div>
        <div>
          <h2 className="text-slate-100 font-semibold text-lg">AI Migration Copilot</h2>
          <p className="text-slate-400 text-sm">Powered by Gemini 2.5 Flash — Generates per-asset NIST PQC migration roadmaps</p>
        </div>
      </div>

      {/* Asset Selector */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <div className="flex items-end gap-3">
          <div className="flex-1">
            <label className="text-slate-400 text-xs font-medium block mb-2">
              Select Asset for Migration Plan
            </label>
            <select
              value={selectedHostname}
              onChange={e => setSelectedHostname(e.target.value)}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-amber-500"
            >
              <option value="">— Choose a quantum-vulnerable asset —</option>
              {loadingAssets ? (
                <option disabled>Loading assets...</option>
              ) : (vulnAssets.length > 0 ? vulnAssets : assets).map(a => (
                <option key={a.id} value={a.hostname}>
                  {a.hostname} [{a.asset_type}] {a.pqc_status ? `— ${a.pqc_status}` : ''}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={generate}
            disabled={!selectedHostname || loading}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all
              ${!selectedHostname || loading
                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'bg-amber-500 text-slate-900 hover:bg-amber-400 active:scale-95'
              }`}
          >
            {loading ? (
              <>
                <Sparkles size={15} className="animate-spin" />
                Generating{dots}
              </>
            ) : (
              <>
                <Bot size={15} />
                Generate Migration Plan
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-3 flex items-center gap-2 text-red-400 text-sm bg-red-950/20 border border-red-800/30 rounded-lg px-3 py-2">
            <AlertTriangle size={14} /> {error}
          </div>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-slate-800/40 border border-amber-700/20 rounded-xl p-8 text-center">
          <Bot size={40} className="text-amber-400 mx-auto mb-3 animate-pulse" />
          <div className="text-slate-300 font-medium">Analyzing cryptographic posture{dots}</div>
          <div className="text-slate-500 text-sm mt-1">Gemini 2.5 Flash is generating your NIST PQC migration plan</div>
          <div className="flex justify-center gap-2 mt-4">
            {['Assessing HNDL risk', 'Selecting NIST algorithm', 'Building migration steps', 'Adding compliance notes'].map((s, i) => (
              <div key={i} className="text-xs text-slate-500 px-2 py-1 bg-slate-800 rounded-full border border-slate-700">
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Plan Display */}
      {plan && !loading && (
        <div className="space-y-4 fade-up">
          {/* Summary Card */}
          <div className={`rounded-xl border p-4 ${PRIORITY_STYLES[plan.priority] || PRIORITY_STYLES['Medium']}`}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider opacity-60">Executive Summary</span>
                  {!plan.ai_generated && (
                    <span className="text-xs px-2 py-0.5 bg-slate-700 text-slate-400 rounded-full border border-slate-600">
                      Template (Configure Gemini API key for AI)
                    </span>
                  )}
                  {plan.ai_generated && (
                    <span className="text-xs px-2 py-0.5 bg-amber-900/40 text-amber-400 rounded-full border border-amber-700/30 flex items-center gap-1">
                      <Sparkles size={9} /> AI Generated
                    </span>
                  )}
                </div>
                <p className="text-sm leading-relaxed">{plan.summary}</p>
              </div>
              <div className="shrink-0 text-right space-y-1">
                <div className="text-xs opacity-60">Priority</div>
                <div className="text-sm font-bold">{plan.priority}</div>
                <div className="text-xs opacity-60 mt-2">Effort</div>
                <div className="text-sm font-bold">{plan.effort_estimate}</div>
                <div className="text-xs opacity-60 mt-2">Timeline</div>
                <div className="text-sm font-bold">{plan.estimated_timeline}</div>
              </div>
            </div>
          </div>

          {/* Replacement Algorithm */}
          <div className="bg-slate-800/60 border border-green-700/20 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Shield size={14} className="text-green-400" />
              <h3 className="text-green-400 text-sm font-semibold">Recommended NIST PQC Algorithm</h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                ['Algorithm', plan.replacement_algorithm?.name],
                ['FIPS Standard', plan.replacement_algorithm?.fips_standard],
                ['OID', plan.replacement_algorithm?.oid],
                ['Security Level', `NIST Level ${plan.replacement_algorithm?.security_level}`],
              ].map(([label, value]) => (
                <div key={label} className="bg-slate-900/50 rounded-lg p-3">
                  <div className="text-slate-500 text-xs mb-1">{label}</div>
                  <div className="text-green-300 font-mono font-semibold text-sm break-all">{value || '—'}</div>
                </div>
              ))}
            </div>
            {plan.replacement_algorithm?.quantum_security_bits && (
              <div className="mt-2 text-xs text-slate-400">
                Quantum Security: <span className="text-green-400 font-semibold">{plan.replacement_algorithm.quantum_security_bits}</span>
              </div>
            )}
          </div>

          {/* Migration Steps */}
          <div>
            <h3 className="text-slate-300 text-sm font-semibold mb-3">
              Migration Steps ({plan.migration_steps?.length || 0})
            </h3>
            <div className="space-y-2">
              {(plan.migration_steps || []).map((step, i) => (
                <StepCard
                  key={i}
                  step={step}
                  expanded={expandedSteps.has(i)}
                  onToggle={() => toggleStep(i)}
                />
              ))}
            </div>
          </div>

          {/* Libraries + Risks row */}
          <div className="grid grid-cols-2 gap-4">
            {/* Recommended Libraries */}
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-700/50">
                <h3 className="text-slate-300 text-sm font-semibold">Recommended PQC Libraries</h3>
              </div>
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-700/30">
                    {['Library', 'Language', 'Install', 'Maturity'].map(h => (
                      <th key={h} className="text-slate-500 text-left px-3 py-2 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(plan.recommended_libraries || []).map((lib, i) => (
                    <tr key={i} className="border-b border-slate-700/20">
                      <td className="px-3 py-2 text-slate-200 font-semibold">{lib.name}</td>
                      <td className="px-3 py-2 text-slate-400">{lib.language}</td>
                      <td className="px-3 py-2 text-amber-400 font-mono text-xs max-w-[120px] truncate">{lib.install}</td>
                      <td className="px-3 py-2">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          lib.maturity === 'Production-ready' ? 'bg-green-900/30 text-green-400' :
                          lib.maturity === 'Beta' ? 'bg-amber-900/30 text-amber-400' :
                          'bg-slate-700 text-slate-400'
                        }`}>
                          {lib.maturity || 'Unknown'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Risks */}
            <div className="bg-slate-800/60 border border-red-900/20 rounded-xl p-4">
              <h3 className="text-red-400 text-sm font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle size={13} /> Migration Risks
              </h3>
              <ul className="space-y-2">
                {(plan.risks || []).map((risk, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
                    <span className="text-red-400 mt-0.5 shrink-0">•</span>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Additional details */}
          {(plan.hybrid_approach || plan.testing_approach || plan.rollback_plan || plan.compliance_notes) && (
            <div className="grid grid-cols-2 gap-4">
              {plan.hybrid_approach && (
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <h3 className="text-blue-400 text-sm font-semibold mb-2">Hybrid Classical + PQC Approach</h3>
                  <p className="text-slate-300 text-xs leading-relaxed">{plan.hybrid_approach}</p>
                </div>
              )}
              {plan.testing_approach && (
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <h3 className="text-slate-300 text-sm font-semibold mb-2">Testing Approach</h3>
                  <p className="text-slate-400 text-xs leading-relaxed">{plan.testing_approach}</p>
                </div>
              )}
              {plan.rollback_plan && (
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <h3 className="text-slate-300 text-sm font-semibold mb-2">Rollback Plan</h3>
                  <p className="text-slate-400 text-xs leading-relaxed">{plan.rollback_plan}</p>
                </div>
              )}
              {plan.compliance_notes && (
                <div className="bg-slate-800/60 border border-amber-700/20 rounded-xl p-4">
                  <h3 className="text-amber-400 text-sm font-semibold mb-2">CERT-IN / RBI Compliance</h3>
                  <p className="text-slate-300 text-xs leading-relaxed">{plan.compliance_notes}</p>
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="text-slate-500 text-xs text-right">
            Generated by {plan.ai_model} • {plan.generated_at?.slice(0, 19)?.replace('T', ' ')}
            {plan.hostname && ` • ${plan.hostname}`}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!plan && !loading && (
        <div className="text-center py-16 text-slate-500">
          <Bot size={48} className="mx-auto mb-4 text-slate-700" />
          <div className="text-slate-400 font-medium mb-2">No Migration Plan Generated Yet</div>
          <div className="text-sm">Select an asset above and click "Generate Migration Plan"</div>
          <div className="text-xs mt-2 text-slate-600">
            Uses Gemini 2.5 Flash to generate NIST FIPS 203/204/205 specific migration roadmaps
          </div>
        </div>
      )}
    </div>
  )
}
