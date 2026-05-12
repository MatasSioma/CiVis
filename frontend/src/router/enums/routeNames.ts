import type { ObjectValues } from '@/shared/types';

export const ROUTE_NAMES = {
  HOME: 'Home',
  ABOUT: 'About',
  CANDIDATE_DASHBOARD: 'CandidateDashboard',
  EMPLOYER_DASHBOARD: 'EmployerDashboard',
  LOGIN: 'Login',
  SIGNUP: 'Signup',
  GATEWAY: 'Gateway',
  UPLOAD_CV: 'UploadCV',
  MY_CV: 'MyCV',
} as const;

export type RouteNamesValues = ObjectValues<typeof ROUTE_NAMES>;
