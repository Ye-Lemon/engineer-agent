import request from './client'
import type {
  ApiResponse,
  DeleteFileResponse,
  FileInfo,
  FileListResponse,
  TaskStatusResponse,
  UploadResponse,
} from '@/types'
import type { AxiosProgressEvent } from 'axios'

function unwrap<T>(response: T | ApiResponse<T>): T {
  return (response as ApiResponse<T>).data ?? (response as T)
}

export async function uploadDocument(file: File, collectionName?: string, onProgress?: (progress: number) => void): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  if (collectionName) formData.append('collection_name', collectionName)

  const response = await request.post<UploadResponse | ApiResponse<UploadResponse>>('/doc/upload', formData, {
    // Override the Axios instance's JSON default so FastAPI can parse UploadFile.
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event: AxiosProgressEvent) => {
      if (event.total) onProgress?.(Math.round((event.loaded / event.total) * 100))
    },
  })
  return unwrap(response as UploadResponse | ApiResponse<UploadResponse>)
}

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const response = await request.get<TaskStatusResponse | ApiResponse<TaskStatusResponse>>(`/tasks/${taskId}`)
  return unwrap(response as TaskStatusResponse | ApiResponse<TaskStatusResponse>)
}

export async function getFileList(): Promise<FileListResponse> {
  const response = await request.get<FileListResponse | ApiResponse<FileListResponse>>('/files/')
  return unwrap(response as FileListResponse | ApiResponse<FileListResponse>)
}

export async function getFileInfo(filename: string): Promise<FileInfo> {
  const response = await request.get<FileInfo | ApiResponse<FileInfo>>(`/files/${filename}`)
  return unwrap(response as FileInfo | ApiResponse<FileInfo>)
}

export async function deleteFile(filename: string): Promise<DeleteFileResponse> {
  const response = await request.delete<DeleteFileResponse | ApiResponse<DeleteFileResponse>>(`/files/${filename}`)
  return unwrap(response as DeleteFileResponse | ApiResponse<DeleteFileResponse>)
}

export function downloadFile(filename: string): Promise<Blob> {
  return request.get(`/download/${filename}`, { responseType: 'blob' })
}
