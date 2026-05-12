import type { ObjectValues } from '@/shared/types';

export const ROUTE_NAMES = {
  HOME: 'Home',
  ABOUT: 'About',
  CANDIDATE_DASHBOARD: 'CandidateDashboard',
  EMPLOYER_DASHBOARD: 'EmployerDashboard',
  EMPLOYER_JOB_POSTING_NEW: 'EmployerJobPostingNew',
  EMPLOYER_JOB_POSTING_EDIT: 'EmployerJobPostingEdit',
  LOGIN: 'Login',
  SIGNUP: 'Signup',
  GATEWAY: 'Gateway',
  UPLOAD_CV: 'UploadCV',
  MY_CV: 'MyCV',
} as const;

export type RouteNamesValues = ObjectValues<typeof ROUTE_NAMES>;
