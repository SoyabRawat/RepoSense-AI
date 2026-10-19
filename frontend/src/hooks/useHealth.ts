import { useState, useEffect, useCallback } from 'react'
import type { HealthState } from '../types/health'
import { checkBackendHealth } from '../services/api'

export function useHealth(autoPollIntervalMs = 0) {
  const [state, setState] = useState<HealthState>({
    data: null,
    isLoading: true,
    error: null,
    latencyMs: null,
    lastChecked: null,
  })

  const refetch = useCallback(() => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    checkBackendHealth()
      .then(({ data, latencyMs }) => {
        setState({
          data,
          isLoading: false,
          error: null,
          latencyMs,
          lastChecked: new Date(),
        })
      })
      .catch((err: unknown) => {
        const message =
          err instanceof Error ? err.message : 'Backend connection failed'
        setState({
          data: null,
          isLoading: false,
          error: message,
          latencyMs: null,
          lastChecked: new Date(),
        })
      })
  }, [])

  useEffect(() => {
    let cancelled = false
    checkBackendHealth()
      .then(({ data, latencyMs }) => {
        if (!cancelled) {
          setState({
            data,
            isLoading: false,
            error: null,
            latencyMs,
            lastChecked: new Date(),
          })
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message =
            err instanceof Error ? err.message : 'Backend connection failed'
          setState({
            data: null,
            isLoading: false,
            error: message,
            latencyMs: null,
            lastChecked: new Date(),
          })
        }
      })

    if (autoPollIntervalMs > 0) {
      const interval = setInterval(refetch, autoPollIntervalMs)
      return () => {
        cancelled = true
        clearInterval(interval)
      }
    }

    return () => {
      cancelled = true
    }
  }, [refetch, autoPollIntervalMs])

  return {
    ...state,
    refetch,
  }
}
