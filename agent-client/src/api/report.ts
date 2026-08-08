import request from './client'
import type { ApiResponse, ReportRequest, ReportResponse } from '@/types'

export async function generateReport(params: ReportRequest): Promise<ReportResponse> {
  const response = await request.post<ReportResponse | ApiResponse<ReportResponse>>('/report/', params)
  const result = response as ReportResponse | ApiResponse<ReportResponse>
  return (result as ApiResponse<ReportResponse>).data ?? (result as ReportResponse)
}
