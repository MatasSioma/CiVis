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

/**
 * Answers every `/api/*` request in the browser, so specs run without the
 * Django backend. The visitor is a guest; unknown endpoints return 404.
 */
export async function mockApi(page: Page) {
  await page.route(
    (url) => url.pathname.startsWith('/api/'),
    (route) => {
      const url = new URL(route.request().url());

      if (url.pathname === '/api/auth/session/') {
        return route.fulfill({ json: { authenticated: false, user: null } });
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

      return route.fulfill({ status: 404, json: { detail: 'Not mocked' } });
    },
  );
}
