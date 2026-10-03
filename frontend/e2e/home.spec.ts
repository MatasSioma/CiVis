import { expect, test } from '@playwright/test';
import { mockApi } from './support/mockApi';

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test('shows the landing page with open job postings', async ({ page }) => {
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

test('filters job postings by search query', async ({ page }) => {
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

test('shows the not found page for unknown routes', async ({ page }) => {
  await page.goto('/does-not-exist');

  await expect(
    page.getByRole('heading', { name: 'Puslapis nerastas' }),
  ).toBeVisible();

  await page.getByRole('link', { name: 'Back to home' }).click();

  await expect(page).toHaveURL('/');
});
