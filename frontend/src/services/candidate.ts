import { apiRequest } from './api';
import type {
  JobPostingSkillRead,
  JobStatus,
  JobType,
  Paginated,
  WorkplaceType,
} from './employer';

export type CandidatePostingOrdering =
  | '-match_score'
  | 'match_score'
  | '-updated_at'
  | 'updated_at'
  | '-salary_max'
  | 'salary_max'
  | 'title'
  | '-title';

export interface CandidateJobPosting {
  id: string;
  title: string;
  company_name: string;
  job_type: JobType;
  workplace_type: WorkplaceType;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  updated_at: string;
  match_score: number;
  has_applied: boolean;
}

export interface CandidatePostingFilters {
  search?: string;
  job_type?: JobType | '';
  workplace_type?: WorkplaceType | '';
  min_salary?: number | null;
  location?: string;
}

export interface CandidateCompany {
  id: string;
  name: string;
  description: string;
  registration_code: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  website: string;
  date_established: string | null;
}

export interface CandidateJobPostingDetail {
  id: string;
  title: string;
  description: string;
  company: CandidateCompany;
  industry_name: string;
  job_type: JobType;
  workplace_type: WorkplaceType;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  status: JobStatus;
  skills: JobPostingSkillRead[];
  match_score: number;
  has_applied: boolean;
  application_id: string | null;
  created_at: string;
  updated_at: string;
}

export const candidatePostingApi = {
  list: (
    page: number,
    ordering: CandidatePostingOrdering,
    filters: CandidatePostingFilters,
  ) => {
    const params = new URLSearchParams({ page: String(page), ordering });

    if (filters.search && filters.search.trim()) {
      params.set('search', filters.search.trim());
    }
    if (filters.job_type) {
      params.set('job_type', filters.job_type);
    }
    if (filters.workplace_type) {
      params.set('workplace_type', filters.workplace_type);
    }
    if (filters.min_salary != null && filters.min_salary > 0) {
      params.set('min_salary', String(filters.min_salary));
    }
    if (filters.location && filters.location.trim()) {
      params.set('location', filters.location.trim());
    }

    return apiRequest<Paginated<CandidateJobPosting>>(
      `/candidate/job-postings/?${params.toString()}`,
    );
  },
  get: (id: string) =>
    apiRequest<CandidateJobPostingDetail>(`/candidate/job-postings/${id}/`),
  apply: (jobPostingId: string) =>
    apiRequest<{ id: string }>('/applications/', {
      method: 'POST',
      body: { job_posting: jobPostingId },
    }),
};

export type ApplicationStatus = 'pending' | 'rejected' | 'accepted';

export interface CandidateApplication {
  id: string;
  job_posting: string;
  job_posting_title: string;
  company_name: string;
  match_score: number;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

function isPaginated<T>(value: unknown): value is Paginated<T> {
  return (
    typeof value === 'object' &&
    value !== null &&
    'results' in value &&
    Array.isArray((value as Paginated<T>).results)
  );
}

export const candidateApplicationApi = {
  async list(): Promise<CandidateApplication[]> {
    const data = await apiRequest<
      Paginated<CandidateApplication> | CandidateApplication[]
    >('/applications/');
    return isPaginated<CandidateApplication>(data) ? data.results : data;
  },
  cancel: (id: string) =>
    apiRequest<void>(`/applications/${id}/`, {
      method: 'DELETE',
    }),
};

export const CANDIDATE_POSTING_ORDERING_OPTIONS: {
  value: CandidatePostingOrdering;
  label: string;
}[] = [
  { value: '-match_score', label: 'Pagal atitikimą (geriausi viršuje)' },
  { value: '-updated_at', label: 'Pagal atnaujinimo datą (naujausi viršuje)' },
  { value: '-salary_max', label: 'Pagal atlyginimą (didžiausias viršuje)' },
  { value: 'title', label: 'Pagal pavadinimą (A–Z)' },
];

export const DEFAULT_CANDIDATE_POSTING_ORDERING: CandidatePostingOrdering =
  '-match_score';

export const CANDIDATE_POSTING_PAGE_SIZE = 20;
