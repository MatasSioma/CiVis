<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '@/stores/auth';
import { useToasts } from '@/stores/toasts';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { cvApi } from '@/services/cv';
import { ApiError } from '@/services/api';
import DashboardCard from '@/components/DashboardCard.vue';
import {
  JOB_TYPE_LABELS,
  WORKPLACE_TYPE_LABELS,
  type JobType,
  type WorkplaceType,
} from '@/services/employer';
import {
  CANDIDATE_POSTING_ORDERING_OPTIONS,
  CANDIDATE_POSTING_PAGE_SIZE,
  DEFAULT_CANDIDATE_POSTING_ORDERING,
  candidateApplicationApi,
  candidatePostingApi,
  type CandidateApplication,
  type CandidateJobPosting,
  type CandidatePostingFilters,
  type CandidatePostingOrdering,
} from '@/services/candidate';

const { state } = useAuth();
const { showToast } = useToasts();
const route = useRoute();
const router = useRouter();

const user = computed(() => state.user);

type CVStatus = 'loading' | 'uploaded' | 'missing';
const cvStatus = ref<CVStatus>('loading');

function formatDate(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('lt-LT', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatShortDate(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('lt-LT');
}

function formatSalary(min: number | null, max: number | null): string {
  if (min == null && max == null) return '—';
  if (min != null && max != null) return `${min} – ${max} €`;
  if (min != null) return `nuo ${min} €`;
  return `iki ${max} €`;
}

function vocative(name: string): string {
  if (name.endsWith('s')) return `${name.slice(0, -1)}i`;
  if (name.endsWith('ė')) return `${name.slice(0, -1)}e`;
  return name;
}

const ALLOWED_ORDERINGS = CANDIDATE_POSTING_ORDERING_OPTIONS.map((o) => o.value);
const JOB_TYPE_VALUES: JobType[] = [
  'full_time',
  'part_time',
  'contract',
  'internship',
  'temporary',
];
const WORKPLACE_TYPE_VALUES: WorkplaceType[] = ['on_site', 'remote'];

function parsePage(raw: unknown): number {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 1 ? Math.floor(parsed) : 1;
}

function parseOrdering(raw: unknown): CandidatePostingOrdering {
  const value = Array.isArray(raw) ? raw[0] : raw;
  return ALLOWED_ORDERINGS.includes(value as CandidatePostingOrdering)
    ? (value as CandidatePostingOrdering)
    : DEFAULT_CANDIDATE_POSTING_ORDERING;
}

function parseString(raw: unknown): string {
  const value = Array.isArray(raw) ? raw[0] : raw;
  return typeof value === 'string' ? value : '';
}

function parseJobType(raw: unknown): JobType | '' {
  const value = parseString(raw);
  return JOB_TYPE_VALUES.includes(value as JobType) ? (value as JobType) : '';
}

function parseWorkplaceType(raw: unknown): WorkplaceType | '' {
  const value = parseString(raw);
  return WORKPLACE_TYPE_VALUES.includes(value as WorkplaceType)
    ? (value as WorkplaceType)
    : '';
}

function parseMinSalary(raw: unknown): number | null {
  const value = parseString(raw);
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : null;
}

const postings = ref<CandidateJobPosting[]>([]);
const postingsTotal = ref(0);
const postingsPage = ref(1);
const postingsNext = ref<string | null>(null);
const postingsPrevious = ref<string | null>(null);
const isPostingsLoading = ref(true);

const filters = reactive<{
  search: string;
  job_type: JobType | '';
  workplace_type: WorkplaceType | '';
  min_salary: number | null;
  location: string;
  ordering: CandidatePostingOrdering;
}>({
  search: '',
  job_type: '',
  workplace_type: '',
  min_salary: null,
  location: '',
  ordering: DEFAULT_CANDIDATE_POSTING_ORDERING,
});

const searchInput = ref('');
const locationInput = ref('');
const minSalaryInput = ref<number | null>(null);

let searchDebounce: ReturnType<typeof setTimeout> | null = null;
let locationDebounce: ReturnType<typeof setTimeout> | null = null;
let minSalaryDebounce: ReturnType<typeof setTimeout> | null = null;

const totalPages = computed(() => {
  if (postingsTotal.value === 0) return 1;
  return Math.ceil(postingsTotal.value / CANDIDATE_POSTING_PAGE_SIZE);
});

const applyingId = ref<string | null>(null);

const applications = ref<CandidateApplication[]>([]);
const isApplicationsLoading = ref(true);
const cancellingApplicationId = ref<string | null>(null);

async function loadApplications() {
  isApplicationsLoading.value = true;

  try {
    applications.value = await candidateApplicationApi.list();
  } catch {
    showToast('Nepavyko įkelti paraiškų.', 'error');
  } finally {
    isApplicationsLoading.value = false;
  }
}

async function cancelApplication(application: CandidateApplication) {
  if (
    !window.confirm(
      `Ar tikrai norite atšaukti paraišką į „${application.job_posting_title}“?`,
    )
  ) {
    return;
  }

  cancellingApplicationId.value = application.id;

  try {
    await candidateApplicationApi.cancel(application.id);
    showToast('Paraiška atšaukta.', 'success');
    await Promise.all([
      loadApplications(),
      loadPostings(postingsPage.value, filters.ordering, {
        search: filters.search,
        job_type: filters.job_type,
        workplace_type: filters.workplace_type,
        min_salary: filters.min_salary,
        location: filters.location,
      }),
    ]);
  } catch {
    showToast('Nepavyko atšaukti paraiškos.', 'error');
  } finally {
    cancellingApplicationId.value = null;
  }
}

async function loadPostings(
  page: number,
  ordering: CandidatePostingOrdering,
  current: CandidatePostingFilters,
) {
  isPostingsLoading.value = true;

  try {
    const data = await candidatePostingApi.list(page, ordering, current);
    postings.value = data.results;
    postingsTotal.value = data.count;
    postingsNext.value = data.next;
    postingsPrevious.value = data.previous;
    postingsPage.value = page;
  } catch {
    showToast('Nepavyko įkelti darbo skelbimų.', 'error');
  } finally {
    isPostingsLoading.value = false;
  }
}

function syncFromRoute() {
  filters.search = parseString(route.query.search);
  filters.job_type = parseJobType(route.query.job_type);
  filters.workplace_type = parseWorkplaceType(route.query.workplace_type);
  filters.min_salary = parseMinSalary(route.query.min_salary);
  filters.location = parseString(route.query.location);
  filters.ordering = parseOrdering(route.query.ordering);

  searchInput.value = filters.search;
  locationInput.value = filters.location;
  minSalaryInput.value = filters.min_salary;
}

async function updateQuery(patch: Record<string, string | null>) {
  const nextQuery = { ...route.query };
  delete nextQuery.page;

  for (const [key, value] of Object.entries(patch)) {
    if (value == null || value === '') {
      delete nextQuery[key];
    } else {
      nextQuery[key] = value;
    }
  }

  await router.push({ query: nextQuery });
}

async function goToPage(page: number) {
  const target = page >= 1 ? page : 1;
  const nextQuery = { ...route.query };

  if (target === 1) {
    delete nextQuery.page;
  } else {
    nextQuery.page = String(target);
  }

  await router.push({ query: nextQuery });
}

async function setOrdering(value: CandidatePostingOrdering) {
  await updateQuery({
    ordering:
      value === DEFAULT_CANDIDATE_POSTING_ORDERING ? null : value,
  });
}

async function setJobType(value: JobType | '') {
  await updateQuery({ job_type: value || null });
}

async function setWorkplaceType(value: WorkplaceType | '') {
  await updateQuery({ workplace_type: value || null });
}

function onSearchInput(value: string) {
  searchInput.value = value;
  if (searchDebounce) clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    void updateQuery({ search: value.trim() || null });
  }, 300);
}

function onLocationInput(value: string) {
  locationInput.value = value;
  if (locationDebounce) clearTimeout(locationDebounce);
  locationDebounce = setTimeout(() => {
    void updateQuery({ location: value.trim() || null });
  }, 300);
}

function onMinSalaryInput(raw: string) {
  const parsed = Number(raw);
  const value =
    raw === '' || !Number.isFinite(parsed) || parsed <= 0
      ? null
      : Math.floor(parsed);
  minSalaryInput.value = value;
  if (minSalaryDebounce) clearTimeout(minSalaryDebounce);
  minSalaryDebounce = setTimeout(() => {
    void updateQuery({ min_salary: value != null ? String(value) : null });
  }, 300);
}

async function clearFilters() {
  await router.push({ query: {} });
}

async function applyTo(posting: CandidateJobPosting) {
  if (cvStatus.value !== 'uploaded' || posting.has_applied) return;

  applyingId.value = posting.id;

  try {
    await candidatePostingApi.apply(posting.id);
    showToast('Paraiška pateikta.', 'success');
    await Promise.all([
      loadApplications(),
      loadPostings(postingsPage.value, filters.ordering, {
        search: filters.search,
        job_type: filters.job_type,
        workplace_type: filters.workplace_type,
        min_salary: filters.min_salary,
        location: filters.location,
      }),
    ]);
  } catch (error) {
    let message = 'Nepavyko pateikti paraiškos.';
    if (error instanceof ApiError && error.status === 400) {
      message =
        (error.details && typeof error.details === 'object'
          ? Object.values(error.details).flat().join(' ')
          : error.message) || message;
    }
    showToast(message, 'error');
  } finally {
    applyingId.value = null;
  }
}

function matchScoreColorClasses(score: number): string {
  if (score >= 70) return 'bg-primary text-attention';
  if (score >= 40) return 'bg-amber-100 text-amber-800';
  return 'bg-red-100 text-red-700';
}

function workplaceLabel(posting: CandidateJobPosting): string {
  if (posting.workplace_type === 'remote') {
    return WORKPLACE_TYPE_LABELS.remote;
  }
  return `${WORKPLACE_TYPE_LABELS.on_site} — ${posting.location || '—'}`;
}

watch(
  () => [
    route.query.page,
    route.query.ordering,
    route.query.search,
    route.query.job_type,
    route.query.workplace_type,
    route.query.min_salary,
    route.query.location,
  ],
  () => {
    syncFromRoute();
    void loadPostings(parsePage(route.query.page), filters.ordering, {
      search: filters.search,
      job_type: filters.job_type,
      workplace_type: filters.workplace_type,
      min_salary: filters.min_salary,
      location: filters.location,
    });
  },
);

onMounted(async () => {
  syncFromRoute();
  try {
    await cvApi.getMyCV();
    cvStatus.value = 'uploaded';
  } catch (error) {
    cvStatus.value =
      error instanceof ApiError && error.status === 404 ? 'missing' : 'missing';
  }

  void loadApplications();
  void loadPostings(parsePage(route.query.page), filters.ordering, {
    search: filters.search,
    job_type: filters.job_type,
    workplace_type: filters.workplace_type,
    min_salary: filters.min_salary,
    location: filters.location,
  });
});
</script>

<template>
  <section v-if="user" class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Darbo ieškančio asmens paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ user.first_name ? vocative(user.first_name) : user.email }}
      </h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <DashboardCard title="Profilis">
        <dl class="mt-3 space-y-2 text-sm">
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">
              Vardas, pavardė
            </dt>
            <dd class="text-gray-900">
              {{ user.first_name }} {{ user.last_name }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">El. paštas</dt>
            <dd class="text-gray-900">{{ user.email }}</dd>
          </div>
          <div v-if="user.date_of_birth">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Gimimo data</dt>
            <dd class="text-gray-900">{{ formatDate(user.date_of_birth) }}</dd>
          </div>
        </dl>
      </DashboardCard>

      <DashboardCard title="CV">
        <p v-if="cvStatus === 'loading'" class="mt-3 text-sm text-gray-500">
          Kraunama...
        </p>
        <template v-else-if="cvStatus === 'uploaded'">
          <p class="mt-3 text-sm text-gray-700">CV įkeltas.</p>
          <RouterLink
            class="bg-attention hover:bg-secondary mt-4 inline-block cursor-pointer rounded-md px-4 py-2 text-sm font-semibold text-white transition"
            :to="{ name: ROUTE_NAMES.MY_CV }">
            Peržiūrėti CV →
          </RouterLink>
        </template>
        <template v-else>
          <p class="mt-3 text-sm text-gray-700">CV dar neįkeltas.</p>
          <RouterLink
            class="bg-attention hover:bg-secondary mt-4 inline-block cursor-pointer rounded-md px-4 py-2 text-sm font-semibold text-white transition"
            :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
            Įkelti CV →
          </RouterLink>
        </template>
      </DashboardCard>

      <DashboardCard title="Paraiškos">
        <p v-if="isApplicationsLoading" class="mt-3 text-sm text-gray-500">
          Kraunama...
        </p>
        <p
          v-else-if="applications.length === 0"
          class="mt-3 text-sm text-gray-700">
          Dar nepateikėte paraiškų.
        </p>
        <ul v-else class="mt-3 space-y-2">
          <li
            v-for="application in applications"
            :key="application.id"
            class="rounded-md border border-gray-200 bg-background/40 p-3">
            <div class="flex items-start justify-between gap-2">
              <RouterLink
                class="text-sm font-medium text-gray-950 hover:underline"
                :to="{
                  name: ROUTE_NAMES.CANDIDATE_JOB_POSTING,
                  params: { id: application.job_posting },
                }">
                {{ application.job_posting_title }}
              </RouterLink>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="matchScoreColorClasses(application.match_score)">
                {{ application.match_score }} / 100
              </span>
            </div>
            <div class="mt-1 flex items-center justify-between gap-2">
              <p class="text-xs text-gray-500">{{ application.company_name }}</p>
              <button
                class="rounded-md bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
                :disabled="cancellingApplicationId === application.id"
                type="button"
                @click="cancelApplication(application)">
                {{
                  cancellingApplicationId === application.id
                    ? 'Atšaukiama...'
                    : 'Atšaukti'
                }}
              </button>
            </div>
          </li>
        </ul>
      </DashboardCard>
    </div>

    <section
      v-if="cvStatus === 'missing'"
      class="flex flex-col items-center gap-3 rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center shadow-sm">
      <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
        Darbo pasiūlymai
      </p>
      <h2 class="text-lg font-semibold text-gray-950">
        Įkelkite CV, kad matytumėte darbo skelbimus
      </h2>
      <p class="max-w-md text-sm text-gray-600">
        Įkėlę CV, čia matysite atvirus skelbimus su atitikimo įvertinimu pagal jūsų
        įgūdžius ir galėsite pateikti paraiškas.
      </p>
      <RouterLink
        class="mt-2 inline-block rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary"
        :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
        Įkelti CV →
      </RouterLink>
    </section>

    <section
      v-else-if="cvStatus === 'uploaded'"
      class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
            Darbo pasiūlymai
          </p>
          <h2 class="mt-1 text-lg font-semibold text-gray-950">
            Atviri darbo skelbimai
            <span v-if="postingsTotal > 0" class="ml-1 text-sm font-normal text-gray-500">
              ({{ postingsTotal }})
            </span>
          </h2>
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <span class="text-xs font-medium text-gray-600">Rikiuoti:</span>
          <select
            :value="filters.ordering"
            class="h-9 rounded-md border border-gray-300 bg-white px-2 text-sm text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            @change="setOrdering(($event.target as HTMLSelectElement).value as CandidatePostingOrdering)">
            <option
              v-for="opt in CANDIDATE_POSTING_ORDERING_OPTIONS"
              :key="opt.value"
              :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <label class="block">
          <span class="text-xs font-medium text-gray-600">Paieška</span>
          <input
            :value="searchInput"
            class="mt-1 h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Ieškoti pagal pavadinimą"
            type="search"
            @input="onSearchInput(($event.target as HTMLInputElement).value)" />
        </label>
        <label class="block">
          <span class="text-xs font-medium text-gray-600">Darbo tipas</span>
          <select
            :value="filters.job_type"
            class="mt-1 h-9 w-full rounded-md border border-gray-300 bg-white px-2 text-sm text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            @change="setJobType(($event.target as HTMLSelectElement).value as JobType | '')">
            <option value="">Visi</option>
            <option v-for="jt in JOB_TYPE_VALUES" :key="jt" :value="jt">
              {{ JOB_TYPE_LABELS[jt] }}
            </option>
          </select>
        </label>
        <label class="block">
          <span class="text-xs font-medium text-gray-600">Darbo vieta</span>
          <select
            :value="filters.workplace_type"
            class="mt-1 h-9 w-full rounded-md border border-gray-300 bg-white px-2 text-sm text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            @change="setWorkplaceType(($event.target as HTMLSelectElement).value as WorkplaceType | '')">
            <option value="">Bet kuri</option>
            <option v-for="wt in WORKPLACE_TYPE_VALUES" :key="wt" :value="wt">
              {{ WORKPLACE_TYPE_LABELS[wt] }}
            </option>
          </select>
        </label>
        <label class="block">
          <span class="text-xs font-medium text-gray-600">Vietovė</span>
          <input
            :value="locationInput"
            class="mt-1 h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Pvz. Vilnius"
            type="text"
            @input="onLocationInput(($event.target as HTMLInputElement).value)" />
        </label>
        <label class="block">
          <span class="text-xs font-medium text-gray-600">Min. atlyginimas (€)</span>
          <input
            :value="minSalaryInput ?? ''"
            class="mt-1 h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            min="0"
            placeholder="Pvz. 1500"
            type="number"
            @input="onMinSalaryInput(($event.target as HTMLInputElement).value)" />
        </label>
      </div>

      <div
        v-if="filters.search || filters.job_type || filters.workplace_type || filters.location || filters.min_salary"
        class="mt-3 flex justify-end">
        <button
          class="text-xs font-semibold text-attention underline-offset-4 hover:underline"
          type="button"
          @click="clearFilters">
          Išvalyti filtrus
        </button>
      </div>

      <p v-if="isPostingsLoading" class="mt-4 text-sm text-gray-600">Kraunama...</p>

      <div
        v-else-if="postings.length === 0"
        class="mt-4 flex flex-col items-center gap-3 rounded-md border border-dashed border-gray-300 bg-background/40 px-4 py-8 text-center">
        <p class="text-sm text-gray-700">
          Pagal pasirinktus filtrus skelbimų nerasta.
        </p>
      </div>

      <div v-else class="mt-4 overflow-x-auto">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
              <th class="py-2 pr-3 font-semibold">Pareigos / įmonė</th>
              <th class="py-2 pr-3 font-semibold">Darbo tipas</th>
              <th class="py-2 pr-3 font-semibold">Darbo vieta</th>
              <th class="py-2 pr-3 font-semibold">Atlyginimas</th>
              <th class="py-2 pr-3 font-semibold">Atnaujinta</th>
              <th class="py-2 pr-3 font-semibold">Atitikimas</th>
              <th class="py-2 font-semibold text-right">Veiksmas</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="posting in postings"
              :key="posting.id"
              class="cursor-pointer border-b border-gray-100 align-top transition hover:bg-background/40"
              @click="
                router.push({
                  name: ROUTE_NAMES.CANDIDATE_JOB_POSTING,
                  params: { id: posting.id },
                })
              ">
              <td class="py-3 pr-3">
                <div class="font-medium text-gray-950">{{ posting.title }}</div>
                <div class="mt-0.5 text-xs text-gray-500">{{ posting.company_name }}</div>
              </td>
              <td class="py-3 pr-3 text-gray-700">
                {{ JOB_TYPE_LABELS[posting.job_type] }}
              </td>
              <td class="py-3 pr-3 text-gray-700">
                {{ workplaceLabel(posting) }}
              </td>
              <td class="py-3 pr-3 text-gray-700">
                {{ formatSalary(posting.salary_min, posting.salary_max) }}
              </td>
              <td class="py-3 pr-3 text-gray-700">
                {{ formatShortDate(posting.updated_at) }}
              </td>
              <td class="py-3 pr-3">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold"
                  :class="matchScoreColorClasses(posting.match_score)">
                  {{ posting.match_score }} / 100
                </span>
              </td>
              <td class="py-3 text-right">
                <span
                  v-if="posting.has_applied"
                  class="inline-block rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-attention">
                  Aplikuota ✓
                </span>
                <button
                  v-else
                  class="inline-block rounded-md bg-attention px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-secondary disabled:opacity-60"
                  :disabled="applyingId === posting.id"
                  type="button"
                  @click.stop="applyTo(posting)">
                  {{ applyingId === posting.id ? 'Pateikiama...' : 'Aplikuoti' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div
          v-if="totalPages > 1"
          class="mt-4 flex items-center justify-between text-sm">
          <button
            class="rounded-md bg-gray-100 px-3 py-1.5 font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
            :disabled="!postingsPrevious"
            type="button"
            @click="goToPage(postingsPage - 1)">
            ← Atgal
          </button>
          <span class="text-gray-600">
            Puslapis {{ postingsPage }} iš {{ totalPages }}
          </span>
          <button
            class="rounded-md bg-gray-100 px-3 py-1.5 font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
            :disabled="!postingsNext"
            type="button"
            @click="goToPage(postingsPage + 1)">
            Pirmyn →
          </button>
        </div>
      </div>
    </section>
  </section>
  <section v-else class="rounded-lg bg-white p-6 text-gray-700 shadow-sm">
    Paskyros būsena atnaujinama.
  </section>
</template>
