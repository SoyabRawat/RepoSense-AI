import React from 'react'
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'

interface StatusBadgeProps {
  status: 'connected' | 'error' | 'loading'
  latencyMs?: number | null
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, latencyMs }) => {
  if (status === 'loading') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
        Checking Connection...
      </span>
    )
  }

  if (status === 'connected') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <CheckCircle2 className="w-3.5 h-3.5" />
        API Online {latencyMs !== undefined && latencyMs !== null ? `(${latencyMs}ms)` : ''}
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
      <AlertCircle className="w-3.5 h-3.5" />
      API Disconnected
    </span>
  )
}
