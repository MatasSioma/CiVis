export type ObjectValues<T> = T[keyof T];

export type UserRole = 'job_seeker' | 'employer';

export interface SessionUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}
