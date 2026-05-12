<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useToasts } from '@/stores/toasts';
import { cvApi, type CVDetailResponse } from '@/services/cv';
import { ApiError } from '@/services/api';
import FormCard from '@/components/FormCard.vue';

const route = useRoute();
const { showToast } = useToasts();

const cv = ref<CVDetailResponse | null>(null);
const isLoading = ref(true);
const notFound = ref(false);

const SKILL_GROUPS = [
  { type: 'hard', label: 'Techniniai įgūdžiai' },
  { type: 'soft', label: 'Socialiniai įgūdžiai' },
  { type: 'experience', label: 'Patirtis' },
] as const;

const isPaymentReturn = route.query.payment === 'success';

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

onMounted(async () => {
  await fetchCV(isPaymentReturn ? 3 : 0);
  isLoading.value = false;
  if (isPaymentReturn && cv.value) {
    showToast('Mokėjimas sėkmingas! CV išsaugotas.', 'success');
  }
});
</script>

<template>
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
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-2xl leading-tight font-bold text-gray-950">
            Mano CV
          </h1>
          <p class="mt-1 text-sm text-gray-500">
            Įkelta: {{ formatDate(cv.created_at) }}
          </p>
        </div>
        <RouterLink
          class="text-secondary hover:text-secondary/80 text-sm font-medium"
          :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
          Įkelti naują →
        </RouterLink>
      </div>

      <template v-for="group in SKILL_GROUPS" :key="group.type">
        <div v-if="skillsByType(group.type).length > 0" class="mt-6">
          <h2
            class="text-sm font-semibold uppercase tracking-wide text-gray-500">
            {{ group.label }}
          </h2>
          <div class="mt-2 flex flex-wrap gap-2">
            <span
              v-for="skill in skillsByType(group.type)"
              :key="skill.name"
              class="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-sm text-gray-800">
              {{ skill.name }}
              <span
                v-if="skill.years_of_experience > 0"
                class="text-xs text-gray-500">
                · {{ skill.years_of_experience }} m.
              </span>
            </span>
          </div>
        </div>
      </template>

      <p v-if="cv.skills.length === 0" class="mt-6 text-sm text-gray-500">
        Nėra išsaugotų įgūdžių.
      </p>
    </FormCard>
  </div>
</template>
