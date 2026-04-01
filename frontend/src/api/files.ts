import { api } from './axiosInstance'
import type { FileMetadata } from '@/types/file'

export const uploadFile = (projectId: number | 'temp', formData: FormData) =>
  api
    .post<FileMetadata>(`/api/projects/${projectId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)

export const deleteFile = (fileId: number) => api.delete(`/api/files/${fileId}`)

export const getDownloadUrl = (fileId: number) =>
  api.get<{ downloadUrl: string }>(`/api/files/${fileId}/download`).then((r) => r.data)
