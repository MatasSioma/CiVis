import { apiRequest } from './api';

export interface ExtractedSkill {
  name: string;
  type: 'hard' | 'soft' | 'experience';
  description: string;
}

export interface UploadResponse {
  file_key: string;
  skills: ExtractedSkill[];
}

export interface SubmitPayload {
  file_key: string;
  skills: ExtractedSkill[];
}

export interface CVDetailSkill {
  name: string;
  type: 'hard' | 'soft' | 'experience';
  description: string;
}

export interface CVDetailResponse {
  id: string;
  file_key: string;
  skills: CVDetailSkill[];
  created_at: string;
  updated_at: string;
}

export const cvApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiRequest<UploadResponse>('/cv/upload/', {
      method: 'POST',
      body: formData,
    });
  },
  getMyCV: () => apiRequest<CVDetailResponse>('/cv/me/'),
  deleteMyCV: () =>
    apiRequest<void>('/cv/me/', {
      method: 'DELETE',
    }),
  checkout: (payload: SubmitPayload) =>
    apiRequest<{ checkout_url: string }>('/cv/checkout/', {
      method: 'POST',
      body: payload,
    }),
  finalize: (sessionId: string) =>
    apiRequest<CVDetailResponse>('/cv/finalize/', {
      method: 'POST',
      body: { session_id: sessionId },
    }),
};
