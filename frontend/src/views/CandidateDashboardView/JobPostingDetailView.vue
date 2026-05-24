<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ApiError } from '@/services/api';
import { cvApi } from '@/services/cv';
import {
  JOB_TYPE_LABELS,
  SKILL_TYPE_LABELS,
  WORKPLACE_TYPE_LABELS,
} from '@/services/employer';
import {
  candidateApplicationApi,
  candidatePostingApi,
  type CandidateJobPostingDetail,
} from '@/services/candidate';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useToasts } from '@/stores/toasts';

const route = useRoute();
const router = useRouter();
const { showToast } = useToasts();

const posting = ref<CandidateJobPostingDetail | null>(null);
const isLoading = ref(true);
const loadError = ref<string>('');

type CVStatus = 'loading' | 'uploaded' | 'missing';
const cvStatus = ref<CVStatus>('loading');

const isApplying = ref(false);
const isCancelling = ref(false);

const postingId = computed(() => {
  const raw = route.params.id;
  return Array.isArray(raw) ? raw[0] : raw;
});

const requiredSkills = computed(() =>
  posting.value ? posting.value.skills.filter((s) => s.is_required) : [],
);
const optionalSkills = computed(() =>
  posting.value ? posting.value.skills.filter((s) => !s.is_required) : [],
);

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('lt-LT', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatSalary(min: number | null, max: number | null): string {
  if (min == null && max == null) return '—';
  if (min != null && max != null) return `${min} – ${max} €`;
  if (min != null) return `nuo ${min} €`;
  return `iki ${max} €`;
}

function matchScoreColorClasses(score: number): string {
  if (score >= 70) return 'bg-primary text-attention';
  if (score >= 40) return 'bg-amber-100 text-amber-800';
  return 'bg-red-100 text-red-700';
}

function workplaceLabel(p: CandidateJobPostingDetail): string {
  if (p.workplace_type === 'remote') return WORKPLACE_TYPE_LABELS.remote;
  return `${WORKPLACE_TYPE_LABELS.on_site} — ${p.location || '—'}`;
}

async function loadPosting() {
  if (!postingId.value) return;
  isLoading.value = true;
  loadError.value = '';

  try {
    posting.value = await candidatePostingApi.get(postingId.value);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      loadError.value = 'Skelbimas nerastas arba nebėra atviras.';
    } else {
      loadError.value = 'Nepavyko įkelti skelbimo.';
    }
    posting.value = null;
  } finally {
    isLoading.value = false;
  }
}

async function loadCvStatus() {
  try {
    await cvApi.getMyCV();
    cvStatus.value = 'uploaded';
  } catch (error) {
    cvStatus.value =
      error instanceof ApiError && error.status === 404 ? 'missing' : 'missing';
  }
}

async function apply() {
  if (!posting.value || cvStatus.value !== 'uploaded' || posting.value.has_applied) {
    return;
  }
  isApplying.value = true;

  try {
    await candidatePostingApi.apply(posting.value.id);
    showToast('Paraiška pateikta.', 'success');
    await loadPosting();
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
    isApplying.value = false;
  }
}

async function cancelApplication() {
  if (!posting.value || !posting.value.application_id) return;
  if (!window.confirm('Ar tikrai norite atšaukti paraišką?')) return;

  isCancelling.value = true;

  try {
    await candidateApplicationApi.cancel(posting.value.application_id);
    showToast('Paraiška atšaukta.', 'success');
    await loadPosting();
  } catch {
    showToast('Nepavyko atšaukti paraiškos.', 'error');
  } finally {
    isCancelling.value = false;
  }
}

function goBack() {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DASHBOARD });
}

watch(postingId, () => {
  void loadPosting();
});

onMounted(() => {
  void loadCvStatus();
  void loadPosting();
});
</script>

<template>
  <section class="space-y-6">
    <button
      class="inline-flex items-center gap-1 text-sm font-semibold text-attention hover:underline"
      type="button"
      @click="goBack">
      ← Grįžti į paskyrą
    </button>

    <p v-if="isLoading" class="text-sm text-gray-600">Kraunama...</p>

    <div
      v-else-if="loadError"
      class="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ loadError }}
    </div>

    <template v-else-if="posting">
      <article class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
              Darbo skelbimas
            </p>
            <h1 class="mt-2 text-2xl font-bold text-gray-950">{{ posting.title }}</h1>
            <p class="mt-1 text-sm text-gray-600">
              {{ posting.company.name }} · {{ posting.industry_name }}
            </p>
          </div>
          <span
            class="inline-flex items-center rounded-full px-4 py-2 text-base font-semibold"
            :class="matchScoreColorClasses(posting.match_score)">
            Atitikimas {{ posting.match_score }} / 100
          </span>
        </div>

        <dl class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">Darbo tipas</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              {{ JOB_TYPE_LABELS[posting.job_type] }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">Darbo vieta</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              {{ workplaceLabel(posting) }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">Atlyginimas</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              {{ formatSalary(posting.salary_min, posting.salary_max) }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">Sukurta</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              {{ formatDate(posting.created_at) }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">Atnaujinta</dt>
            <dd class="mt-1 text-sm font-medium text-gray-950">
              {{ formatDate(posting.updated_at) }}
            </dd>
          </div>
        </dl>

        <div class="mt-6">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Aprašymas
          </h2>
          <p class="mt-2 whitespace-pre-line text-sm text-gray-800">
            {{ posting.description || '—' }}
          </p>
        </div>

        <div v-if="requiredSkills.length > 0" class="mt-6">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Privalomi reikalavimai
          </h2>
          <ul class="mt-2 space-y-2">
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

        <div v-if="optionalSkills.length > 0" class="mt-6">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Pageidaujami įgūdžiai
          </h2>
          <ul class="mt-2 space-y-2">
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

        <div class="mt-6 flex flex-wrap items-center gap-3 border-t border-gray-200 pt-5">
          <template v-if="cvStatus === 'loading'">
            <span class="text-sm text-gray-500">Kraunama paraiškos būsena...</span>
          </template>
          <template v-else-if="cvStatus === 'missing'">
            <p class="text-sm text-gray-700">
              Norėdami pateikti paraišką, pirmiausia įkelkite CV.
            </p>
            <RouterLink
              class="rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary"
              :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
              Įkelti CV →
            </RouterLink>
          </template>
          <template v-else-if="posting.has_applied">
            <span
              class="inline-block rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-attention">
              Aplikuota ✓
            </span>
            <button
              class="rounded-md bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-60"
              :disabled="isCancelling"
              type="button"
              @click="cancelApplication">
              {{ isCancelling ? 'Atšaukiama...' : 'Atšaukti paraišką' }}
            </button>
          </template>
          <template v-else>
            <button
              class="rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary disabled:opacity-60"
              :disabled="isApplying"
              type="button"
              @click="apply">
              {{ isApplying ? 'Pateikiama...' : 'Aplikuoti' }}
            </button>
          </template>
        </div>
      </article>

      <article class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
          Įmonės informacija
        </p>
        <h2 class="mt-2 text-xl font-bold text-gray-950">{{ posting.company.name }}</h2>
        <p
          v-if="posting.company.description"
          class="mt-2 whitespace-pre-line text-sm text-gray-700">
          {{ posting.company.description }}
        </p>
        <p v-else class="mt-2 text-sm text-gray-500">Aprašymas dar nepateiktas.</p>

        <dl class="mt-4 grid gap-3 sm:grid-cols-2">
          <div>
            <dt class="text-xs text-gray-500">Įmonės kodas</dt>
            <dd class="text-sm font-medium text-gray-950">
              {{ posting.company.registration_code || '—' }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Įsteigimo data</dt>
            <dd class="text-sm font-medium text-gray-950">
              {{
                posting.company.date_established
                  ? formatDate(posting.company.date_established)
                  : '—'
              }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Adresas</dt>
            <dd class="text-sm font-medium text-gray-950">
              {{ posting.company.address || '—' }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Kontaktinis el. paštas</dt>
            <dd class="text-sm font-medium text-gray-950">
              <a
                v-if="posting.company.contact_email"
                class="text-attention underline-offset-4 hover:underline"
                :href="`mailto:${posting.company.contact_email}`">
                {{ posting.company.contact_email }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Kontaktinis telefonas</dt>
            <dd class="text-sm font-medium text-gray-950">
              <a
                v-if="posting.company.contact_phone"
                class="text-attention underline-offset-4 hover:underline"
                :href="`tel:${posting.company.contact_phone}`">
                {{ posting.company.contact_phone }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Svetainė / socialinis tinklas</dt>
            <dd class="text-sm font-medium text-gray-950">
              <a
                v-if="posting.company.website"
                class="text-attention underline-offset-4 hover:underline"
                :href="posting.company.website"
                rel="noopener noreferrer"
                target="_blank">
                {{ posting.company.website }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
        </dl>
      </article>
    </template>
  </section>
</template>
