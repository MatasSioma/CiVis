import { expect, test } from '@playwright/test';
import { EMPLOYER, INDUSTRIES, mockApi } from './support/mockApi';
import {
  NEW_POSTING_URL,
  POSTING,
  TEAMWORK_REQUIREMENT,
  VUE_REQUIREMENT,
  fillRequiredFields,
  fillRequirement,
} from './support/jobPostingForm';

test.describe(
  'KAN-142 Darbo skelbimas išsaugomas duomenų bazėje',
  {
    tag: '@KAN-142',
    annotation: {
      type: 'issue',
      description: 'https://mif-team-wcvvzu5f.atlassian.net/browse/KAN-142',
    },
  },
  () => {
    test('TC-FR142-01 saves the posting with its required fields (AC1)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);
      await fillRequiredFields(page);
      await page
        .getByLabel('Darbo tipas')
        .selectOption({ label: 'Dalinis etatas' });
      // Requirements are not needed to save, so drop the empty one the form starts with.
      await page.getByRole('button', { name: 'Pašalinti' }).click();
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(page).toHaveURL('/employer');
      expect(api.jobPostings).toMatchObject([
        {
          industry: INDUSTRIES[0].id,
          title: POSTING.title,
          description: POSTING.description,
          job_type: 'part_time',
        },
      ]);
      const row = page.getByRole('row', { name: POSTING.title });
      await expect(row).toContainText(INDUSTRIES[0].name);
      await expect(row).toContainText('Dalinis etatas');
    });

    test('TC-FR142-02 does not save a posting with an empty required field (AC2)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);
      await fillRequiredFields(page);
      await fillRequirement(page, 0, VUE_REQUIREMENT);
      const title = page.getByLabel('Pavadinimas', { exact: true });
      await title.clear();
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      // The browser's required-field check stops the form: it focuses the empty
      // field, marks it invalid and shows its message there (the text depends
      // on the browser language).
      await expect(title).toBeFocused();
      await expect(title.and(page.locator(':invalid'))).toBeVisible();
      await expect(page).toHaveURL(NEW_POSTING_URL);
      expect(api.jobPostingSaves).toBe(0);
    });

    test('TC-FR142-03 saves the requirements and returns to the postings list (AC3)', async ({
      page,
    }) => {
      const api = await mockApi(page, { user: EMPLOYER });
      await page.goto(NEW_POSTING_URL);
      await fillRequiredFields(page);
      await fillRequirement(page, 0, VUE_REQUIREMENT);
      await page.getByRole('button', { name: '+ Pridėti įgūdį' }).click();
      await fillRequirement(page, 1, TEAMWORK_REQUIREMENT);
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(page.getByText('Skelbimas sukurtas.')).toBeVisible();
      await expect(page).toHaveURL('/employer');
      await expect(
        page.getByRole('row', { name: POSTING.title }),
      ).toContainText('Juodraštis');
      expect(api.jobPostings).toMatchObject([
        {
          status: 'draft',
          skills_detail: [VUE_REQUIREMENT, TEAMWORK_REQUIREMENT],
        },
      ]);
    });

    test('TC-FR142-04 shows an error and keeps the form when saving fails (AC4)', async ({
      page,
    }) => {
      const api = await mockApi(page, {
        user: EMPLOYER,
        failJobPostingSaves: true,
      });
      await page.goto(NEW_POSTING_URL);
      await fillRequiredFields(page);
      await fillRequirement(page, 0, VUE_REQUIREMENT);
      await page.getByRole('button', { name: 'Išsaugoti' }).click();

      await expect(
        page.locator('form').getByText('Nepavyko išsaugoti skelbimo.'),
      ).toBeVisible();
      await expect(page).toHaveURL(NEW_POSTING_URL);
      expect(api.jobPostingSaves).toBe(1);
      expect(api.jobPostings).toHaveLength(0);
    });
  },
);
