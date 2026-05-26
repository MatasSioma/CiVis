<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useToasts } from '@/stores/toasts';
import { cvApi, type CVDetailResponse } from '@/services/cv';
import { ApiError } from '@/services/api';
import FormCard from '@/components/FormCard.vue';

const route = useRoute();
const router = useRouter();
const { showToast } = useToasts();

const cv = ref<CVDetailResponse | null>(null);
const isLoading = ref(true);
const notFound = ref(false);
const showDeleteConfirm = ref(false);
const isDeleting = ref(false);

const SKILL_GROUPS = [
  { type: 'hard', label: 'Techniniai įgūdžiai' },
  { type: 'soft', label: 'Socialiniai įgūdžiai' },
  { type: 'experience', label: 'Patirtis' },
] as const;

const isPaymentReturn = route.query.payment === 'success';
const sessionId =
  typeof route.query.session_id === 'string' ? route.query.session_id : '';

function skillsByType(type: string) {
  return cv.value?.skills.filter((s) => s.type === type) ?? [];
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('lt-LT', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchCV(retries: number) {
  try {
    cv.value = await cvApi.getMyCV();
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      if (retries > 0 && isPaymentReturn) {
        await delay(1500);
        return fetchCV(retries - 1);
      }
      notFound.value = true;
    }
  }
}

async function finalizePayment() {
  try {
    cv.value = await cvApi.finalize(sessionId);
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 404) {
      throw error;
    }
  }
}

async function confirmDelete() {
  isDeleting.value = true;

  try {
    await cvApi.deleteMyCV();
    showToast('CV ištrintas.', 'success');
    router.push({ name: ROUTE_NAMES.CANDIDATE_DASHBOARD });
  } catch {
    showToast('Nepavyko ištrinti CV. Bandykite dar kartą.', 'error');
  } finally {
    isDeleting.value = false;
    showDeleteConfirm.value = false;
  }
}

onMounted(async () => {
  if (isPaymentReturn && sessionId) {
    try {
      await finalizePayment();
    } catch {
      // Ignore — fall back to webhook + retry-fetch.
    }
  }

  if (!cv.value) {
    await fetchCV(isPaymentReturn ? 3 : 0);
  }

  isLoading.value = false;

  if (isPaymentReturn && cv.value) {
    showToast('Mokėjimas sėkmingas! CV išsaugotas.', 'success');
  }
});

function goBack() {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DASHBOARD });
}
</script>

<template>
  <section class="space-y-6">
    <button
      class="inline-flex items-center gap-1 text-sm font-semibold text-attention hover:underline"
      type="button"
      @click="goBack">
      ← Grįžti į paskyrą
    </button>

  <div class="flex justify-center py-8">
    <FormCard v-if="isLoading" max-width="max-w-3xl">
      <p class="text-center text-gray-500">Kraunama...</p>
    </FormCard>

    <FormCard v-else-if="notFound" max-width="max-w-3xl">
      <h1 class="text-2xl leading-tight font-bold text-gray-950">Mano CV</h1>
      <p class="mt-2 text-sm text-gray-600">
        Dar neįkėlėte CV. Įkelkite PDF failą, kad sistema galėtų išgauti
        įgūdžius.
      </p>
      <RouterLink
        class="bg-attention hover:bg-secondary mt-4 inline-block cursor-pointer rounded-md px-4 py-2.5 font-semibold text-white transition"
        :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
        Įkelti CV →
      </RouterLink>
    </FormCard>

    <FormCard v-else-if="cv" max-width="max-w-3xl">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl leading-tight font-bold text-gray-950">
            Mano CV
          </h1>
          <p class="mt-1 text-sm text-gray-500">
            Įkelta: {{ formatDate(cv.created_at) }}
          </p>
        </div>
        <div class="flex flex-col items-end gap-2 sm:flex-row sm:items-center">
          <button
            class="bg-attention hover:bg-secondary cursor-pointer rounded-md px-3 py-1.5 text-sm font-semibold text-white transition"
            type="button"
            @click="router.push({ name: ROUTE_NAMES.UPLOAD_CV })">
            Įkelti naują
          </button>
          <button
            class="cursor-pointer rounded-md border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 transition hover:bg-red-50 hover:text-red-700"
            type="button"
            @click="showDeleteConfirm = true">
            Ištrinti CV
          </button>
        </div>
      </div>

      <template v-for="group in SKILL_GROUPS" :key="group.type">
        <div v-if="skillsByType(group.type).length > 0" class="mt-6">
          <h2
            class="text-sm font-semibold uppercase tracking-wide text-gray-500">
            {{ group.label }}
          </h2>
          <ul class="mt-2 space-y-2">
            <li
              v-for="skill in skillsByType(group.type)"
              :key="skill.name"
              class="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm">
              <div class="font-medium text-gray-900">{{ skill.name }}</div>
              <p
                v-if="skill.description"
                class="mt-0.5 text-xs text-gray-600">
                {{ skill.description }}
              </p>
            </li>
          </ul>
        </div>
      </template>

      <p v-if="cv.skills.length === 0" class="mt-6 text-sm text-gray-500">
        Nėra išsaugotų įgūdžių.
      </p>
    </FormCard>

    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      @click.self="showDeleteConfirm = false">
      <div class="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        <h2 class="text-lg font-semibold text-gray-950">
          Ar tikrai norite ištrinti CV?
        </h2>
        <p class="mt-3 text-sm text-gray-700">
          <span class="font-semibold text-red-600">Įspėjimas:</span>
          kartu bus ištrintos visos jūsų paraiškos darbo skelbimams.
        </p>
        <div class="mt-5 flex justify-end gap-3">
          <button
            class="h-10 cursor-pointer rounded-md border border-gray-300 px-4 text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
            :disabled="isDeleting"
            type="button"
            @click="showDeleteConfirm = false">
            Atšaukti
          </button>
          <button
            class="h-10 cursor-pointer rounded-md bg-red-600 px-4 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="isDeleting"
            type="button"
            @click="confirmDelete">
            {{ isDeleting ? 'Trinama...' : 'Ištrinti' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  </section>
</template>
