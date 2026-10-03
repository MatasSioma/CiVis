import { expect, test } from '@playwright/test';
import { mockApi } from './support/mockApi';

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test('redirects guests from protected pages to login', async ({ page }) => {
  await page.goto('/candidate');

  await expect(page).toHaveURL('/login?redirect=/candidate');
  await expect(
    page.getByRole('heading', { name: 'Prisijungimas per Semėno vartus' }),
  ).toBeVisible();
});

test('requires choosing a user type before continuing', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Tęsti į Semėno vartus' }).click();

  await expect(
    page.locator('form').getByText('Pasirinkite naudotojo tipą.'),
  ).toBeVisible();
  await expect(page).toHaveURL('/login');
});

test('continues to the gateway after choosing a user type', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Darbo ieškantis asmuo' }).click();
  await page.getByRole('button', { name: 'Tęsti į Semėno vartus' }).click();

  await expect(page).toHaveURL('/gateway');
  await expect(
    page.getByRole('heading', { level: 1, name: 'Prisijungimas', exact: true }),
  ).toBeVisible();
});
