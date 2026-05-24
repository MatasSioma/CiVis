import { apiRequest } from './api';

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Company {
  id: string;
  owner: string;
  name: string;
  description: string;
  registration_code: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  website: string;
  date_established: string | null;
  created_at: string;
  updated_at: string;
}

export type CompanyUpdatePayload = Partial<
  Pick<
    Company,
    | 'name'
    | 'description'
    | 'registration_code'
    | 'address'
    | 'contact_email'
    | 'contact_phone'
    | 'website'
    | 'date_established'
  >
>;

export interface Industry {
  id: string;
  name: string;
}

export type SkillType = 'hard' | 'soft' | 'experience';
export type JobType =
  | 'full_time'
  | 'part_time'
  | 'contract'
  | 'internship'
  | 'temporary';
export type JobStatus = 'draft' | 'open' | 'closed';
export type WorkplaceType = 'on_site' | 'remote';

export interface JobPostingSkillRead {
  name: string;
  type: SkillType;
  description: string;
  is_required: boolean;
}

export interface JobPostingSkillInput {
  name: string;
  type: SkillType;
  description: string;
  is_required: boolean;
}

export type JobPostingOrdering =
  | '-created_at'
  | 'created_at'
  | 'title'
  | '-title'
  | '-applicant_count'
  | 'applicant_count';

export interface JobPostingListItem {
  id: string;
  title: string;
  industry: string;
  industry_name: string;
  job_type: JobType;
  workplace_type: WorkplaceType;
  status: JobStatus;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  applicant_count: number;
  created_at: string;
}

export interface JobPostingDetail {
  id: string;
  company: string;
  industry: string;
  title: string;
  description: string;
  workplace_type: WorkplaceType;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  job_type: JobType;
  status: JobStatus;
  skills_detail: JobPostingSkillRead[];
  created_at: string;
  updated_at: string;
}

export interface JobPostingPayload extends Record<string, unknown> {
  industry: string;
  title: string;
  description: string;
  workplace_type: WorkplaceType;
  location?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  job_type: JobType;
  status: JobStatus;
  skills: JobPostingSkillInput[];
}

function isPaginated<T>(value: unknown): value is Paginated<T> {
  return (
    typeof value === 'object' &&
    value !== null &&
    'results' in value &&
    Array.isArray((value as Paginated<T>).results)
  );
}

export const companyApi = {
  async mine(): Promise<Company | null> {
    const data = await apiRequest<Paginated<Company> | Company[]>('/companies/');
    const results = isPaginated<Company>(data) ? data.results : data;
    return results[0] ?? null;
  },
  update: (id: string, payload: CompanyUpdatePayload) =>
    apiRequest<Company>(`/companies/${id}/`, {
      method: 'PATCH',
      body: payload,
    }),
};

export const industryApi = {
  async list(): Promise<Industry[]> {
    const data = await apiRequest<Paginated<Industry> | Industry[]>('/industries/');
    return isPaginated<Industry>(data) ? data.results : data;
  },
  create: (name: string) =>
    apiRequest<Industry>('/industries/', {
      method: 'POST',
      body: { name },
    }),
};

export const jobPostingApi = {
  list: (
    page = 1,
    ordering: JobPostingOrdering = '-created_at',
    search = '',
  ) => {
    const params = new URLSearchParams({
      page: String(page),
      ordering,
    });

    if (search.trim()) {
      params.set('search', search.trim());
    }

    return apiRequest<Paginated<JobPostingListItem>>(
      `/job-postings/?${params.toString()}`,
    );
  },
  get: (id: string) => apiRequest<JobPostingDetail>(`/job-postings/${id}/`),
  create: (payload: JobPostingPayload) =>
    apiRequest<JobPostingDetail>('/job-postings/', {
      method: 'POST',
      body: payload,
    }),
  update: (id: string, payload: JobPostingPayload) =>
    apiRequest<JobPostingDetail>(`/job-postings/${id}/`, {
      method: 'PUT',
      body: payload,
    }),
  delete: (id: string) =>
    apiRequest<void>(`/job-postings/${id}/`, {
      method: 'DELETE',
    }),
  clone: (id: string) =>
    apiRequest<JobPostingDetail>(`/job-postings/${id}/clone/`, {
      method: 'POST',
    }),
};

export const JOB_TYPE_LABELS: Record<JobType, string> = {
  full_time: 'Pilnas etatas',
  part_time: 'Dalinis etatas',
  contract: 'Sutartis',
  internship: 'Praktika',
  temporary: 'Laikinas',
};

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  draft: 'Juodraštis',
  open: 'Atvira',
  closed: 'Uždaryta',
};

export const SKILL_TYPE_LABELS: Record<SkillType, string> = {
  hard: 'Hard skill',
  soft: 'Soft skill',
  experience: 'Darbo patirtis',
};

export const WORKPLACE_TYPE_LABELS: Record<WorkplaceType, string> = {
  on_site: 'Vietoje',
  remote: 'Nuotolinis',
};

export const JOB_POSTING_ORDERING_OPTIONS: {
  value: JobPostingOrdering;
  label: string;
}[] = [
  { value: '-created_at', label: 'Pagal įkėlimo datą (naujausios viršuje)' },
  { value: '-applicant_count', label: 'Pagal aplikantų skaičių (daugiausiai)' },
  { value: 'title', label: 'Pagal pavadinimą (A–Z)' },
];

export const DEFAULT_JOB_POSTING_ORDERING: JobPostingOrdering = '-created_at';

export type ApplicationStatus = 'pending' | 'rejected' | 'accepted';

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  pending: 'Laukia peržiūros',
  rejected: 'Atmesta',
  accepted: 'Priimta',
};

export const APPLICATION_STATUS_VALUES: ApplicationStatus[] = [
  'pending',
  'rejected',
  'accepted',
];

export interface EmployerApplicantListItem {
  id: string;
  applicant_id: string;
  applicant_first_name: string;
  applicant_last_name: string;
  applicant_email: string;
  match_score: number;
  status: ApplicationStatus;
  created_at: string;
}

export interface EmployerApplicationDetail {
  id: string;
  job_posting_id: string;
  job_posting_title: string;
  company_name: string;
  applicant: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    date_of_birth: string | null;
  };
  cv: {
    id: string;
    file_key: string;
    skills: {
      name: string;
      type: SkillType;
      description: string;
    }[];
    created_at: string;
    updated_at: string;
  } | null;
  match_score: number;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

export const employerApplicationApi = {
  list: (jobPostingId: string, page = 1) => {
    const params = new URLSearchParams({
      job_posting: jobPostingId,
      page: String(page),
    });
    return apiRequest<Paginated<EmployerApplicantListItem>>(
      `/applications/?${params.toString()}`,
    );
  },
  get: (id: string) =>
    apiRequest<EmployerApplicationDetail>(`/applications/${id}/`),
  updateStatus: (id: string, status: ApplicationStatus) =>
    apiRequest<EmployerApplicantListItem>(`/applications/${id}/`, {
      method: 'PATCH',
      body: { status },
    }),
};
