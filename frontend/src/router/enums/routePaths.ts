import type { ObjectValues } from '@/shared/types';

export const ROUTE_PATHS = {
  HOME: '',
  ABOUT: 'about',
  CANDIDATE_DASHBOARD: 'candidate',
  EMPLOYER_DASHBOARD: 'employer',
  EMPLOYER_JOB_POSTING_NEW: 'employer/job-postings/new',
  EMPLOYER_JOB_POSTING_EDIT: 'employer/job-postings/:id',
  LOGIN: 'login',
  SIGNUP: 'signup',
  GATEWAY: 'gateway',
  UPLOAD_CV: 'candidate/upload-cv',
  MY_CV: 'candidate/my-cv',
  CANDIDATE_JOB_POSTING: 'candidate/job-postings/:id',
  EMPLOYER_APPLICANTS: 'employer/job-postings/:id/applicants',
  EMPLOYER_APPLICATION_DETAIL:
    'employer/job-postings/:postingId/applications/:id',
  NOT_FOUND: '/:pathMatch(.*)*',
} as const;

export type RoutePathsValues = ObjectValues<typeof ROUTE_PATHS>;
