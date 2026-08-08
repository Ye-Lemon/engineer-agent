export interface FileInfo {
  filename: string
  size: number
  created_at: number
  modified_at: number
  path: string
}

export interface FileListResponse {
  files: FileInfo[]
}

export interface DeleteFileResponse {
  success: boolean
  message: string
}

export interface UploadRequest {
  collection_name?: string
}

export interface UploadResponse {
  task_id: string
  status: string
  filename: string
}

export interface TaskStatusResponse {
  task_id: string
  status: string
  filename?: string
  step?: string
  chunks?: number
  error?: string
  created_at?: string
}

export interface QueryRequest {
  question: string
  top_k?: number
  collection_name?: string
}

export interface SourceDocument {
  content: string
  source: string
  page?: number
  similarity?: number
}

export interface QueryResponse {
  answer: string
  sources: SourceDocument[]
  processing_time_ms: number
}

export interface ReportRequest {
  report_type: string
  parameters: Record<string, unknown>
  collection_name?: string
}

export interface ReportReference {
  standard_name: string
  section?: string
  content?: string
}

export interface ReportResponse {
  content: string
  references: ReportReference[]
  generated_at: string
}
