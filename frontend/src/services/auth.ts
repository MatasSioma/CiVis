import type { SessionUser, UserRole } from '@/shared/types';
import { apiRequest } from './api';

export interface AuthSession {
  authenticated: boolean;
  user: SessionUser | null;
}

export interface LoginPayload {
  personal_code: string;
  password: string;
  role: UserRole;
}

export interface SignupPayload extends LoginPayload {
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  date_of_birth?: string;
  company_name?: string;
  company_description?: string;
}

export const authApi = {
  session: () => apiRequest<AuthSession>('/auth/session/'),
  login: (payload: LoginPayload) =>
    apiRequest<AuthSession>('/auth/login/', {
      method: 'POST',
      body: payload,
    }),
  signup: (payload: SignupPayload) =>
    apiRequest<AuthSession>('/auth/signup/', {
      method: 'POST',
      body: payload,
    }),
  logout: () =>
    apiRequest<void>('/auth/logout/', {
      method: 'POST',
    }),
};
