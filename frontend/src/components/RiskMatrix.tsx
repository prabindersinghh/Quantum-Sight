interface RiskMatrixProps {
  data?: Record<string, number>
}

const CELLS = [
  // [impact, likelihood, label, bg]
  ['High', 'High', 'Critical', 'bg-red-600/60 border-red-500/40 text-red-200'],
  ['High', 'Medium', 'High Risk', 'bg-red-700/40 border-red-600/30 text-red-300'],
  ['High', 'Low', 'Medium', 'bg-orange-700/30 border-orange-600/30 text-orange-300'],
  ['Medium', 'High', 'High Risk', 'bg-red-700/40 border-red-600/30 text-red-300'],
  ['Medium', 'Medium', 'Medium', 'bg-amber-700/30 border-amber-600/30 text-amber-300'],
  ['Medium', 'Low', 'Low', 'bg-yellow-800/20 border-yellow-700/30 text-yellow-300'],
  ['Low', 'High', 'Medium', 'bg-orange-700/30 border-orange-600/30 text-orange-300'],
  ['Low', 'Medium', 'Low', 'bg-yellow-800/20 border-yellow-700/30 text-yellow-300'],
  ['Low', 'Low', 'Safe', 'bg-green-800/20 border-green-700/30 text-green-400'],
]

const DEMO_COUNTS: Record<string, number> = {
  'High-High': 2,
  'High-Medium': 1,
  'High-Low': 0,
  'Medium-High': 1,
  'Medium-Medium': 3,
  'Medium-Low': 2,
  'Low-High': 0,
  'Low-Medium': 1,
  'Low-Low': 2,
}

export default function RiskMatrix({ data }: RiskMatrixProps) {
  const counts = data || DEMO_COUNTS
  const impacts = ['High', 'Medium', 'Low']
  const likelihoods = ['High', 'Medium', 'Low']

  return (
    <div className="bg-slate-800/40 rounded-xl border border-slate-700/50 p-4">
      <h3 className="text-slate-300 text-sm font-semibold mb-4">Risk Overview Matrix</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="text-slate-500 text-left pb-2 pr-3 font-medium">Impact ↓ / Likelihood →</th>
              {likelihoods.map(l => (
                <th key={l} className="text-slate-400 text-center pb-2 px-2 font-medium">{l}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {impacts.map(impact => (
              <tr key={impact}>
                <td className="text-slate-400 py-1.5 pr-3 font-medium">{impact}</td>
                {likelihoods.map(likelihood => {
                  const key = `${impact}-${likelihood}`
                  const cell = CELLS.find(c => c[0] === impact && c[1] === likelihood)
                  const count = counts[key] || 0
                  const style = cell ? cell[3] : 'bg-slate-700/30 text-slate-400'

                  return (
                    <td key={likelihood} className="py-1.5 px-2 text-center">
                      <div className={`inline-flex flex-col items-center justify-center w-16 h-14 rounded-lg border ${style}`}>
                        <span className="text-base font-bold">{count}</span>
                        <span className="text-xs opacity-75">{cell?.[2]}</span>
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 flex gap-3 flex-wrap">
        {[
          { label: 'Critical/High Risk', color: 'bg-red-500' },
          { label: 'Medium Risk', color: 'bg-amber-500' },
          { label: 'Low/Safe', color: 'bg-green-500' },
        ].map(l => (
          <div key={l.label} className="flex items-center gap-1.5 text-xs text-slate-400">
            <div className={`w-2 h-2 rounded-full ${l.color}`} />
            {l.label}
          </div>
        ))}
      </div>
    </div>
  )
}
