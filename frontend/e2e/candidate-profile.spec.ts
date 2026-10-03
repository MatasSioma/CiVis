import { expect, test, type Page } from '@playwright/test';
import { CANDIDATE, CV, EMPLOYER, mockApi } from './support/mockApi';

const PROFILE_URL = '/employer/job-postings/1/applications/application-1';

const APPLICATION = {
  id: 'application-1',
  job_posting_id: '1',
  job_posting_title: 'Frontend programuotojas',
  company_name: 'UAB Pavyzdys',
  applicant: CANDIDATE,
  cv: {
    ...CV,
    skills: [
      ...CV.skills,
      { name: 'Pardavimų vadyba', type: 'experience', description: '' },
    ],
  },
  match_score: 80,
  status: 'pending',
  created_at: '2026-09-20T10:00:00Z',
  updated_at: '2026-09-20T10:00:00Z',
};

/** The employer's applicants list and the profile of the one candidate in it. */
async function mockCandidate(page: Page) {
  await mockApi(page, { user: EMPLOYER });
  await page.route(
    (url) => url.pathname.startsWith('/api/applications/'),
    (route) => {
      const isList =
        new URL(route.request().url()).pathname === '/api/applications/';
      const listItem = {
        ...APPLICATION,
        applicant_id: CANDIDATE.id,
        applicant_first_name: CANDIDATE.first_name,
        applicant_last_name: CANDIDATE.last_name,
        applicant_email: CANDIDATE.email,
      };

      return route.fulfill({
        json: isList
          ? { count: 1, next: null, previous: null, results: [listItem] }
          : APPLICATION,
      });
    },
  );
}

test.describe(
  'KAN-32 US-03: Peržiūrėti kandidato profilį',
  {
    tag: '@KAN-32',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-32',
    },
  },
  () => {
    test('TC-US32-01 opens the candidate profile from the candidates list (AC1)', async ({
      page,
    }) => {
      await mockCandidate(page);
      await page.goto('/employer/job-postings/1/applicants');
      await page.getByRole('cell', { name: 'Jonas Jonaitis' }).click();

      await expect(page).toHaveURL(PROFILE_URL);
      await expect(
        page.getByRole('heading', { name: 'Jonas Jonaitis' }),
      ).toBeVisible();
    });

    test('TC-US32-02 loads the profile within 2 seconds (AC2)', async ({
      page,
    }) => {
      // The API is mocked, so this only measures how fast the page renders.
      // The designed 1.9 / 2 / 2.1 s dataset is not simulated.
      await mockCandidate(page);
      await page.goto('/employer/job-postings/1/applicants');
      await page.getByRole('cell', { name: 'Jonas Jonaitis' }).click();

      await expect(
        page.getByRole('heading', { name: 'Jonas Jonaitis' }),
      ).toBeVisible({ timeout: 2_000 });
    });

    test('TC-US32-03 shows the name, work experience and competences (AC3)', async ({
      page,
    }) => {
      await mockCandidate(page);
      await page.goto(PROFILE_URL);

      await expect(
        page.getByRole('heading', { name: 'Jonas Jonaitis' }),
      ).toBeVisible();
      await expect(
        page.getByRole('heading', { name: 'Darbo patirtis' }),
      ).toBeVisible();
      await expect(page.getByText('Pardavimų vadyba')).toBeVisible();
      await expect(page.getByText('Vue.js', { exact: true })).toBeVisible();
      await expect(page.getByText('Komandinis darbas')).toBeVisible();
    });

    test('TC-US32-04 shows the CV without downloading it (AC4)', async ({
      page,
    }) => {
      await mockCandidate(page);
      await page.goto(PROFILE_URL);

      await expect(page.getByText('CV ir įgūdžiai')).toBeVisible();
      await expect(page.getByText('Vue.js', { exact: true })).toBeVisible();
      await expect(page.getByRole('link', { name: /atsisiųsti/i })).toHaveCount(
        0,
      );
    });

    test('TC-US32-05 shows the suitability score (AC5)', async ({ page }) => {
      await mockCandidate(page);
      await page.goto(PROFILE_URL);

      await expect(page.getByText('Atitikimas 80 / 100')).toBeVisible();
    });

    test('TC-US32-06 sends a guest to the login page instead of the profile (AC6)', async ({
      page,
    }) => {
      await mockApi(page);
      await page.goto(PROFILE_URL);

      await expect(page).toHaveURL(`/login?redirect=${PROFILE_URL}`);
      await expect(page.getByText('Jonas Jonaitis')).toBeHidden();
    });
  },
);
