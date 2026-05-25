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
  CANDIDATE_JOB_POSTING: 'CandidateJobPosting',
  EMPLOYER_APPLICANTS: 'EmployerApplicants',
  EMPLOYER_APPLICATION_DETAIL: 'EmployerApplicationDetail',
  NOT_FOUND: 'NotFound',
} as const;

export type RouteNamesValues = ObjectValues<typeof ROUTE_NAMES>;
