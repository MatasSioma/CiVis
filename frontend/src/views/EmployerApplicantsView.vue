<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useToasts } from '@/stores/toasts';
import { ApiError } from '@/services/api';
import {
  APPLICATION_STATUS_LABELS,
  APPLICATION_STATUS_VALUES,
  JOB_TYPE_LABELS,
  SKILL_TYPE_LABELS,
  employerApplicationApi,
  jobPostingApi,
  type ApplicationStatus,
  type EmployerApplicantListItem,
  type JobPostingDetail,
} from '@/services/employer';

const route = useRoute();
const router = useRouter();
const { showToast } = useToasts();

const PAGE_SIZE = 10;

const postingId = computed(() => {
  const raw = route.params.id;
  return Array.isArray(raw) ? raw[0] : raw;
});

const posting = ref<JobPostingDetail | null>(null);
const isPostingLoading = ref(true);

function formatSalaryRange(min: number | null, max: number | null): string {
  if (min == null && max == null) return 'Atlyginimas nenurodytas';
  if (min != null && max != null) return `${min} – ${max} €`;
  if (min != null) return `nuo ${min} €`;
  return `iki ${max} €`;
}

const requiredSkills = computed(() =>
  posting.value
    ? posting.value.skills_detail.filter((s) => s.is_required)
    : [],
);
const optionalSkills = computed(() =>
  posting.value
    ? posting.value.skills_detail.filter((s) => !s.is_required)
    : [],
);

const applicants = ref<EmployerApplicantListItem[]>([]);
const applicantsTotal = ref(0);
const applicantsPage = ref(1);
const applicantsNext = ref<string | null>(null);
const applicantsPrevious = ref<string | null>(null);
const isApplicantsLoading = ref(true);

const updatingStatusId = ref<string | null>(null);

const totalPages = computed(() => {
  if (applicantsTotal.value === 0) return 1;
  return Math.ceil(applicantsTotal.value / PAGE_SIZE);
});

function parsePage(raw: unknown): number {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 1 ? Math.floor(parsed) : 1;
}

function formatShortDate(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('lt-LT');
}

function matchScoreColorClasses(score: number): string {
  if (score >= 70) return 'bg-primary text-attention';
  if (score >= 40) return 'bg-amber-100 text-amber-800';
  return 'bg-red-100 text-red-700';
}

function applicantDisplayName(item: EmployerApplicantListItem): string {
  const name = `${item.applicant_first_name} ${item.applicant_last_name}`.trim();
  return name || item.applicant_email;
}

async function loadPosting() {
  if (!postingId.value) return;
  isPostingLoading.value = true;

  try {
    posting.value = await jobPostingApi.get(postingId.value);
  } catch {
    posting.value = null;
    showToast('Nepavyko įkelti skelbimo.', 'error');
  } finally {
    isPostingLoading.value = false;
  }
}

async function loadApplicants(page: number) {
  if (!postingId.value) return;
  isApplicantsLoading.value = true;

  try {
    const data = await employerApplicationApi.list(postingId.value, page);
    applicants.value = data.results;
    applicantsTotal.value = data.count;
    applicantsNext.value = data.next;
    applicantsPrevious.value = data.previous;
    applicantsPage.value = page;
  } catch {
    showToast('Nepavyko įkelti kandidatų.', 'error');
  } finally {
    isApplicantsLoading.value = false;
  }
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

function goToDetail(application: EmployerApplicantListItem) {
  if (!postingId.value) return;
  router.push({
    name: ROUTE_NAMES.EMPLOYER_APPLICATION_DETAIL,
    params: { postingId: postingId.value, id: application.id },
  });
}

function goBack() {
  router.push({ name: ROUTE_NAMES.EMPLOYER_DASHBOARD });
}

async function updateStatus(
  application: EmployerApplicantListItem,
  value: ApplicationStatus,
) {
  const previousStatus = application.status;

  if (value === previousStatus) return;

  updatingStatusId.value = application.id;
  application.status = value;

  try {
    await employerApplicationApi.updateStatus(application.id, value);
    showToast('Būsena atnaujinta.', 'success');
  } catch (error) {
    application.status = previousStatus;
    let message = 'Nepavyko atnaujinti būsenos.';
    if (error instanceof ApiError && error.status === 400) {
      message =
        (error.details && typeof error.details === 'object'
          ? Object.values(error.details).flat().join(' ')
          : error.message) || message;
    }
    showToast(message, 'error');
  } finally {
    updatingStatusId.value = null;
  }
}

watch(
  () => route.query.page,
  () => {
    void loadApplicants(parsePage(route.query.page));
  },
);

watch(postingId, () => {
  void loadPosting();
  void loadApplicants(parsePage(route.query.page));
});

onMounted(() => {
  void loadPosting();
  void loadApplicants(parsePage(route.query.page));
});
</script>

<template>
  <section class="space-y-6">
    <button
      class="inline-flex items-center gap-1 text-sm font-semibold text-attention hover:underline"
      type="button"
      @click="goBack">
      ← Grįžti į skelbimų sąrašą
    </button>

    <header class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
            Kandidatai
          </p>
          <h1 v-if="isPostingLoading" class="mt-2 text-lg text-gray-500">
            Kraunama...
          </h1>
          <h1 v-else-if="posting" class="mt-2 text-2xl font-bold text-gray-950">
            {{ posting.title }}
          </h1>
          <h1 v-else class="mt-2 text-2xl font-bold text-gray-950">
            Skelbimas nerastas
          </h1>
          <p v-if="posting" class="mt-1 text-sm text-gray-600">
            {{ JOB_TYPE_LABELS[posting.job_type]
            }}<span v-if="!isApplicantsLoading">
              · paraiškų: {{ applicantsTotal }}</span>
          </p>
          <p
            v-else-if="!isApplicantsLoading"
            class="mt-1 text-sm text-gray-600">
            Iš viso paraiškų: {{ applicantsTotal }}
          </p>
        </div>
        <span
          v-if="posting"
          class="inline-flex items-center rounded-full bg-primary px-4 py-2 text-base font-semibold text-attention">
          {{ formatSalaryRange(posting.salary_min, posting.salary_max) }}
        </span>
      </div>

      <div v-if="posting" class="mt-5 space-y-5">
        <div>
          <h2 class="text-xs font-semibold uppercase tracking-wide text-secondary">
            Skelbimo aprašymas
          </h2>
          <p class="mt-2 whitespace-pre-line text-sm text-gray-800">
            {{ posting.description || '—' }}
          </p>
        </div>

        <div v-if="requiredSkills.length > 0">
          <h2 class="text-xs font-semibold uppercase tracking-wide text-secondary">
            Privalomi reikalavimai
          </h2>
          <ul class="mt-2 grid gap-2 sm:grid-cols-2">
            <li
              v-for="skill in requiredSkills"
              :key="`req-${skill.name}`"
              class="rounded-md border border-gray-200 bg-background/40 p-3">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm font-medium text-gray-950">{{ skill.name }}</span>
                <span class="text-xs text-gray-500">
                  {{ SKILL_TYPE_LABELS[skill.type] }}
                </span>
              </div>
              <p v-if="skill.description" class="mt-1 text-xs text-gray-600">
                {{ skill.description }}
              </p>
            </li>
          </ul>
        </div>

        <div v-if="optionalSkills.length > 0">
          <h2 class="text-xs font-semibold uppercase tracking-wide text-secondary">
            Pageidaujami įgūdžiai
          </h2>
          <ul class="mt-2 grid gap-2 sm:grid-cols-2">
            <li
              v-for="skill in optionalSkills"
              :key="`opt-${skill.name}`"
              class="rounded-md border border-gray-200 bg-background/40 p-3">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm font-medium text-gray-950">{{ skill.name }}</span>
                <span class="text-xs text-gray-500">
                  {{ SKILL_TYPE_LABELS[skill.type] }}
                </span>
              </div>
              <p v-if="skill.description" class="mt-1 text-xs text-gray-600">
                {{ skill.description }}
              </p>
            </li>
          </ul>
        </div>
      </div>
    </header>

    <section class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <p v-if="isApplicantsLoading" class="text-sm text-gray-600">Kraunama...</p>

      <div
        v-else-if="applicants.length === 0"
        class="flex flex-col items-center gap-3 rounded-md border border-dashed border-gray-300 bg-background/40 px-4 py-8 text-center">
        <p class="text-sm text-gray-700">Į šį skelbimą dar nėra paraiškų.</p>
        <button
          class="rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary"
          type="button"
          @click="goBack">
          Grįžti į skelbimus
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
              <th class="py-2 pr-3 font-semibold">Vardas, pavardė</th>
              <th class="py-2 pr-3 font-semibold">El. paštas</th>
              <th class="py-2 pr-3 font-semibold">Pateikta</th>
              <th class="py-2 pr-3 font-semibold">Atitikimas</th>
              <th class="py-2 pr-3 font-semibold">Būsena</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="application in applicants"
              :key="application.id"
              class="cursor-pointer border-b border-gray-100 transition hover:bg-background/40"
              @click="goToDetail(application)">
              <td class="py-3 pr-3 font-medium text-gray-950">
                {{ applicantDisplayName(application) }}
              </td>
              <td class="py-3 pr-3 text-gray-700">{{ application.applicant_email }}</td>
              <td class="py-3 pr-3 text-gray-700">
                {{ formatShortDate(application.created_at) }}
              </td>
              <td class="py-3 pr-3">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
                  :class="matchScoreColorClasses(application.match_score)">
                  {{ application.match_score }} / 100
                </span>
              </td>
              <td class="py-3 pr-3" @click.stop>
                <select
                  :value="application.status"
                  class="h-9 rounded-md border border-gray-300 bg-white px-2 text-sm text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40 disabled:opacity-60"
                  :disabled="updatingStatusId === application.id"
                  @change="
                    updateStatus(
                      application,
                      ($event.target as HTMLSelectElement).value as ApplicationStatus,
                    )
                  ">
                  <option
                    v-for="value in APPLICATION_STATUS_VALUES"
                    :key="value"
                    :value="value">
                    {{ APPLICATION_STATUS_LABELS[value] }}
                  </option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>

        <div
          v-if="totalPages > 1"
          class="mt-4 flex items-center justify-between text-sm">
          <button
            class="rounded-md bg-gray-100 px-3 py-1.5 font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
            :disabled="!applicantsPrevious"
            type="button"
            @click="goToPage(applicantsPage - 1)">
            ← Atgal
          </button>
          <span class="text-gray-600">
            Puslapis {{ applicantsPage }} iš {{ totalPages }}
          </span>
          <button
            class="rounded-md bg-gray-100 px-3 py-1.5 font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
            :disabled="!applicantsNext"
            type="button"
            @click="goToPage(applicantsPage + 1)">
            Pirmyn →
          </button>
        </div>
      </div>
    </section>
  </section>
</template>
