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

    test.fail(
      'TC-US46-02 rejects a DOCX file (AC2)',
      {
        annotation: {
          type: 'defect',
          description:
            'The DOCX is rejected, but with "Leidžiami tik PDF failai." instead of "Please upload files in PDF format".',
        },
      },
      async ({ page }) => {
        await page.goto('/candidate/upload-cv');
        await page.locator('input[type=file]').setInputFiles({
          name: 'cv.docx',
          mimeType:
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          buffer: Buffer.alloc(MEGABYTE),
        });

        await expect(
          page.getByText('Please upload files in PDF format'),
        ).toBeVisible();
      },
    );

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

    test.fail(
      'TC-US46-03 rejects a 10.1 MB PDF file (AC3, BV5)',
      {
        annotation: {
          type: 'defect',
          description:
            'The file is rejected, but with "Failo dydis negali viršyti 10 MB." instead of "Maximum allowed file size <= 10MB".',
        },
      },
      async ({ page }) => {
        await page.goto('/candidate/upload-cv');
        await page.locator('input[type=file]').setInputFiles({
          ...PDF,
          buffer: Buffer.alloc(Math.round(10.1 * MEGABYTE)),
        });

        await expect(
          page.getByText('Maximum allowed file size <= 10MB'),
        ).toBeVisible();
      },
    );

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

    test.fail(
      'TC-US46-06 shows an error and a "Try again" button when the upload fails (AC6)',
      {
        annotation: {
          type: 'defect',
          description:
            'The error reads "Įvyko klaida įkeliant failą. Bandykite dar kartą." and the button stays "Įkelti ir analizuoti" instead of changing to "Try again".',
        },
      },
      async ({ page }) => {
        await page.route('**/api/cv/upload/', (route) =>
          route.fulfill({
            status: 500,
            contentType: 'text/html',
            body: '<h1>Server Error (500)</h1>',
          }),
        );
        await page.goto('/candidate/upload-cv');
        await page.locator('input[type=file]').setInputFiles(PDF);
        await page
          .getByRole('button', { name: 'Įkelti ir analizuoti' })
          .click();

        await expect(
          page.getByText('Failed to upload the file. Please try again'),
        ).toBeVisible();
        await expect(
          page.getByRole('button', { name: 'Try again' }),
        ).toBeVisible();
      },
    );
  },
);
