import type { HealthResponse } from '../types/health'

export const CONFIGURED_BACKEND_URL =
  (import.meta.env.VITE_BACKEND_URL as string | undefined) || null

// Candidate URLs to probe for local development (supports default 8000 and alternate 8001 if 8000 is occupied)
const PROBE_URLS = CONFIGURED_BACKEND_URL
  ? [CONFIGURED_BACKEND_URL]
  : ['http://127.0.0.1:8000', 'http://127.0.0.1:8001']

let activeBaseUrl: string = PROBE_URLS[0]

export function getActiveBaseUrl(): string {
  return activeBaseUrl
}

export interface HealthCheckResult {
  data: HealthResponse
  latencyMs: number
  endpointUsed: string
}

/**
 * Fetch health status from backend API with latency measurement and fallback port support.
 */
export async function checkBackendHealth(): Promise<HealthCheckResult> {
  const startTime = performance.now()
  let lastError: Error | null = null

  for (const baseUrl of PROBE_URLS) {
    const endpoint = `${baseUrl}/api/v1/health`
    try {
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: { Accept: 'application/json' },
      })

      const latencyMs = Math.round(performance.now() - startTime)

      if (response.ok) {
        const data = (await response.json()) as HealthResponse
        // Verify this is actually a RepoSense AI backend response
        if (data && data.app_name && data.app_name.includes('RepoSense')) {
          activeBaseUrl = baseUrl
          return { data, latencyMs, endpointUsed: endpoint }
        }
      }
    } catch (err: unknown) {
      lastError = err instanceof Error ? err : new Error(String(err))
    }
  }

  const endpointList = PROBE_URLS.map((u) => `${u}/api/v1/health`).join(' or ')
  const message = lastError ? lastError.message : 'No responsive RepoSense AI backend found'
  throw new Error(`Failed to connect to backend at ${endpointList}: ${message}`)
}

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const base = getActiveBaseUrl()
  const endpoint = `${base}${path.startsWith('/') ? path : `/${path}`}`

  const response = await fetch(endpoint, {
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`
    try {
      const errJson = await response.json()
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail)
      } else if (errJson.error) {
        errorDetail = errJson.error
      }
    } catch {
      // ignored
    }
    throw new Error(errorDetail)
  }

  return (await response.json()) as T
}
