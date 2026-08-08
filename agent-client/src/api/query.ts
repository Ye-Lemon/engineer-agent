import request from './client'
import type { ApiResponse, QueryRequest, QueryResponse } from '@/types'

export async function queryKnowledge(params: QueryRequest): Promise<QueryResponse> {
  const response = await request.post<QueryResponse | ApiResponse<QueryResponse>>('/query/', params)
  const result = response as QueryResponse | ApiResponse<QueryResponse>
  return (result as ApiResponse<QueryResponse>).data ?? (result as QueryResponse)
}
