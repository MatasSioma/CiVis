import { apiRequest } from './api';

export interface ExtractedSkill {
  name: string;
  type: 'hard' | 'soft' | 'experience';
  years_of_experience: number;
}

export interface UploadResponse {
  file_key: string;
  skills: ExtractedSkill[];
}

export interface SubmitPayload {
  file_key: string;
  skills: ExtractedSkill[];
}

export interface CVResponse {
  id: string;
  user: string;
  file_key: string;
  skills: { id: string; name: string }[];
  created_at: string;
  updated_at: string;
}

export interface CVDetailSkill {
  name: string;
  type: 'hard' | 'soft' | 'experience';
  years_of_experience: number;
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
  submit: (payload: SubmitPayload) =>
    apiRequest<CVResponse>('/cv/submit/', {
      method: 'POST',
      body: payload,
    }),
  getMyCV: () => apiRequest<CVDetailResponse>('/cv/me/'),
  checkout: (payload: SubmitPayload) =>
    apiRequest<{ checkout_url: string }>('/cv/checkout/', {
      method: 'POST',
      body: payload,
    }),
};
