export type FileType = 'PRESENTATION' | 'REPORT' | 'README' | 'CODE_ZIP' | 'POSTER' | 'LINK'

export interface ProjectFile {
  id: number
  projectId: number
  originalName: string
  storedName: string
  mimeType: string
  size: number
  fileType: FileType
  isRestricted: boolean
  uploadedAt: string
}

export interface FileMetadata {
  fileId: number
  originalName: string
  storedName: string
  size: number
  uploadedAt: string
}
