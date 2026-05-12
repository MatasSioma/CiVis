<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BrandLogo from '@/components/BrandLogo.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useGateway, type GatewaySignupPayload } from '@/stores/gateway';
import { useToasts } from '@/stores/toasts';
import type { UserRole } from '@/shared/types';

const router = useRouter();
const route = useRoute();
const gateway = useGateway();
const { showToast } = useToasts();

function getInitialRole(): UserRole {
  return route.query.role === 'employer' || route.query.role === 'job_seeker'
    ? route.query.role
    : 'job_seeker';
}

const form = reactive({
  role: getInitialRole(),
  email: '',
  first_name: '',
  last_name: '',
  company_name: '',
  company_description: '',
});
const errorMessage = ref('');

const roleOptions: { label: string; value: UserRole }[] = [
  { label: 'Darbo ieškantis asmuo', value: 'job_seeker' },
  { label: 'Darbdavys', value: 'employer' },
];

onMounted(() => {
  if (gateway.state.flow === 'signup' && gateway.state.payload) {
    const payload = gateway.state.payload as GatewaySignupPayload;
    form.role = payload.role;
    form.email = payload.email ?? '';
    form.first_name = payload.first_name ?? '';
    form.last_name = payload.last_name ?? '';
    form.company_name = payload.company_name ?? '';
    form.company_description = payload.company_description ?? '';
  }
});

function validateSignup() {
  if (!form.role) {
    return 'Pasirinkite naudotojo tipą.';
  }

  if (!form.first_name.trim()) {
    return 'Įveskite vardą.';
  }

  if (!form.email.trim()) {
    return 'Įveskite el. pašto adresą.';
  }

  if (form.role === 'employer' && !form.company_name.trim()) {
    return 'Įveskite įmonės pavadinimą.';
  }

  return '';
}

async function continueToGateway() {
  errorMessage.value = '';

  const validationError = validateSignup();

  if (validationError) {
    errorMessage.value = validationError;
    showToast(validationError, 'error');
    return;
  }

  gateway.start('signup', {
    role: form.role,
    email: form.email.trim(),
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    company_name:
      form.role === 'employer' ? form.company_name.trim() : undefined,
    company_description:
      form.role === 'employer' ? form.company_description.trim() : undefined,
  });

  await router.push({ name: ROUTE_NAMES.GATEWAY });
}
</script>

<template>
  <form
    class="w-full max-w-[800px] rounded-lg border border-white/70 bg-white p-5 shadow-lg sm:p-6"
    @submit.prevent="continueToGateway">
    <div class="mb-4">
      <RouterLink
        :to="{ name: ROUTE_NAMES.HOME }"
        aria-label="Į pradžios puslapį"
        class="inline-block">
        <BrandLogo />
      </RouterLink>
      <p class="mt-4 text-xs font-semibold uppercase tracking-wide text-secondary">
        CiVis paskyra
      </p>
      <h1 class="mt-1 text-2xl font-bold leading-tight text-gray-950">
        Registracija
      </h1>
      <p class="mt-1 text-sm text-gray-600">
        Užpildykite duomenis, slaptažodį ir asmens kodą įvesite Semėno vartuose.
      </p>
    </div>

    <div class="mb-4 grid grid-cols-2 gap-1 rounded-lg border border-primary bg-background p-1">
      <button
        v-for="option in roleOptions"
        :key="option.value"
        class="rounded-md px-3 py-2 text-sm font-semibold transition"
        :class="
          form.role === option.value
            ? 'bg-white text-attention shadow-sm ring-1 ring-primary'
            : 'text-gray-600 hover:text-gray-950'
        "
        type="button"
        @click="form.role = option.value">
        {{ option.label }}
      </button>
    </div>

    <section>
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary">
        Asmens informacija
      </p>

      <div class="grid gap-3 md:grid-cols-2">
        <label class="block">
          <span class="text-sm font-medium text-gray-700">Vardas</span>
          <input
            v-model="form.first_name"
            autocomplete="given-name"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Įveskite vardą"
            type="text" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Pavardė</span>
          <input
            v-model="form.last_name"
            autocomplete="family-name"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Įveskite pavardę"
            type="text" />
        </label>

        <label class="block md:col-span-2">
          <span class="text-sm font-medium text-gray-700">El. paštas</span>
          <input
            v-model="form.email"
            autocomplete="email"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="vardas@pastas.lt"
            required
            type="email" />
        </label>
      </div>
    </section>

    <section
      v-if="form.role === 'employer'"
      class="mt-4 rounded-lg border border-primary bg-background/70 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary">
        Įmonės informacija
      </p>

      <div class="grid gap-3">
        <label class="block">
          <span class="text-sm font-medium text-gray-700">Įmonės pavadinimas</span>
          <input
            v-model="form.company_name"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Įveskite įmonės pavadinimą"
            required
            type="text" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Įmonės aprašymas</span>
          <textarea
            v-model="form.company_description"
            class="mt-1 min-h-20 w-full resize-y rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Trumpai aprašykite įmonę" />
        </label>
      </div>
    </section>

    <p v-if="errorMessage" class="mt-4 text-sm text-red-600">
      {{ errorMessage }}
    </p>

    <button
      class="mt-4 h-11 w-full rounded-md bg-attention px-4 font-semibold text-white transition hover:bg-secondary"
      type="submit">
      Tęsti į Semėno vartus
    </button>

    <p class="mt-3 text-center text-sm text-gray-600">
      Jau turite paskyrą?
      <RouterLink
        class="font-semibold text-attention underline-offset-4 hover:underline"
        to="/login">
        Prisijungti
      </RouterLink>
    </p>
  </form>
</template>
