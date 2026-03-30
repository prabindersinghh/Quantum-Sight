import { useEffect, useState, useRef } from 'react'
import { CheckCircle, Loader2, AlertCircle } from 'lucide-react'

interface ScanProgressProps {
  sessionId: string
  onComplete?: (results: any[]) => void
}

interface ProgressState {
  status: 'pending' | 'running' | 'completed' | 'failed'
  scanned: number
  total: number
  percentage: number
  currentHost: string
  results: any[]
}

export default function ScanProgress({ sessionId, onComplete }: ScanProgressProps) {
  const [progress, setProgress] = useState<ProgressState>({
    status: 'pending',
    scanned: 0,
    total: 0,
    percentage: 0,
    currentHost: '',
    results: [],
  })
  const wsRef = useRef<WebSocket | null>(null)
  const resultsRef = useRef<any[]>([])

  useEffect(() => {
    if (!sessionId) return

    const wsUrl = `ws://${window.location.hostname}:8000/ws/scan/${sessionId}`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected for scan', sessionId)
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'progress') {
          if (msg.result) {
            resultsRef.current.push(msg.result)
          }
          setProgress({
            status: msg.status,
            scanned: msg.scanned,
            total: msg.total,
            percentage: msg.percentage,
            currentHost: msg.current_host || '',
            results: [...resultsRef.current],
          })
          if (msg.status === 'completed') {
            onComplete?.(resultsRef.current)
            ws.close()
          }
        }
      } catch (e) {
        // ignore parse errors
      }
    }

    ws.onerror = () => {
      setProgress(p => ({ ...p, status: 'failed' }))
    }

    ws.onclose = () => {
      console.log('WebSocket closed')
    }

    return () => {
      ws.close()
    }
  }, [sessionId])

  const isComplete = progress.status === 'completed'
  const isFailed = progress.status === 'failed'

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {isComplete ? (
            <CheckCircle size={18} className="text-green-400" />
          ) : isFailed ? (
            <AlertCircle size={18} className="text-red-400" />
          ) : (
            <Loader2 size={18} className="text-amber-400 animate-spin" />
          )}
          <span className="text-slate-200 font-semibold text-sm">
            {isComplete ? 'Scan Complete' : isFailed ? 'Scan Failed' : 'Scanning...'}
          </span>
        </div>
        <span className="text-slate-400 text-sm font-mono">
          {progress.scanned}/{progress.total}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-slate-700/50 rounded-full h-2 mb-3">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            isComplete ? 'bg-green-500' : isFailed ? 'bg-red-500' : 'bg-amber-500'
          }`}
          style={{ width: `${progress.percentage}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-slate-500">
        <span className="truncate max-w-xs">
          {progress.currentHost
            ? `Scanning: ${progress.currentHost}`
            : isComplete
            ? 'All domains scanned successfully'
            : 'Waiting...'}
        </span>
        <span className="font-mono text-amber-400 font-semibold">{progress.percentage}%</span>
      </div>

      {/* Recent results */}
      {progress.results.length > 0 && (
        <div className="mt-3 space-y-1 max-h-32 overflow-y-auto">
          {progress.results.slice(-5).reverse().map((r, i) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              {r.success !== false ? (
                <CheckCircle size={11} className="text-green-400 shrink-0" />
              ) : (
                <AlertCircle size={11} className="text-red-400 shrink-0" />
              )}
              <span className={r.success !== false ? 'text-slate-300' : 'text-red-400'}>
                {r.hostname}
              </span>
              {r.error && <span className="text-red-400 truncate">{r.error}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
