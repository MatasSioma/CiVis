<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ApiError } from '@/services/api';
import { dashboardRouteName, useAuth } from '@/stores/auth';
import { useToasts } from '@/stores/toasts';
import type { UserRole } from '@/shared/types';

const router = useRouter();
const route = useRoute();
const auth = useAuth();
const { showToast } = useToasts();

function getInitialRole(): UserRole {
  return route.query.role === 'employer' || route.query.role === 'job_seeker'
    ? route.query.role
    : 'job_seeker';
}

const form = reactive({
  role: getInitialRole(),
  personal_code: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  company_name: '',
  company_description: '',
});
const errorMessage = ref('');

const roleOptions: { label: string; value: UserRole }[] = [
  { label: 'Darbo ieškantis asmuo', value: 'job_seeker' },
  { label: 'Darbdavys', value: 'employer' },
];

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.details) {
    const details = error.details as Record<string, string[] | string>;
    const firstValue = Object.values(details)[0];

    if (Array.isArray(firstValue)) {
      return firstValue[0] ?? 'Registracija nepavyko.';
    }

    if (typeof firstValue === 'string') {
      return firstValue;
    }
  }

  return 'Registracija nepavyko.';
}

function validateSignup() {
  if (!form.role) {
    return 'Pasirinkite naudotojo tipą.';
  }

  if (!form.first_name.trim()) {
    return 'Įveskite vardą.';
  }

  if (!form.personal_code.trim()) {
    return 'Įveskite asmens kodą.';
  }

  if (!/^\d{11}$/.test(form.personal_code.trim())) {
    return 'Asmens kodą turi sudaryti 11 skaitmenų.';
  }

  if (!form.email.trim()) {
    return 'Įveskite el. pašto adresą.';
  }

  if (!form.password) {
    return 'Slaptažodis negali būti tuščias.';
  }

  if (form.password !== form.password_confirm) {
    return 'Slaptažodžiai nesutampa.';
  }

  if (form.role === 'employer' && !form.company_name.trim()) {
    return 'Įveskite įmonės pavadinimą.';
  }

  return '';
}

async function submitSignup() {
  errorMessage.value = '';

  const validationError = validateSignup();

  if (validationError) {
    errorMessage.value = validationError;
    showToast(validationError, 'error');
    return;
  }

  try {
    const user = await auth.signup({
      role: form.role,
      personal_code: form.personal_code,
      email: form.email,
      first_name: form.first_name,
      last_name: form.last_name,
      password: form.password,
      company_name: form.role === 'employer' ? form.company_name : undefined,
      company_description:
        form.role === 'employer' ? form.company_description : undefined,
    });

    if (!user) {
      errorMessage.value = 'Sesija nesukurta.';
      return;
    }

    showToast('Registracija sėkminga.', 'success');
    await router.push({ name: dashboardRouteName(user.role) });
  } catch (error) {
    errorMessage.value = getErrorMessage(error);
    showToast('Registracija nepavyko. Patikrinkite įvestus duomenis.', 'error');
  }
}
</script>

<template>
  <form
    class="w-full max-w-[800px] rounded-lg border border-white/70 bg-white p-5 shadow-lg sm:p-6"
    @submit.prevent="submitSignup">
    <div class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
        CiVis paskyra
      </p>
      <h1 class="mt-1 text-2xl font-bold leading-tight text-gray-950">
        Registracija
      </h1>
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

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Asmens kodas</span>
          <input
            v-model="form.personal_code"
            autocomplete="username"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            inputmode="numeric"
            maxlength="11"
            placeholder="Įveskite 11 skaitmenų asmens kodą"
            required
            type="text" />
        </label>

        <label class="block">
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

    <section class="mt-4">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary">
        Prisijungimo duomenys
      </p>

      <div class="grid gap-3 md:grid-cols-2">
        <label class="block">
          <span class="text-sm font-medium text-gray-700">Slaptažodis</span>
          <input
            v-model="form.password"
            autocomplete="new-password"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Įveskite slaptažodį"
            required
            type="password" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Pakartoti slaptažodį</span>
          <input
            v-model="form.password_confirm"
            autocomplete="new-password"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Pakartokite slaptažodį"
            required
            type="password" />
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
      class="mt-4 h-11 w-full rounded-md bg-attention px-4 font-semibold text-white transition hover:bg-secondary disabled:cursor-not-allowed disabled:bg-gray-300"
      :disabled="auth.state.isLoading"
      type="submit">
      {{ auth.state.isLoading ? 'Kuriama...' : 'Sukurti paskyrą' }}
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
