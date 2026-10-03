import { expect, test, type Page } from '@playwright/test';
import { EMPLOYER, mockApi } from './support/mockApi';
import {
  NEW_POSTING_URL,
  POSTING,
  VUE_REQUIREMENT,
  fillRequiredFields,
  fillRequirement,
  postingDescription,
  requirementDescription,
  requirementIsRequired,
  requirementName,
  requirementType,
  selectIndustry,
} from './support/jobPostingForm';

function requirementCounter(page: Page) {
  return page.getByText(/\d+ \/ 20/);
}

function addRequirementButton(page: Page) {
  return page.getByRole('button', { name: '+ Pridėti įgūdį' });
}

/** A new posting starts with one empty requirement; adds or removes rows to reach `count`. */
async function setRequirementCount(page: Page, count: number) {
  if (count === 0) {
    await page.getByRole('button', { name: 'Pašalinti' }).click();
  }

  for (let rows = 1; rows < count; rows += 1) {
    await addRequirementButton(page).click();
  }
}

/** Clicks "Išsaugoti" and reports whether the posting reached the server within 3 s. */
async function saveReachesServer(page: Page) {
  const saveRequest = page.waitForRequest(
    (request) =>
      request.method() === 'POST' &&
      new URL(request.url()).pathname === '/api/job-postings/',
    { timeout: 3_000 },
  );
  await page.getByRole('button', { name: 'Išsaugoti' }).click();

  return saveRequest.then(
    () => true,
    () => false,
  );
}

test.describe(
  'KAN-14 Kuriant darbo skelbimą, noriu išskirti būtinus reikalavimus',
  {
    tag: '@KAN-14',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-14',
    },
  },
  () => {
    test('TC-US14-01 creates a requirement and then deletes it (AC1)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);
      await fillRequiredFields(page);
      await fillRequirement(page, 0, VUE_REQUIREMENT);
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(page).toHaveURL('/employer');
      expect(api.jobPostings).toMatchObject([
        { skills_detail: [VUE_REQUIREMENT] },
      ]);

      await page
        .getByRole('row', { name: POSTING.title })
        .getByRole('button', { name: 'Redaguoti' })
        .click();
      await page.getByRole('button', { name: 'Pašalinti' }).click();
      await expect(
        page.getByRole('textbox', { name: 'Įgūdis', exact: true }),
      ).toHaveCount(0);
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(page).toHaveURL('/employer');
      expect(api.jobPostings).toMatchObject([{ skills_detail: [] }]);
    });

    for (const count of [0, 1, 18, 19]) {
      test(`TC-US14-02 allows adding a requirement when there are ${count} (AC1, BV2)`, async ({
        page,
      }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto(NEW_POSTING_URL);
        await setRequirementCount(page, count);
        await expect(requirementCounter(page)).toHaveText(`${count} / 20`);

        await addRequirementButton(page).click();

        await expect(requirementCounter(page)).toHaveText(`${count + 1} / 20`);
      });
    }

    test('TC-US14-02 does not allow adding a requirement at the limit of 20 (AC2, BV2)', async ({
      page,
    }) => {
      await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);
      await setRequirementCount(page, 20);

      await expect(requirementCounter(page)).toHaveText('20 / 20');
      await expect(addRequirementButton(page)).toBeDisabled();
    });

    test('TC-US14-03 shows every field of a requirement (AC3)', async ({
      page,
    }) => {
      await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);

      await expect(requirementName(page)).toBeVisible();
      await expect(requirementDescription(page)).toBeVisible();
      await expect(requirementIsRequired(page)).toBeVisible();
      await expect(requirementType(page).getByRole('option')).toHaveText([
        'Hard skill',
        'Soft skill',
        'Darbo patirtis',
      ]);
    });

    // AC4 doesn't say what the validation message reads, so these tests check
    // the outcome it does define: the requirement is not saved.

    test.fail(
      'TC-US14-04 does not save a requirement without a description (AC4)',
      {
        annotation: {
          type: 'defect',
          description: 'A requirement with an empty description is saved.',
        },
      },
      async ({ page }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto(NEW_POSTING_URL);
        await fillRequiredFields(page);
        await requirementName(page).fill(VUE_REQUIREMENT.name);

        expect(await saveReachesServer(page)).toBe(false);
      },
    );

    test.fail(
      'TC-US14-04 does not save a requirement without a type (AC4)',
      {
        annotation: {
          type: 'defect',
          description:
            'The type starts on "Hard skill" and cannot be cleared, so the requirement is saved without the employer choosing a type.',
        },
      },
      async ({ page }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto(NEW_POSTING_URL);
        await fillRequiredFields(page);
        await requirementName(page).fill(VUE_REQUIREMENT.name);
        await requirementDescription(page).fill(VUE_REQUIREMENT.description);

        expect(await saveReachesServer(page)).toBe(false);
      },
    );

    test.fail(
      'TC-US14-05 has every general information field of a posting (AC5)',
      {
        annotation: {
          type: 'defect',
          description: 'The form has no "terminas" (deadline) field.',
        },
      },
      async ({ page }) => {
        await mockApi(page, { user: EMPLOYER });
        await page.goto(NEW_POSTING_URL);
        await expect(
          page.getByLabel('Pavadinimas', { exact: true }),
        ).toBeVisible();

        // Soft checks report every missing field. The form renders all its
        // fields at once, so they don't need to wait long.
        const field = expect.configure({ soft: true, timeout: 1_000 });
        await field(
          page.getByLabel('Veiklos sritis'),
          'sektorius',
        ).toBeVisible();
        await field(
          page.getByLabel('Pavadinimas', { exact: true }),
          'pavadinimas',
        ).toBeVisible();
        await field(page.getByLabel(/terminas/i), 'terminas').toBeVisible();
        await field(postingDescription(page), 'aprašymas').toBeVisible();
        // Full-time, part-time etc. stand for the working hours.
        await field(
          page.getByLabel('Darbo tipas'),
          'darbo valandos',
        ).toBeVisible();
        await field(
          page.getByLabel('Atlyginimas nuo'),
          'atlyginimas',
        ).toBeVisible();
        await field(
          page.getByLabel('Atlyginimas iki'),
          'atlyginimas',
        ).toBeVisible();
        await field(
          page.getByLabel('Darbo vieta').getByRole('option'),
          'lokacija: vietoje arba nuotoliu',
        ).toHaveText(['Vietoje', 'Nuotolinis']);
        await field(
          page.getByLabel('Adresas'),
          'lokacija: adresas',
        ).toBeVisible();
      },
    );

    test('TC-US14-06 does not publish the posting until the required fields are filled (AC6)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);
      await page.getByLabel('Pavadinimas', { exact: true }).fill(POSTING.title);
      await postingDescription(page).fill(POSTING.description);
      await fillRequirement(page, 0, VUE_REQUIREMENT);
      await page
        .getByLabel('Darbo skelbimo būsena')
        .selectOption({ label: 'Atvira' });
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(
        page.locator('form').getByText('Pasirinkite veiklos sritį.'),
      ).toBeVisible();
      expect(api.jobPostingSaves).toBe(0);

      await selectIndustry(page);
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(page).toHaveURL('/employer');
      expect(api.jobPostings).toMatchObject([{ status: 'open' }]);
    });
  },
);
