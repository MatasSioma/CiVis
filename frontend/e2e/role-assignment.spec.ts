import { expect, test } from '@playwright/test';
import { mockApi } from './support/mockApi';

test.describe(
  'KAN-92 Sistema turi priskirti vartotojui rolę',
  {
    tag: '@KAN-92',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-92',
    },
  },
  () => {
    test.beforeEach(async ({ page }) => {
      await mockApi(page);
      await page.goto('/signup');
      await page.getByPlaceholder('Įveskite vardą').fill('Jonas');
      await page.getByPlaceholder('Įveskite pavardę').fill('Jonaitis');
      await page.getByPlaceholder('vardas@pastas.lt').fill('jonas@example.com');
    });

    test('TC-FR92-01 candidate registration continues with the candidate role (AC1)', async ({
      page,
    }) => {
      await page.getByRole('button', { name: 'Darbo ieškantis asmuo' }).click();
      await page.getByLabel('Gimimo data').fill('1990-01-01');
      await page.getByRole('button', { name: 'Tęsti' }).click();

      await expect(page).toHaveURL('/gateway');
      await page.getByText('Peržiūrėti įvestus duomenis').click();
      await expect(page.getByText('Darbo ieškantis asmuo')).toBeVisible();
    });

    test('TC-FR92-01 employer registration continues with the employer role (AC1)', async ({
      page,
    }) => {
      await page.getByRole('button', { name: 'Darbdavys' }).click();
      await page
        .getByPlaceholder('Įveskite įmonės pavadinimą')
        .fill('UAB Pavyzdys');
      await page.getByRole('button', { name: 'Tęsti' }).click();

      await expect(page).toHaveURL('/gateway');
      await page.getByText('Peržiūrėti įvestus duomenis').click();
      await expect(page.getByText('Darbdavys')).toBeVisible();
    });
  },
);
