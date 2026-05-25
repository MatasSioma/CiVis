<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
  watchEffect,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { dashboardRouteName, useAuth } from '@/stores/auth';
import { useToasts } from '@/stores/toasts';
import {
  JOB_TYPE_LABELS,
  WORKPLACE_TYPE_LABELS,
  type JobType,
  type WorkplaceType,
} from '@/services/employer';
import {
  DEFAULT_PUBLIC_POSTING_ORDERING,
  PUBLIC_POSTING_ORDERING_OPTIONS,
  PUBLIC_POSTING_PAGE_SIZE,
  publicPostingApi,
  type PublicJobPosting,
  type PublicPostingFilters,
  type PublicPostingOrdering,
} from '@/services/public';

const auth = useAuth();
const router = useRouter();
const route = useRoute();
const { showToast } = useToasts();

watchEffect(() => {
  if (import.meta.env.DEV) {
    console.debug('[view] HomeView auth redirect check', {
      user: auth.state.user,
    });
  }

  if (auth.state.user) {
    router.replace({ name: dashboardRouteName(auth.state.user.role) });
  }
});

const ALLOWED_ORDERINGS = PUBLIC_POSTING_ORDERING_OPTIONS.map((o) => o.value);
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

function parseOrdering(raw: unknown): PublicPostingOrdering {
  const value = Array.isArray(raw) ? raw[0] : raw;
  return ALLOWED_ORDERINGS.includes(value as PublicPostingOrdering)
    ? (value as PublicPostingOrdering)
    : DEFAULT_PUBLIC_POSTING_ORDERING;
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

const postings = ref<PublicJobPosting[]>([]);
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
  ordering: PublicPostingOrdering;
}>({
  search: '',
  job_type: '',
  workplace_type: '',
  min_salary: null,
  location: '',
  ordering: DEFAULT_PUBLIC_POSTING_ORDERING,
});

const searchInput = ref('');
const locationInput = ref('');
const minSalaryInput = ref<number | null>(null);

let searchDebounce: ReturnType<typeof setTimeout> | null = null;
let locationDebounce: ReturnType<typeof setTimeout> | null = null;
let minSalaryDebounce: ReturnType<typeof setTimeout> | null = null;

const totalPages = computed(() => {
  if (postingsTotal.value === 0) return 1;
  return Math.ceil(postingsTotal.value / PUBLIC_POSTING_PAGE_SIZE);
});

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

function workplaceLabel(posting: PublicJobPosting): string {
  if (posting.workplace_type === 'remote') {
    return WORKPLACE_TYPE_LABELS.remote;
  }
  return `${WORKPLACE_TYPE_LABELS.on_site} — ${posting.location || '—'}`;
}

async function loadPostings(
  page: number,
  ordering: PublicPostingOrdering,
  current: PublicPostingFilters,
) {
  isPostingsLoading.value = true;

  try {
    const data = await publicPostingApi.list(page, ordering, current);
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

async function setOrdering(value: PublicPostingOrdering) {
  await updateQuery({
    ordering: value === DEFAULT_PUBLIC_POSTING_ORDERING ? null : value,
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

const tableSection = ref<HTMLElement | null>(null);
const isTableVisible = ref(false);
let tableObserver: IntersectionObserver | null = null;

function scrollToTable() {
  tableSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
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

onMounted(() => {
  if (import.meta.env.DEV) {
    console.debug('[view] HomeView mounted');
  }

  syncFromRoute();
  void loadPostings(parsePage(route.query.page), filters.ordering, {
    search: filters.search,
    job_type: filters.job_type,
    workplace_type: filters.workplace_type,
    min_salary: filters.min_salary,
    location: filters.location,
  });

  if (tableSection.value && 'IntersectionObserver' in window) {
    tableObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            isTableVisible.value = true;
            tableObserver?.disconnect();
            tableObserver = null;
            break;
          }
        }
      },
      { threshold: 0.15 },
    );
    tableObserver.observe(tableSection.value);
  } else {
    isTableVisible.value = true;
  }
});

onBeforeUnmount(() => {
  if (import.meta.env.DEV) {
    console.debug('[view] HomeView beforeUnmount');
  }

  tableObserver?.disconnect();
  tableObserver = null;
});
</script>

<template>
  <section v-if="!auth.state.user" class="space-y-16 py-10">
    <div class="relative flex min-h-[calc(100vh-112px)] items-center">
      <div
        class="grid w-full items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
      <div class="max-w-2xl">
        <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
          Darbo paieškos ir įdarbinimo sistema
        </p>
        <h1 class="mt-3 text-4xl font-bold leading-tight text-gray-950 md:text-5xl">
          Darbo paieška ir kandidatų atranka vienoje vietoje
        </h1>
        <p class="mt-5 text-lg leading-8 text-gray-700">
          Platforma padeda darbo ieškantiems asmenims pristatyti savo patirtį, o
          darbdaviams patogiai valdyti įmonės skelbimus ir paraiškas.
        </p>

        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink
            class="rounded-md bg-attention px-5 py-3 font-semibold text-white no-underline transition hover:bg-secondary"
            :to="{ name: ROUTE_NAMES.LOGIN }">
            Prisijungti
          </RouterLink>
          <RouterLink
            class="rounded-md bg-primary px-5 py-3 font-semibold text-attention no-underline transition hover:bg-secondary"
            :to="{ name: ROUTE_NAMES.SIGNUP }">
            Registruotis
          </RouterLink>
        </div>
      </div>

      <div class="grid gap-4">
        <article class="rounded-lg border border-white/70 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-950">Darbo ieškantiems asmenims</h2>
          <p class="mt-2 text-sm leading-6 text-gray-600">
            Kurkite profilį, valdykite CV ir sekite savo paraiškas be papildomo
            triukšmo.
          </p>
        </article>
        <article class="rounded-lg border border-white/70 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-950">Darbdaviams</h2>
          <p class="mt-2 text-sm leading-6 text-gray-600">
            Tvarkykite įmonės informaciją, skelbimus ir kandidatų paraiškas vienoje
            darbo erdvėje.
          </p>
        </article>
      </div>
      </div>

      <button
        class="absolute bottom-4 left-1/2 flex -translate-x-1/2 flex-col items-center gap-1 text-xs font-semibold uppercase tracking-wide text-attention transition-opacity duration-500 hover:text-secondary"
        :class="
          isTableVisible
            ? 'pointer-events-none opacity-0'
            : 'animate-bounce opacity-100'
        "
        type="button"
        @click="scrollToTable">
        <span>Darbo skelbimai</span>
        <span aria-hidden="true" class="text-lg leading-none">↓</span>
      </button>
    </div>

    <section
      ref="tableSection"
      class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-all duration-700 ease-out"
      :class="
        isTableVisible
          ? 'translate-y-0 opacity-100'
          : 'pointer-events-none translate-y-16 opacity-0'
      ">
      <p class="rounded-md bg-primary/40 px-4 py-3 text-center text-sm text-gray-800">
        Prisijunkite ir įkelkite CV, kad pamatytumėte jūsų atitikimo įvertinimą.
      </p>

      <div class="mt-5 flex flex-wrap items-start justify-between gap-3">
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
            @change="setOrdering(($event.target as HTMLSelectElement).value as PublicPostingOrdering)">
            <option
              v-for="opt in PUBLIC_POSTING_ORDERING_OPTIONS"
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
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="posting in postings"
              :key="posting.id"
              class="border-b border-gray-100 align-top transition hover:bg-background/40">
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
</template>
