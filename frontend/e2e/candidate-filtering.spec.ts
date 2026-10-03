import { expect, test, type Page } from '@playwright/test';
import {
  CANDIDATE,
  COMPANY,
  EMPLOYER,
  INDUSTRIES,
  mockApi,
} from './support/mockApi';

const POSTING = {
  id: '1',
  company: COMPANY.id,
  industry: INDUSTRIES[0].id,
  title: 'Frontend programuotojas',
  description: 'Kurti ir prižiūrėti įmonės interneto aplikacijas.',
  workplace_type: 'remote',
  location: null,
  salary_min: 2000,
  salary_max: 3000,
  job_type: 'full_time',
  status: 'open',
  skills_detail: [
    { name: 'Vue.js', type: 'hard', description: '', is_required: true },
    { name: 'Python', type: 'hard', description: '', is_required: false },
  ],
  created_at: '2026-09-01T10:00:00Z',
  updated_at: '2026-09-01T10:00:00Z',
};

const CANDIDATES_URL = `/employer/job-postings/${POSTING.id}/applicants`;

function applicant(
  number: number,
  firstName: string,
  lastName: string,
  matchScore: number,
) {
  return {
    id: `application-${number}`,
    applicant_id: `candidate-${number}`,
    applicant_first_name: firstName,
    applicant_last_name: lastName,
    applicant_email: `${firstName}.${lastName}@example.com`.toLowerCase(),
    match_score: matchScore,
    status: 'pending',
    created_at: '2026-09-20T10:00:00Z',
  };
}

// The candidates who applied, with the match scores of the backend test, in
// the API's default order (newest first), which is not the order of the scores.
const APPLICANTS = [
  applicant(1, CANDIDATE.first_name, CANDIDATE.last_name, 50),
  applicant(2, 'Petras', 'Petraitis', 0),
  applicant(3, 'Mantas', 'Mantaitis', 100),
  applicant(4, 'Lukas', 'Lukaitis', 1),
  applicant(5, 'Rokas', 'Rokaitis', 99),
];

/** The employer's posting 1 and the candidates who applied to it. */
async function mockCandidateList(page: Page) {
  await mockApi(page, { user: EMPLOYER });
  await page.route(
    (url) => url.pathname === `/api/job-postings/${POSTING.id}/`,
    (route) => route.fulfill({ json: POSTING }),
  );
  await page.route(
    (url) => url.pathname === '/api/applications/',
    (route) => {
      // Like the API, sorts the candidates by match score when asked to.
      const ordering = new URL(route.request().url()).searchParams.get(
        'ordering',
      );
      const results =
        ordering === '-match_score'
          ? [...APPLICANTS].sort((a, b) => b.match_score - a.match_score)
          : APPLICANTS;

      return route.fulfill({
        json: { count: results.length, next: null, previous: null, results },
      });
    },
  );
}

/** The candidates' rows, without the header row. */
function candidateRows(page: Page) {
  return page.getByRole('row').filter({ has: page.getByRole('cell') });
}

async function sortByBestMatch(page: Page) {
  await page
    .getByLabel('Rikiuoti')
    .selectOption({ label: 'Pagal atitikimą (geriausi viršuje)' });
}

test.describe(
  'KAN-25 FR-01: Sistema turi apdoroti kandidatų filtravimo kriterijus',
  {
    tag: '@KAN-25',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-25',
    },
  },
  () => {
    test('TC-FR25-01 sorts candidates by match score, best first (AC1)', async ({
      page,
    }) => {
      // The list has no filter by minimum score, so sorting by match score stands in.
      await mockCandidateList(page);
      await page.goto(CANDIDATES_URL);
      await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);

      await sortByBestMatch(page);

      await expect(candidateRows(page).getByText(/\d+ \/ 100/)).toHaveText([
        '100 / 100',
        '99 / 100',
        '50 / 100',
        '1 / 100',
        '0 / 100',
      ]);
    });

    test(
      'TC-FR25-02 filters candidates by competence (AC2)',
      {
        annotation: {
          type: 'defect',
          description: 'The applicants list has no filter by competence.',
        },
      },
      async ({ page }) => {
        await mockCandidateList(page);
        await page.goto(CANDIDATES_URL);
        await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);

        await expect(page.getByLabel('Kompetencija')).toBeVisible();
      },
    );

    test(
      'TC-FR25-03 combines several filters with AND (AC3)',
      {
        annotation: {
          type: 'defect',
          description:
            'The applicants list has no filter by competence, so it cannot be combined with sorting by match score.',
        },
      },
      async ({ page }) => {
        await mockCandidateList(page);
        await page.goto(CANDIDATES_URL);
        await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);

        await sortByBestMatch(page);
        await expect(page.getByLabel('Kompetencija')).toBeVisible();
      },
    );

    test('TC-FR25-04 shows an error and keeps the list when filtering fails (AC4)', async ({
      page,
    }) => {
      // The list has no filter by score or competence, so the status filter stands in.
      await mockCandidateList(page);
      await page.route(
        (url) =>
          url.pathname === '/api/applications/' &&
          url.searchParams.has('status'),
        (route) => route.fulfill({ status: 500 }),
      );
      await page.goto(CANDIDATES_URL);
      await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);
      await page.getByLabel('Būsena').selectOption({ label: 'Atmesta' });

      await expect(page.getByText('Nepavyko įkelti kandidatų.')).toBeVisible();
      await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);
    });
  },
);
