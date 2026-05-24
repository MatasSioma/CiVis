<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useToasts } from '@/stores/toasts';
import { ApiError } from '@/services/api';
import {
  APPLICATION_STATUS_LABELS,
  APPLICATION_STATUS_VALUES,
  SKILL_TYPE_LABELS,
  employerApplicationApi,
  type ApplicationStatus,
  type EmployerApplicationDetail,
  type SkillType,
} from '@/services/employer';

const route = useRoute();
const router = useRouter();
const { showToast } = useToasts();

const application = ref<EmployerApplicationDetail | null>(null);
const isLoading = ref(true);
const loadError = ref<string>('');
const isUpdatingStatus = ref(false);

const applicationId = computed(() => {
  const raw = route.params.id;
  return Array.isArray(raw) ? raw[0] : raw;
});

const postingId = computed(() => {
  const raw = route.params.postingId;
  return Array.isArray(raw) ? raw[0] : raw;
});

const skillsByType = computed(() => {
  const groups: Record<SkillType, EmployerApplicationDetail['cv'] extends null
    ? never
    : NonNullable<EmployerApplicationDetail['cv']>['skills']> = {
    hard: [],
    soft: [],
    experience: [],
  };

  const cv = application.value?.cv;
  if (!cv) return groups;

  for (const skill of cv.skills) {
    groups[skill.type].push(skill);
  }
  return groups;
});

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('lt-LT', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function matchScoreColorClasses(score: number): string {
  if (score >= 70) return 'bg-primary text-attention';
  if (score >= 40) return 'bg-amber-100 text-amber-800';
  return 'bg-red-100 text-red-700';
}

function applicantDisplayName(detail: EmployerApplicationDetail): string {
  const name = `${detail.applicant.first_name} ${detail.applicant.last_name}`.trim();
  return name || detail.applicant.email;
}

async function loadApplication() {
  if (!applicationId.value) return;
  isLoading.value = true;
  loadError.value = '';

  try {
    application.value = await employerApplicationApi.get(applicationId.value);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      loadError.value = 'Paraiška nerasta.';
    } else {
      loadError.value = 'Nepavyko įkelti paraiškos.';
    }
    application.value = null;
  } finally {
    isLoading.value = false;
  }
}

function goBack() {
  if (postingId.value) {
    router.push({
      name: ROUTE_NAMES.EMPLOYER_APPLICANTS,
      params: { id: postingId.value },
    });
  } else if (application.value) {
    router.push({
      name: ROUTE_NAMES.EMPLOYER_APPLICANTS,
      params: { id: application.value.job_posting_id },
    });
  } else {
    router.push({ name: ROUTE_NAMES.EMPLOYER_DASHBOARD });
  }
}

async function updateStatus(value: ApplicationStatus) {
  if (!application.value) return;
  const previous = application.value.status;
  if (value === previous) return;

  isUpdatingStatus.value = true;
  application.value.status = value;

  try {
    await employerApplicationApi.updateStatus(application.value.id, value);
    showToast('Būsena atnaujinta.', 'success');
  } catch (error) {
    if (application.value) {
      application.value.status = previous;
    }
    let message = 'Nepavyko atnaujinti būsenos.';
    if (error instanceof ApiError && error.status === 400) {
      message =
        (error.details && typeof error.details === 'object'
          ? Object.values(error.details).flat().join(' ')
          : error.message) || message;
    }
    showToast(message, 'error');
  } finally {
    isUpdatingStatus.value = false;
  }
}

watch(applicationId, () => {
  void loadApplication();
});

onMounted(() => {
  void loadApplication();
});
</script>

<template>
  <section class="space-y-6">
    <button
      class="inline-flex items-center gap-1 text-sm font-semibold text-attention hover:underline"
      type="button"
      @click="goBack">
      ← Grįžti į kandidatų sąrašą
    </button>

    <p v-if="isLoading" class="text-sm text-gray-600">Kraunama...</p>

    <div
      v-else-if="loadError"
      class="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ loadError }}
    </div>

    <template v-else-if="application">
      <article class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
              Kandidatas
            </p>
            <h1 class="mt-2 text-2xl font-bold text-gray-950">
              {{ applicantDisplayName(application) }}
            </h1>
            <p class="mt-1 text-sm text-gray-600">
              Paraiška pateikta {{ formatDate(application.created_at) }}
            </p>
          </div>
          <span
            class="inline-flex items-center rounded-full px-4 py-2 text-base font-semibold"
            :class="matchScoreColorClasses(application.match_score)">
            Atitikimas {{ application.match_score }} / 100
          </span>
        </div>

        <dl class="mt-6 grid gap-4 sm:grid-cols-3">
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">El. paštas</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              <a
                class="text-attention underline-offset-4 hover:underline"
                :href="`mailto:${application.applicant.email}`">
                {{ application.applicant.email }}
              </a>
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">Gimimo data</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              {{
                application.applicant.date_of_birth
                  ? formatDate(application.applicant.date_of_birth)
                  : '—'
              }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">
              Paraiškos statusas
            </dt>
            <dd class="mt-1">
              <select
                :value="application.status"
                class="h-9 w-full rounded-md border border-gray-300 bg-white px-2 text-sm text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40 disabled:opacity-60"
                :disabled="isUpdatingStatus"
                @change="
                  updateStatus(
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
            </dd>
          </div>
        </dl>
      </article>

      <article class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
          CV ir įgūdžiai
        </p>

        <p
          v-if="!application.cv"
          class="mt-3 rounded-md border border-dashed border-gray-300 bg-background/40 px-4 py-3 text-sm text-gray-700">
          Kandidatas CV pašalino.
        </p>

        <template v-else>
          <p class="mt-2 text-sm text-gray-600">
            Įkelta {{ formatDate(application.cv.created_at) }}
          </p>

          <div class="mt-5 space-y-5">
            <section v-if="skillsByType.hard.length > 0">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">
                {{ SKILL_TYPE_LABELS.hard }}
              </h3>
              <ul class="mt-2 space-y-2">
                <li
                  v-for="skill in skillsByType.hard"
                  :key="`hard-${skill.name}`"
                  class="rounded-md border border-gray-200 bg-background/40 p-3">
                  <span class="text-sm font-medium text-gray-950">
                    {{ skill.name }}
                  </span>
                  <p v-if="skill.description" class="mt-1 text-xs text-gray-600">
                    {{ skill.description }}
                  </p>
                </li>
              </ul>
            </section>

            <section v-if="skillsByType.soft.length > 0">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">
                {{ SKILL_TYPE_LABELS.soft }}
              </h3>
              <ul class="mt-2 space-y-2">
                <li
                  v-for="skill in skillsByType.soft"
                  :key="`soft-${skill.name}`"
                  class="rounded-md border border-gray-200 bg-background/40 p-3">
                  <span class="text-sm font-medium text-gray-950">
                    {{ skill.name }}
                  </span>
                  <p v-if="skill.description" class="mt-1 text-xs text-gray-600">
                    {{ skill.description }}
                  </p>
                </li>
              </ul>
            </section>

            <section v-if="skillsByType.experience.length > 0">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500">
                {{ SKILL_TYPE_LABELS.experience }}
              </h3>
              <ul class="mt-2 space-y-2">
                <li
                  v-for="skill in skillsByType.experience"
                  :key="`exp-${skill.name}`"
                  class="rounded-md border border-gray-200 bg-background/40 p-3">
                  <span class="text-sm font-medium text-gray-950">
                    {{ skill.name }}
                  </span>
                  <p v-if="skill.description" class="mt-1 text-xs text-gray-600">
                    {{ skill.description }}
                  </p>
                </li>
              </ul>
            </section>

            <p
              v-if="
                skillsByType.hard.length === 0 &&
                skillsByType.soft.length === 0 &&
                skillsByType.experience.length === 0
              "
              class="text-sm text-gray-600">
              CV įgūdžių sąrašas tuščias.
            </p>
          </div>
        </template>
      </article>
    </template>
  </section>
</template>
