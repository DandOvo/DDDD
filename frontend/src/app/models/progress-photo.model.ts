export interface ProgressPhoto {
  id: string;
  userId: string;
  fileName: string;
  originalFileName: string;
  mediaType: string;
  fileSize: number;
  mimeType: string;
  blobUrl: string;
  thumbnailUrl?: string;
  photoType: string;
  notes?: string;
  recordedAt: Date;
  uploadedAt: Date;
  updatedAt: Date;
}

export interface ProgressPhotoListResponse {
  items: ProgressPhoto[];
  total: number;
  page: number;
  pageSize: number;
}
