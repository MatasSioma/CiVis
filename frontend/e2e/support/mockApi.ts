import type { Page, Route } from '@playwright/test';

export const JOB_POSTINGS = [
  {
    id: '1',
    title: 'Frontend programuotojas',
    company_name: 'UAB Pavyzdys',
    job_type: 'full_time',
    workplace_type: 'remote',
    location: null,
    salary_min: 2000,
    salary_max: 3000,
    updated_at: '2026-09-01T10:00:00Z',
  },
  {
    id: '2',
    title: 'Backend programuotojas',
    company_name: 'UAB Testas',
    job_type: 'part_time',
    workplace_type: 'on_site',
    location: 'Vilnius',
    salary_min: 1500,
    salary_max: null,
    updated_at: '2026-09-02T10:00:00Z',
  },
];

export const CANDIDATE = {
  id: 'candidate-1',
  email: 'jonas.jonaitis@example.com',
  first_name: 'Jonas',
  last_name: 'Jonaitis',
  role: 'job_seeker',
  date_of_birth: '1998-04-12',
  created_at: '2026-09-01T10:00:00Z',
  updated_at: '2026-09-01T10:00:00Z',
};

export const EMPLOYER = {
  id: 'employer-1',
  email: 'ona.onaite@example.com',
  first_name: 'Ona',
  last_name: 'Onaitė',
  role: 'employer',
  date_of_birth: null,
  created_at: '2026-09-01T10:00:00Z',
  updated_at: '2026-09-01T10:00:00Z',
};

export const CV = {
  id: 'cv-1',
  file_key: 'cvs/cv-1.pdf',
  skills: [
    {
      name: 'Vue.js',
      type: 'hard',
      description: 'Vieno puslapio aplikacijų kūrimas',
    },
    { name: 'Komandinis darbas', type: 'soft', description: '' },
  ],
  created_at: '2026-09-15T10:00:00Z',
  updated_at: '2026-09-15T10:00:00Z',
};

export const INDUSTRIES = [
  { id: 'industry-1', name: 'Informacinės technologijos' },
  { id: 'industry-2', name: 'Finansai' },
];

export const COMPANY = {
  id: 'company-1',
  owner: EMPLOYER.id,
  name: 'UAB Pavyzdys',
  description: 'Programinės įrangos kūrimas',
  registration_code: '123456789',
  address: 'Vilnius',
  contact_email: 'info@pavyzdys.lt',
  contact_phone: '',
  website: '',
  date_established: null,
  created_at: '2026-09-01T10:00:00Z',
  updated_at: '2026-09-01T10:00:00Z',
};

/** A job posting as the mocked API stores and returns it. */
type JobPosting = Record<string, unknown> & { id: string };

function paginated<T>(results: T[]) {
  return { count: results.length, next: null, previous: null, results };
}

interface MockApiOptions {
  /** The logged-in user; a guest when omitted. */
  user?: typeof CANDIDATE | typeof EMPLOYER;
  /** The candidate's CV; not uploaded when omitted. */
  cv?: typeof CV;
  /** Makes creating or updating a job posting fail with a server error. */
  failJobPostingSaves?: boolean;
}

/**
 * Answers every `/api/*` request in the browser, so specs run without the
 * Django backend. The visitor is a guest unless `user` is given; unknown
 * endpoints return 404. Returns the mocked server state, so specs can check
 * which changes reached the "server".
 */
export async function mockApi(
  page: Page,
  { user, cv, failJobPostingSaves = false }: MockApiOptions = {},
) {
  const state = {
    cv: cv ?? null,
    cvDeleteRequests: 0,
    /** The saved job postings: the mocked `job_postings` table. */
    jobPostings: [] as JobPosting[],
    /** How many requests tried to create or update a job posting. */
    jobPostingSaves: 0,
  };

  function saveJobPosting(route: Route, existing?: JobPosting) {
    state.jobPostingSaves += 1;

    if (failJobPostingSaves) {
      return route.fulfill({
        status: 500,
        contentType: 'text/html',
        body: '<h1>Server Error (500)</h1>',
      });
    }

    const { skills, ...fields } = route.request().postDataJSON();
    const posting: JobPosting = {
      created_at: '2026-10-01T10:00:00Z',
      ...existing,
      ...fields,
      id: existing?.id ?? `posting-${state.jobPostings.length + 1}`,
      company: COMPANY.id,
      skills_detail: skills,
      updated_at: '2026-10-01T10:00:00Z',
    };

    state.jobPostings = [
      ...state.jobPostings.filter((saved) => saved.id !== posting.id),
      posting,
    ];

    return route.fulfill({ status: existing ? 200 : 201, json: posting });
  }

  await page.route(
    (url) => url.pathname.startsWith('/api/'),
    (route) => {
      const url = new URL(route.request().url());
      const method = route.request().method();

      if (url.pathname === '/api/auth/session/') {
        return route.fulfill({
          json: { authenticated: Boolean(user), user: user ?? null },
        });
      }

      if (url.pathname === '/api/public/job-postings/') {
        const search = url.searchParams.get('search')?.toLowerCase() ?? '';
        const results = JOB_POSTINGS.filter((posting) =>
          posting.title.toLowerCase().includes(search),
        );

        return route.fulfill({ json: paginated(results) });
      }

      if (url.pathname === '/api/cv/me/') {
        if (method === 'DELETE') {
          state.cvDeleteRequests += 1;
        }

        if (!state.cv) {
          return route.fulfill({
            status: 404,
            json: { detail: 'CV nerastas.' },
          });
        }

        if (method === 'DELETE') {
          state.cv = null;
          return route.fulfill({ status: 204 });
        }

        return route.fulfill({ json: state.cv });
      }

      if (url.pathname === '/api/industries/') {
        return route.fulfill({ json: INDUSTRIES });
      }

      if (url.pathname === '/api/companies/') {
        return route.fulfill({ json: paginated([COMPANY]) });
      }

      if (url.pathname === '/api/job-postings/') {
        if (method === 'POST') {
          return saveJobPosting(route);
        }

        const listItems = state.jobPostings.map((posting) => ({
          ...posting,
          industry_name: INDUSTRIES.find(
            (industry) => industry.id === posting.industry,
          )?.name,
          applicant_count: 0,
        }));

        return route.fulfill({ json: paginated(listItems) });
      }

      const postingId = url.pathname.match(
        /^\/api\/job-postings\/([^/]+)\/$/,
      )?.[1];

      if (postingId) {
        const posting = state.jobPostings.find(
          (saved) => saved.id === postingId,
        );

        if (!posting) {
          return route.fulfill({
            status: 404,
            json: { detail: 'No JobPosting matches the given query.' },
          });
        }

        if (method === 'PUT') {
          return saveJobPosting(route, posting);
        }

        return route.fulfill({ json: posting });
      }

      if (
        url.pathname === '/api/applications/' ||
        url.pathname === '/api/candidate/job-postings/'
      ) {
        return route.fulfill({ json: paginated([]) });
      }

      // No applications exist, like in the backend after a candidate deletes
      // their CV: the applications made with it are deleted too.
      if (url.pathname.startsWith('/api/applications/')) {
        return route.fulfill({
          status: 404,
          json: { detail: 'No Application matches the given query.' },
        });
      }

      return route.fulfill({ status: 404, json: { detail: 'Not mocked' } });
    },
  );

  return state;
}
