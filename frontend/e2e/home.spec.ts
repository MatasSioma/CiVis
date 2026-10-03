import { expect, test } from '@playwright/test';
import { mockApi } from './support/mockApi';

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test.describe(
  'KAN-151 FR-04: Neprisijungusiam vartotojui rodomas filtruojamas, rūšiuojamas darbo pozicijų sąrašas',
  {
    tag: '@KAN-151',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-151',
    },
  },
  () => {
    test('TC-FR151-01 shows the landing page with open job postings without logging in (AC1)', async ({
      page,
    }) => {
      await page.goto('/');

      await expect(page).toHaveTitle('CiVis');
      await expect(
        page.getByRole('heading', {
          level: 1,
          name: 'Darbo paieška ir kandidatų atranka vienoje vietoje',
        }),
      ).toBeVisible();
      await expect(
        page.getByRole('cell', { name: 'Frontend programuotojas' }),
      ).toBeVisible();
      await expect(
        page.getByRole('cell', { name: 'Backend programuotojas' }),
      ).toBeVisible();
    });

    test('TC-FR151-03 shows the main posting information without a match percentage (AC2)', async ({
      page,
    }) => {
      await page.goto('/');

      const posting = page.getByRole('row', {
        name: 'Frontend programuotojas',
      });
      await expect(posting).toContainText('UAB Pavyzdys');
      await expect(posting).toContainText('Pilnas etatas');
      await expect(posting).toContainText('Nuotolinis');
      await expect(posting).toContainText('2000 – 3000 €');
      await expect(page.getByText(/\d+\s*%/)).toHaveCount(0);
      await expect(
        page.getByRole('columnheader', { name: 'Atitikimas' }),
      ).toHaveCount(0);
    });

    test('TC-FR151-04 shows only the postings that match the filter (AC3)', async ({
      page,
    }) => {
      await page.goto('/');
      await page.getByPlaceholder('Ieškoti pagal pavadinimą').fill('Backend');

      await expect(page).toHaveURL(/\?search=Backend$/);
      await expect(
        page.getByRole('cell', { name: 'Backend programuotojas' }),
      ).toBeVisible();
      await expect(
        page.getByRole('cell', { name: 'Frontend programuotojas' }),
      ).toBeHidden();
    });

    test.fail(
      'TC-FR151-04 shows "No jobs match your filters" when nothing matches (AC8)',
      {
        annotation: {
          type: 'defect',
          description:
            'The empty list reads "Pagal pasirinktus filtrus skelbimų nerasta." instead of "No jobs match your filters".',
        },
      },
      async ({ page }) => {
        await page.goto('/');
        await page
          .getByPlaceholder('Ieškoti pagal pavadinimą')
          .fill('Pardavėjas');

        await expect(
          page.getByText('No jobs match your filters'),
        ).toBeVisible();
      },
    );

    test('TC-FR151-05 sorts the postings by the newest first by default (AC4)', async ({
      page,
    }) => {
      await page.goto('/');

      await expect(page.getByLabel('Rikiuoti')).toHaveValue('-updated_at');
    });

    test('TC-FR151-05 sorts the postings by salary when chosen (AC4)', async ({
      page,
    }) => {
      await page.goto('/');
      const request = page.waitForRequest(/ordering=-salary_max/);
      await page
        .getByLabel('Rikiuoti')
        .selectOption({ label: 'Pagal atlyginimą (didžiausias viršuje)' });

      await request;
      await expect(page).toHaveURL(/ordering=-salary_max/);
    });

    test('TC-FR151-05 does not offer sorting by match (AC4)', async ({
      page,
    }) => {
      await page.goto('/');

      await expect(
        page.getByLabel('Rikiuoti').getByRole('option', { name: /atitikim/i }),
      ).toHaveCount(0);
    });

    test.skip(
      'TC-FR151-06 refreshes the list smoothly when the filters change (AC5)',
      {
        annotation: {
          type: 'skip',
          description: 'AC5 "sklandžiai" has no measurable criterion.',
        },
      },
      async () => {},
    );

    test.skip(
      'TC-FR151-07 does not let a guest apply for a job (AC6)',
      {
        annotation: {
          type: 'skip',
          description:
            'The landing page has no "Apply" button; the server side is tested in test_public_job_postings.py.',
        },
      },
      async () => {},
    );

    test.fail(
      'TC-FR151-09 shows an error and a "Try again" button when the postings fail to load (AC8)',
      {
        annotation: {
          type: 'defect',
          description:
            'A failed load only shows the toast "Nepavyko įkelti darbo skelbimų."; there is no "Try again" button.',
        },
      },
      async ({ page }) => {
        await page.route(
          (url) => url.pathname === '/api/public/job-postings/',
          (route) =>
            route.fulfill({
              status: 500,
              contentType: 'text/html',
              body: '<h1>Server Error (500)</h1>',
            }),
        );
        await page.goto('/');

        await expect(
          page.getByText('Failed to load jobs. Please try again'),
        ).toBeVisible();
        await expect(
          page.getByRole('button', { name: 'Try again' }),
        ).toBeVisible();
      },
    );
  },
);

test('shows the not found page for unknown routes', async ({ page }) => {
  await page.goto('/does-not-exist');

  await expect(
    page.getByRole('heading', { name: 'Puslapis nerastas' }),
  ).toBeVisible();

  await page.getByRole('link', { name: 'Back to home' }).click();

  await expect(page).toHaveURL('/');
});
