import type { Page } from '@playwright/test';
import { INDUSTRIES } from './mockApi';

export const NEW_POSTING_URL = '/employer/job-postings/new';

export const POSTING = {
  title: 'Frontend programuotojas',
  description: 'Kurti ir prižiūrėti įmonės interneto aplikacijas.',
};

/** A requirement as the job posting form sends it to the API. */
export interface Requirement {
  name: string;
  type: 'hard' | 'soft' | 'experience';
  description: string;
  is_required: boolean;
}

export const VUE_REQUIREMENT: Requirement = {
  name: 'Vue.js',
  type: 'hard',
  description: 'Komponentų kūrimas su Composition API',
  is_required: true,
};

export const TEAMWORK_REQUIREMENT: Requirement = {
  name: 'Komandinis darbas',
  type: 'soft',
  description: 'Darbas Scrum komandoje',
  is_required: false,
};

/** The posting's own description; every requirement has an "Aprašymas" too. */
export function postingDescription(page: Page) {
  return page.getByRole('textbox', { name: 'Aprašymas', exact: true }).first();
}

// Fields of requirement `index` (0-based) in the "Reikalavimai ir įgūdžiai"
// list. They're found by accessible name: the <label> around a <select> also
// holds the option texts, so getByLabel can't match "Tipas" exactly.

export function requirementName(page: Page, index = 0) {
  return page.getByRole('textbox', { name: 'Įgūdis', exact: true }).nth(index);
}

export function requirementType(page: Page, index = 0) {
  return page.getByRole('combobox', { name: 'Tipas', exact: true }).nth(index);
}

export function requirementDescription(page: Page, index = 0) {
  return page
    .getByRole('textbox', { name: 'Aprašymas', exact: true })
    .nth(index + 1);
}

export function requirementIsRequired(page: Page, index = 0) {
  return page.getByRole('checkbox', { name: 'Privalomas' }).nth(index);
}

export async function selectIndustry(page: Page, name = INDUSTRIES[0].name) {
  await page.getByLabel('Veiklos sritis').fill(name);
  await page.getByRole('listitem').filter({ hasText: name }).click();
}

/** Fills the fields the form requires: title, sector and description. */
export async function fillRequiredFields(page: Page) {
  await page.getByLabel('Pavadinimas', { exact: true }).fill(POSTING.title);
  await selectIndustry(page);
  await postingDescription(page).fill(POSTING.description);
}

export async function fillRequirement(
  page: Page,
  index: number,
  requirement: Requirement,
) {
  await requirementName(page, index).fill(requirement.name);
  await requirementType(page, index).selectOption(requirement.type);
  await requirementDescription(page, index).fill(requirement.description);
  await requirementIsRequired(page, index).setChecked(requirement.is_required);
}
