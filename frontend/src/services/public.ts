import { apiRequest } from './api';
import type { JobType, Paginated, WorkplaceType } from './employer';

export type PublicPostingOrdering =
  | '-updated_at'
  | 'updated_at'
  | '-salary_max'
  | 'salary_max'
  | 'title'
  | '-title';

export interface PublicJobPosting {
  id: string;
  title: string;
  company_name: string;
  job_type: JobType;
  workplace_type: WorkplaceType;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  updated_at: string;
}

export interface PublicPostingFilters {
  search?: string;
  job_type?: JobType | '';
  workplace_type?: WorkplaceType | '';
  min_salary?: number | null;
  location?: string;
}

export const publicPostingApi = {
  list: (
    page: number,
    ordering: PublicPostingOrdering,
    filters: PublicPostingFilters,
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

    return apiRequest<Paginated<PublicJobPosting>>(
      `/public/job-postings/?${params.toString()}`,
    );
  },
};

export const PUBLIC_POSTING_ORDERING_OPTIONS: {
  value: PublicPostingOrdering;
  label: string;
}[] = [
  { value: '-updated_at', label: 'Pagal atnaujinimo datą (naujausi viršuje)' },
  { value: '-salary_max', label: 'Pagal atlyginimą (didžiausias viršuje)' },
  { value: 'title', label: 'Pagal pavadinimą (A–Z)' },
];

export const DEFAULT_PUBLIC_POSTING_ORDERING: PublicPostingOrdering =
  '-updated_at';

export const PUBLIC_POSTING_PAGE_SIZE = 20;
