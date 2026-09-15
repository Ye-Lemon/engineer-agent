import request from './client'
import type { ApiResponse, QueryRequest, QueryResponse } from '@/types'

export async function queryKnowledge(params: QueryRequest): Promise<QueryResponse> {
  const response = await request.post<QueryResponse | ApiResponse<QueryResponse>>('/chat/ask', params)
  const rawResponse: unknown = response
  if (typeof rawResponse === 'string') {
    const line = rawResponse.split('\n').find((item: string) => item.startsWith('data:') && !item.includes('[DONE]'))
    if (line) {
      try { return JSON.parse(line.slice(5).trim()) as QueryResponse } catch { /* fall through */ }
    }
  }
  const result = response as QueryResponse | ApiResponse<QueryResponse>
  return (result as ApiResponse<QueryResponse>).data ?? (result as QueryResponse)
}

export async function streamKnowledge(params: QueryRequest, onChunk?: (result: QueryResponse) => void): Promise<QueryResponse> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/chat/stream`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) })
  if (!response.ok || !response.body) throw new Error(`流式请求失败（${response.status}）`)
  const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''; let latest: QueryResponse | null = null
  while (true) {
    const { value, done } = await reader.read(); buffer += decoder.decode(value || new Uint8Array(), { stream: !done })
    const events = buffer.split('\n\n'); buffer = events.pop() || ''
    for (const event of events) { const line = event.split('\n').find((item) => item.startsWith('data:')); if (!line || line.includes('[DONE]')) continue; latest = JSON.parse(line.slice(5).trim()) as QueryResponse; onChunk?.(latest) }
    if (done) break
  }
  if (!latest) throw new Error('未收到模型响应'); return latest
}

export interface ChatModel { id: string; name: string }
export async function getChatModels(): Promise<{ models: ChatModel[]; default: string }> {
  return request.get('/chat/models')
}
