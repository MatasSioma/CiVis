import type { ObjectValues } from '@/shared/types';

export const ROUTE_PATHS = {
  HOME: '',
  ABOUT: 'about',
  CANDIDATE_DASHBOARD: 'candidate',
  EMPLOYER_DASHBOARD: 'employer',
  LOGIN: 'login',
  SIGNUP: 'signup',
  GATEWAY: 'gateway',
  UPLOAD_CV: 'candidate/upload-cv',
  MY_CV: 'candidate/my-cv',
} as const;

export type RoutePathsValues = ObjectValues<typeof ROUTE_PATHS>;
