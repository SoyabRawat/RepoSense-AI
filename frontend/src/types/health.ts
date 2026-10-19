/**
 * Health response structure matching FastAPI backend schemas.
 */
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  app_name: string
  version: string
  phase: string
  environment: string
  timestamp: string
  capabilities: Record<string, string>
}

export interface HealthState {
  data: HealthResponse | null
  isLoading: boolean
  error: string | null
  latencyMs: number | null
  lastChecked: Date | null
}
