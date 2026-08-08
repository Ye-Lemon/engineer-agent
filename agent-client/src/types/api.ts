export interface ApiResponse<T = unknown> {
  code?: number
  message?: string
  data: T
}

export interface HealthResponse {
  status: string
  timestamp: string
  version: string
}
