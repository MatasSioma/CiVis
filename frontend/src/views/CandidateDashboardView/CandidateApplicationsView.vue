<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useToasts } from '@/stores/toasts';
import {
  APPLICATION_STATUS_LABELS,
} from '@/services/employer';
import {
  candidateApplicationApi,
  type CandidateApplication,
} from '@/services/candidate';

const router = useRouter();
const { showToast } = useToasts();

const applications = ref<CandidateApplication[]>([]);
const isLoading = ref(true);
const cancellingId = ref<string | null>(null);
const archivingId = ref<string | null>(null);

const activeApplications = computed(() =>
  applications.value.filter((a) => !a.is_archived),
);

const archivedApplications = computed(() =>
  applications.value.filter((a) => a.is_archived),
);

function formatShortDate(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('lt-LT');
}

function matchScoreColorClasses(score: number): string {
  if (score >= 70) return 'bg-primary text-attention';
  if (score >= 40) return 'bg-amber-100 text-amber-800';
  return 'bg-red-100 text-red-700';
}

function applicationStatusClasses(status: CandidateApplication['status']): string {
  if (status === 'accepted') return 'bg-primary text-attention';
  if (status === 'rejected') return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
}

function goBack() {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DASHBOARD });
}

async function loadApplications() {
  isLoading.value = true;

  try {
    applications.value = await candidateApplicationApi.list();
  } catch {
    showToast('Nepavyko įkelti paraiškų.', 'error');
  } finally {
    isLoading.value = false;
  }
}

async function cancelApplication(application: CandidateApplication) {
  if (
    !window.confirm(
      `Ar tikrai norite atšaukti paraišką į „${application.job_posting_title}"?`,
    )
  ) {
    return;
  }

  cancellingId.value = application.id;

  try {
    await candidateApplicationApi.cancel(application.id);
    showToast('Paraiška atšaukta.', 'success');
    await loadApplications();
  } catch {
    showToast('Nepavyko atšaukti paraiškos.', 'error');
  } finally {
    cancellingId.value = null;
  }
}

async function archiveApplication(application: CandidateApplication) {
  archivingId.value = application.id;

  try {
    await candidateApplicationApi.archive(application.id);
    showToast('Paraiška archyvuota.', 'success');
    await loadApplications();
  } catch {
    showToast('Nepavyko archyvuoti paraiškos.', 'error');
  } finally {
    archivingId.value = null;
  }
}

onMounted(() => {
  void loadApplications();
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

    <div>
      <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
        Mano paraiškos
      </p>
      <h1 class="mt-1 text-2xl font-bold text-gray-950">Paraiškos</h1>
    </div>

    <p v-if="isLoading" class="text-sm text-gray-500">Kraunama...</p>

    <div
      v-else-if="applications.length === 0"
      class="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center shadow-sm">
      <p class="text-sm text-gray-600">Dar nepateikėte paraiškų.</p>
    </div>

    <template v-else>
      <section
        v-if="activeApplications.length > 0"
        class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">
          Aktyvios paraiškos
          <span class="ml-1 text-sm font-normal text-gray-500">
            ({{ activeApplications.length }})
          </span>
        </h2>

        <ul class="mt-4 space-y-3">
          <li
            v-for="application in activeApplications"
            :key="application.id"
            class="rounded-md border border-gray-200 bg-background/40 p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <RouterLink
                  class="text-sm font-medium text-gray-950 hover:underline"
                  :to="{
                    name: ROUTE_NAMES.CANDIDATE_JOB_POSTING,
                    params: { id: application.job_posting },
                  }">
                  {{ application.job_posting_title }}
                </RouterLink>
                <p class="mt-0.5 text-xs text-gray-500">
                  {{ application.company_name }}
                </p>
              </div>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="matchScoreColorClasses(application.match_score)">
                {{ application.match_score }} / 100
              </span>
            </div>

            <div class="mt-2 flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span
                  class="rounded-full px-2.5 py-1 text-xs font-semibold"
                  :class="applicationStatusClasses(application.status)">
                  {{ APPLICATION_STATUS_LABELS[application.status] }}
                </span>
                <span class="text-xs text-gray-400">
                  {{ formatShortDate(application.created_at) }}
                </span>
              </div>

              <button
                v-if="application.status === 'pending'"
                class="rounded-md bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
                :disabled="cancellingId === application.id"
                type="button"
                @click="cancelApplication(application)">
                {{
                  cancellingId === application.id
                    ? 'Atšaukiama...'
                    : 'Atšaukti'
                }}
              </button>
              <button
                v-else
                class="rounded-md border border-gray-200 px-2.5 py-1 text-xs font-semibold text-gray-600 transition hover:bg-gray-100 disabled:opacity-50"
                :disabled="archivingId === application.id"
                type="button"
                @click="archiveApplication(application)">
                {{
                  archivingId === application.id
                    ? 'Archyvuojama...'
                    : 'Archyvuoti'
                }}
              </button>
            </div>
          </li>
        </ul>
      </section>

      <section
        v-if="archivedApplications.length > 0"
        class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">
          Archyvuotos paraiškos
          <span class="ml-1 text-sm font-normal text-gray-500">
            ({{ archivedApplications.length }})
          </span>
        </h2>

        <ul class="mt-4 space-y-3">
          <li
            v-for="application in archivedApplications"
            :key="application.id"
            class="rounded-md border border-gray-200 bg-background/40 p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <RouterLink
                  class="text-sm font-medium text-gray-950 hover:underline"
                  :to="{
                    name: ROUTE_NAMES.CANDIDATE_JOB_POSTING,
                    params: { id: application.job_posting },
                  }">
                  {{ application.job_posting_title }}
                </RouterLink>
                <p class="mt-0.5 text-xs text-gray-500">
                  {{ application.company_name }}
                </p>
              </div>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="matchScoreColorClasses(application.match_score)">
                {{ application.match_score }} / 100
              </span>
            </div>

            <div class="mt-2 flex items-center gap-2">
              <span
                class="rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="applicationStatusClasses(application.status)">
                {{ APPLICATION_STATUS_LABELS[application.status] }}
              </span>
              <span class="text-xs text-gray-400">
                {{ formatShortDate(application.created_at) }}
              </span>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </section>
</template>
