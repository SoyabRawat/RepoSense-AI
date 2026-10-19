import React from 'react'
import { Server, RefreshCw, Terminal, AlertTriangle, ShieldCheck } from 'lucide-react'
import type { HealthResponse } from '../types/health'
import { StatusBadge } from './StatusBadge'

interface ConnectivityCardProps {
  data: HealthResponse | null
  isLoading: boolean
  error: string | null
  latencyMs: number | null
  lastChecked: Date | null
  onRetry: () => void
}

export const ConnectivityCard: React.FC<ConnectivityCardProps> = ({
  data,
  isLoading,
  error,
  latencyMs,
  lastChecked,
  onRetry,
}) => {
  const status = isLoading ? 'loading' : error ? 'error' : 'connected'

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Backend API Verification</h2>
            <p className="text-xs text-slate-400">
              Live HTTP connectivity test to FastAPI service
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <StatusBadge status={status} latencyMs={latencyMs} />
          <button
            onClick={onRetry}
            disabled={isLoading}
            title="Refresh connectivity check"
            className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 disabled:opacity-50 rounded-lg transition-colors border border-slate-700/60 cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="mt-5">
        {isLoading && !data && (
          <div className="py-8 text-center text-slate-400 text-sm">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400" />
            Connecting to backend at <code className="text-indigo-300">127.0.0.1:8000 / 8001 /api/v1/health</code>...
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-rose-950/30 border border-rose-800/40 p-4 text-sm text-rose-300">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <p className="font-medium text-rose-200">Backend Unreachable</p>
                <p className="text-xs text-rose-300/80 font-mono break-all">{error}</p>
                <div className="pt-2 text-xs text-slate-300 bg-slate-950/60 rounded p-2.5 border border-slate-800">
                  <p className="font-semibold text-slate-200 mb-1 flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5" /> Local Start Command:
                  </p>
                  <code className="text-indigo-300 block">
                    backend\.venv\Scripts\uvicorn app.main:app --app-dir backend --port 8000 (or 8001)
                  </code>
                </div>
              </div>
            </div>
          </div>
        )}

        {data && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Application</span>
                <span className="font-medium text-white">{data.app_name}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Version</span>
                <span className="font-mono text-indigo-300">{data.version}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Environment</span>
                <span className="font-mono text-emerald-400 capitalize">{data.environment}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400 block mb-1">Latency</span>
                <span className="font-mono text-amber-300">{latencyMs} ms</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                Declared Capabilities & Boundaries (Verified)
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {Object.entries(data.capabilities).map(([capability, statusDesc]) => {
                  const isActive = statusDesc === 'active'
                  return (
                    <div
                      key={capability}
                      className="flex items-center justify-between p-2 rounded bg-slate-900/90 border border-slate-800/80"
                    >
                      <span className="font-mono text-slate-300 capitalize">
                        {capability.replace(/_/g, ' ')}
                      </span>
                      <span
                        className={`text-[11px] px-2 py-0.5 rounded font-medium ${
                          isActive
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {statusDesc}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            {lastChecked && (
              <div className="text-[11px] text-slate-500 text-right">
                Last checked: {lastChecked.toLocaleTimeString()}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
