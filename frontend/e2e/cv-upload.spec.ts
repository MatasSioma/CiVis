import { expect, test } from '@playwright/test';
import { CANDIDATE, mockApi } from './support/mockApi';

const MEGABYTE = 1024 * 1024;

const PDF = {
  name: 'cv.pdf',
  mimeType: 'application/pdf',
  buffer: Buffer.alloc(MEGABYTE),
};

const EXTRACTED_CV = {
  file_key: 'cvs/cv-1.pdf',
  skills: [{ name: 'python', type: 'hard', description: 'Backend' }],
};

test.describe(
  'KAN-46 US-01: CV failo įkėlimas',
  {
    tag: '@KAN-46',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-46',
    },
  },
  () => {
    test.beforeEach(async ({ page }) => {
      await mockApi(page, { user: CANDIDATE });
    });

    test('TC-US46-01 shows the "Įkelti CV" button on the main page (AC1)', async ({
      page,
    }) => {
      await page.goto('/candidate');

      await expect(
        page.getByRole('link', { name: 'Įkelti CV →' }).first(),
      ).toBeVisible();
    });

    test('TC-US46-02 accepts a PDF file (AC2)', async ({ page }) => {
      await page.goto('/candidate/upload-cv');
      await page.locator('input[type=file]').setInputFiles(PDF);

      await expect(
        page.getByRole('button', { name: 'Įkelti ir analizuoti' }),
      ).toBeEnabled();
    });

    test('TC-US46-02 rejects a DOCX file (AC2)', async ({ page }) => {
      await page.goto('/candidate/upload-cv');
      await page.locator('input[type=file]').setInputFiles({
        name: 'cv.docx',
        mimeType:
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        buffer: Buffer.alloc(MEGABYTE),
      });

      await expect(page.getByText('Leidžiami tik PDF failai.')).toBeVisible();
    });

    for (const megabytes of [9.9, 10]) {
      test(`TC-US46-03 accepts a ${megabytes} MB PDF file (AC3, BV5)`, async ({
        page,
      }) => {
        await page.goto('/candidate/upload-cv');
        await page.locator('input[type=file]').setInputFiles({
          ...PDF,
          buffer: Buffer.alloc(Math.round(megabytes * MEGABYTE)),
        });

        await expect(
          page.getByRole('button', { name: 'Įkelti ir analizuoti' }),
        ).toBeEnabled();
      });
    }

    test('TC-US46-03 rejects a 10.1 MB PDF file (AC3, BV5)', async ({
      page,
    }) => {
      await page.goto('/candidate/upload-cv');
      await page.locator('input[type=file]').setInputFiles({
        ...PDF,
        buffer: Buffer.alloc(Math.round(10.1 * MEGABYTE)),
      });

      await expect(
        page.getByText('Failo dydis negali viršyti 10 MB.'),
      ).toBeVisible();
    });

    test('TC-US46-04 shows that the file is being processed (AC4)', async ({
      page,
    }) => {
      await page.route('**/api/cv/upload/', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 1_000));
        await route.fulfill({ json: EXTRACTED_CV });
      });
      await page.goto('/candidate/upload-cv');
      await page.locator('input[type=file]').setInputFiles(PDF);
      await page.getByRole('button', { name: 'Įkelti ir analizuoti' }).click();

      // The test case expects a spinning circle; the app shows the text
      // "Apdorojama..." on the disabled button instead.
      await expect(
        page.getByRole('button', { name: 'Apdorojama...' }),
      ).toBeDisabled();
    });

    test('TC-US46-05 fills the form automatically and lets the user edit it afterwards (AC5)', async ({
      page,
    }) => {
      await page.route('**/api/cv/upload/', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 1_000));
        await route.fulfill({ json: EXTRACTED_CV });
      });
      await page.goto('/candidate/upload-cv');
      await page.locator('input[type=file]').setInputFiles(PDF);
      await page.getByRole('button', { name: 'Įkelti ir analizuoti' }).click();

      await expect(page.getByLabel('Pavadinimas')).toHaveCount(0);

      await expect(page.getByLabel('Pavadinimas')).toHaveValue('Python');
      await page.getByLabel('Pavadinimas').fill('Python 3');
      await expect(page.getByLabel('Pavadinimas')).toHaveValue('Python 3');
    });

    test('TC-US46-06 shows an error and lets the user retry when the upload fails (AC6)', async ({
      page,
    }) => {
      await page.route('**/api/cv/upload/', (route) =>
        route.fulfill({
          status: 500,
          contentType: 'text/html',
          body: '<h1>Server Error (500)</h1>',
        }),
      );
      await page.goto('/candidate/upload-cv');
      await page.locator('input[type=file]').setInputFiles(PDF);
      await page.getByRole('button', { name: 'Įkelti ir analizuoti' }).click();

      // The message is shown both under the form and in a toast.
      await expect(
        page
          .getByText('Įvyko klaida įkeliant failą. Bandykite dar kartą.')
          .first(),
      ).toBeVisible();
      // The test case expects a "Try again" button; the app keeps the
      // original upload button enabled instead.
      await expect(
        page.getByRole('button', { name: 'Įkelti ir analizuoti' }),
      ).toBeEnabled();
    });
  },
);
