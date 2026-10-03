import { expect, test } from '@playwright/test';
import { CANDIDATE, EMPLOYER, mockApi } from './support/mockApi';

const APPLICANT = {
  id: 'application-1',
  applicant_id: CANDIDATE.id,
  applicant_first_name: CANDIDATE.first_name,
  applicant_last_name: CANDIDATE.last_name,
  applicant_email: CANDIDATE.email,
  match_score: 80,
  status: 'pending',
  created_at: '2026-09-20T10:00:00Z',
};

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
    test.fail(
      'TC-FR25-01 filters candidates by minimum score (AC1)',
      {
        annotation: {
          type: 'defect',
          description: 'The applicants list has no filter by minimum score.',
        },
      },
      async ({ page }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto('/employer/job-postings/1/applicants');

        await expect(page.getByLabel('Minimalus įvertinimas')).toBeVisible();
      },
    );

    test.fail(
      'TC-FR25-02 filters candidates by competence (AC2)',
      {
        annotation: {
          type: 'defect',
          description: 'The applicants list has no filter by competence.',
        },
      },
      async ({ page }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto('/employer/job-postings/1/applicants');

        await expect(page.getByLabel('Kompetencija')).toBeVisible();
      },
    );

    test.fail(
      'TC-FR25-03 combines several filters with AND (AC3)',
      {
        annotation: {
          type: 'defect',
          description:
            'The applicants list has no filter by score or competence, so they cannot be combined.',
        },
      },
      async ({ page }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto('/employer/job-postings/1/applicants');

        await expect(page.getByLabel('Minimalus įvertinimas')).toBeVisible();
        await expect(page.getByLabel('Kompetencija')).toBeVisible();
      },
    );

    test('TC-FR25-04 shows an error and keeps the list when filtering fails (AC4)', async ({
      page,
    }) => {
      // The list has no filter by score or competence, so the status filter stands in.
      await mockApi(page, { user: EMPLOYER });
      await page.route(
        (url) => url.pathname === '/api/applications/',
        (route) =>
          route.request().url().includes('status=')
            ? route.fulfill({ status: 500 })
            : route.fulfill({
                json: {
                  count: 1,
                  next: null,
                  previous: null,
                  results: [APPLICANT],
                },
              }),
      );
      await page.goto('/employer/job-postings/1/applicants');
      await page.getByLabel('Būsena').selectOption({ label: 'Atmesta' });

      await expect(page.getByText('Nepavyko įkelti kandidatų.')).toBeVisible();
      await expect(
        page.getByRole('cell', { name: 'Jonas Jonaitis' }),
      ).toBeVisible();
    });
  },
);
