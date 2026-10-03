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

// The candidates who applied, with the match scores of the backend test: the
// TC-FR25-01 boundaries 0, 1, 99 and 100, and 50 in between.
const APPLICANTS = [
  applicant(1, CANDIDATE.first_name, CANDIDATE.last_name, 0),
  applicant(2, 'Petras', 'Petraitis', 1),
  applicant(3, 'Mantas', 'Mantaitis', 50),
  applicant(4, 'Lukas', 'Lukaitis', 99),
  applicant(5, 'Rokas', 'Rokaitis', 100),
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
    (route) =>
      route.fulfill({
        json: {
          count: APPLICANTS.length,
          next: null,
          previous: null,
          results: APPLICANTS,
        },
      }),
  );
}

/** The candidates' rows, without the header row. */
function candidateRows(page: Page) {
  return page.getByRole('row').filter({ has: page.getByRole('cell') });
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
    test(
      'TC-FR25-01 filters candidates by minimum score (AC1)',
      {
        annotation: {
          type: 'defect',
          description: 'The applicants list has no filter by minimum score.',
        },
      },
      async ({ page }) => {
        await mockCandidateList(page);
        await page.goto(CANDIDATES_URL);
        await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);

        await expect(page.getByLabel('Minimalus įvertinimas')).toBeVisible();
      },
    );

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
            'The applicants list has no filter by score or competence, so they cannot be combined.',
        },
      },
      async ({ page }) => {
        await mockCandidateList(page);
        await page.goto(CANDIDATES_URL);
        await expect(candidateRows(page)).toHaveCount(APPLICANTS.length);

        await expect(page.getByLabel('Minimalus įvertinimas')).toBeVisible();
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
