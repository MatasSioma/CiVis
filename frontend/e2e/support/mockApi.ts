import type { Page } from '@playwright/test';

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

const EMPTY_PAGE = { count: 0, next: null, previous: null, results: [] };

interface MockApiOptions {
  /** The logged-in user; a guest when omitted. */
  user?: typeof CANDIDATE | typeof EMPLOYER;
  /** The candidate's CV; not uploaded when omitted. */
  cv?: typeof CV;
}

/**
 * Answers every `/api/*` request in the browser, so specs run without the
 * Django backend. The visitor is a guest unless `user` is given; unknown
 * endpoints return 404. Returns the mocked server state, so specs can check
 * which changes reached the "server".
 */
export async function mockApi(page: Page, { user, cv }: MockApiOptions = {}) {
  const state = { cv: cv ?? null, cvDeleteRequests: 0 };

  await page.route(
    (url) => url.pathname.startsWith('/api/'),
    (route) => {
      const url = new URL(route.request().url());

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

        return route.fulfill({
          json: { count: results.length, next: null, previous: null, results },
        });
      }

      if (url.pathname === '/api/cv/me/') {
        const isDelete = route.request().method() === 'DELETE';

        if (isDelete) {
          state.cvDeleteRequests += 1;
        }

        if (!state.cv) {
          return route.fulfill({
            status: 404,
            json: { detail: 'CV nerastas.' },
          });
        }

        if (isDelete) {
          state.cv = null;
          return route.fulfill({ status: 204 });
        }

        return route.fulfill({ json: state.cv });
      }

      if (
        url.pathname === '/api/applications/' ||
        url.pathname === '/api/candidate/job-postings/'
      ) {
        return route.fulfill({ json: EMPTY_PAGE });
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
