<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BrandLogo from '@/components/BrandLogo.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useGateway } from '@/stores/gateway';
import { useToasts } from '@/stores/toasts';
import type { UserRole } from '@/shared/types';

const route = useRoute();
const router = useRouter();
const gateway = useGateway();
const { showToast } = useToasts();

const selectedRole = ref<UserRole | null>(null);
const fieldError = ref('');

const roleOptions: { label: string; description: string; value: UserRole }[] = [
  {
    label: 'Darbdavys',
    description: 'Įmonės skelbimų ir kandidatų paraiškų valdymas.',
    value: 'employer',
  },
  {
    label: 'Darbo ieškantis asmuo',
    description: 'CV, profilio ir darbo paraiškų valdymas.',
    value: 'job_seeker',
  },
];

const signupRoute = computed(() => ({
  name: ROUTE_NAMES.SIGNUP,
  query: selectedRole.value ? { role: selectedRole.value } : undefined,
}));

onMounted(() => {
  if (gateway.state.flow === 'login' && gateway.state.payload) {
    selectedRole.value = gateway.state.payload.role;
  }
});

async function continueToGateway() {
  fieldError.value = '';

  if (!selectedRole.value) {
    fieldError.value = 'Pasirinkite naudotojo tipą.';
    showToast(fieldError.value, 'error');
    return;
  }

  const redirect =
    typeof route.query.redirect === 'string' ? route.query.redirect : undefined;

  gateway.start('login', { role: selectedRole.value }, redirect);
  await router.push({ name: ROUTE_NAMES.GATEWAY });
}
</script>

<template>
  <section class="grid w-full max-w-5xl gap-6 lg:grid-cols-[0.9fr_1.1fr]">
    <div class="rounded-lg bg-white p-8 shadow-md">
      <RouterLink
        :to="{ name: ROUTE_NAMES.HOME }"
        aria-label="Į pradžios puslapį"
        class="inline-block">
        <BrandLogo large />
      </RouterLink>
      <p
        class="text-secondary mt-8 text-sm font-semibold tracking-wide uppercase">
        Semėno vartai
      </p>
      <h1 class="mt-3 text-3xl leading-tight font-bold text-gray-950">
        Prisijungimas per Semėno vartus
      </h1>
      <p class="mt-4 leading-7 text-gray-700">
        Pasirinkite naudotojo tipą, kad būtumėte nukreipti į Semėno vartų
        portalą tapatybei patvirtinti.
      </p>

      <div class="border-primary bg-background mt-6 rounded-lg border p-4">
        <div class="flex items-start gap-3">
          <div
            class="bg-attention flex h-10 w-10 shrink-0 items-center justify-center rounded-md text-lg font-bold text-white">
            ID
          </div>
          <div>
            <h2 class="font-semibold text-gray-950">Saugus prisijungimas</h2>
            <p class="mt-1 text-sm leading-6 text-gray-600">
              Slaptažodis ir asmens kodas bus įvedami Semėno vartuose.
            </p>
          </div>
        </div>
      </div>
    </div>

    <form
      class="rounded-lg border border-white/80 bg-white p-8 shadow-md"
      @submit.prevent="continueToGateway">
      <div class="border-b border-gray-200 pb-5">
        <p class="text-secondary text-sm font-semibold tracking-wide uppercase">
          Prisijungimo pasirinkimas
        </p>
        <h2 class="mt-2 text-2xl font-bold text-gray-950">Naudotojo tipas</h2>
      </div>

      <div class="mt-6 grid gap-3">
        <button
          v-for="option in roleOptions"
          :key="option.value"
          class="cursor-pointer rounded-lg border p-4 text-left transition"
          :class="
            selectedRole === option.value
              ? 'border-attention bg-primary shadow-sm'
              : 'hover:border-secondary hover:bg-background border-gray-200 bg-white'
          "
          type="button"
          @click="selectedRole = option.value">
          <span class="flex items-center justify-between gap-4">
            <span>
              <span class="block font-semibold text-gray-950">
                {{ option.label }}
              </span>
              <span class="mt-1 block text-sm leading-6 text-gray-600">
                {{ option.description }}
              </span>
            </span>
            <span
              class="h-4 w-4 rounded-full border"
              :class="
                selectedRole === option.value
                  ? 'border-attention bg-attention'
                  : 'border-gray-300 bg-white'
              " />
          </span>
        </button>
      </div>

      <button
        class="bg-attention hover:bg-secondary mt-6 w-full cursor-pointer rounded-md px-4 py-3 font-semibold text-white transition"
        type="submit">
        Tęsti į Semėno vartus
      </button>

      <p v-if="fieldError" class="mt-4 text-sm text-red-600">
        {{ fieldError }}
      </p>

      <p class="mt-4 text-center text-sm text-gray-600">
        Neturite paskyros?
        <RouterLink class="text-attention font-semibold" :to="signupRoute">
          Registruotis
        </RouterLink>
      </p>
    </form>
  </section>
</template>
