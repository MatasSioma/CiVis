import { expect, test } from '@playwright/test';
import { CANDIDATE, CV, EMPLOYER, mockApi } from './support/mockApi';

const SKILL = CV.skills[0].name;

// Every executed test case needs a screenshot of its result in the report.
test.use({ screenshot: 'on' });

test.describe(
  'KAN-28 Naudotojas gali ištrinti savo CV',
  {
    tag: '@KAN-28',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-28',
    },
  },
  () => {
    test('TC-US28-01 shows the "Ištrinti CV" button on the profile page (AC1)', async ({
      page,
    }) => {
      await mockApi(page, { user: CANDIDATE, cv: CV });
      await page.goto('/candidate');
      await page.getByRole('link', { name: 'Peržiūrėti CV →' }).click();

      await expect(page).toHaveURL('/candidate/my-cv');
      const deleteButton = page.getByRole('button', { name: 'Ištrinti CV' });
      await expect(deleteButton).toBeVisible();
      await expect(deleteButton).toBeEnabled();
    });

    test('TC-US28-02 asks to confirm the deletion (AC2)', async ({ page }) => {
      const api = await mockApi(page, { user: CANDIDATE, cv: CV });
      await page.goto('/candidate/my-cv');
      await page.getByRole('button', { name: 'Ištrinti CV' }).click();

      await expect(
        page.getByRole('heading', { name: 'Ar tikrai norite ištrinti CV?' }),
      ).toBeVisible();
      await expect(
        page.getByRole('button', { name: 'Atšaukti' }),
      ).toBeVisible();
      await expect(
        page.getByRole('button', { name: 'Ištrinti', exact: true }),
      ).toBeVisible();
      expect(api.cvDeleteRequests).toBe(0);
    });

    test('TC-US28-03 deletes the CV and its data after confirming (AC3)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: CANDIDATE, cv: CV });
      await page.goto('/candidate/my-cv');
      await page.getByRole('button', { name: 'Ištrinti CV' }).click();
      await page.getByRole('button', { name: 'Ištrinti', exact: true }).click();

      await expect(page.getByText('CV ištrintas.')).toBeVisible();
      await expect(page).toHaveURL('/candidate');
      expect(api.cvDeleteRequests).toBe(1);
      await expect(page.getByText('CV dar neįkeltas.')).toBeVisible();

      await page.goto('/candidate/my-cv');

      await expect(page.getByText('Dar neįkėlėte CV.')).toBeVisible();
      await expect(page.getByText(SKILL, { exact: true })).toBeHidden();
      await expect(
        page.getByRole('button', { name: 'Ištrinti CV' }),
      ).toHaveCount(0);
    });

    test('TC-US28-04 hides the deleted CV from employers (AC4)', async ({
      page,
    }) => {
      // The candidate has already deleted the CV, and with it the application.
      await mockApi(page, { user: EMPLOYER });
      await page.goto('/employer/job-postings/1/applications/application-1');

      await expect(page.getByText('Paraiška nerasta.')).toBeVisible();
      await expect(page.getByText('CV ir įgūdžiai')).toBeHidden();
      await expect(page.getByText(SKILL, { exact: true })).toBeHidden();
    });

    test('TC-US28-05 keeps the CV when the deletion is cancelled (AC5)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: CANDIDATE, cv: CV });
      await page.goto('/candidate/my-cv');
      await page.getByRole('button', { name: 'Ištrinti CV' }).click();
      await page.getByRole('button', { name: 'Atšaukti' }).click();

      await expect(
        page.getByRole('heading', { name: 'Ar tikrai norite ištrinti CV?' }),
      ).toBeHidden();
      expect(api.cvDeleteRequests).toBe(0);

      await page.reload();

      await expect(
        page.getByRole('button', { name: 'Ištrinti CV' }),
      ).toBeVisible();
      await expect(page.getByText(SKILL, { exact: true })).toBeVisible();
    });

    test('TC-US28-06 cannot delete a CV that was not uploaded (AC6)', async ({
      page,
    }) => {
      await mockApi(page, { user: CANDIDATE });
      await page.goto('/candidate/my-cv');

      await expect(page.getByText('Dar neįkėlėte CV.')).toBeVisible();
      // The test case expects a disabled button; the app hides it instead,
      // which still meets AC6.
      await expect(
        page.getByRole('button', { name: 'Ištrinti CV' }),
      ).toHaveCount(0);
      await expect(
        page.getByRole('link', { name: 'Įkelti CV →' }),
      ).toBeVisible();
    });
  },
);
