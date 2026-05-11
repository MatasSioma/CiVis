<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ApiError } from '@/services/api';
import { dashboardRouteName, useAuth } from '@/stores/auth';
import type { UserRole } from '@/shared/types';

const router = useRouter();
const auth = useAuth();

const form = reactive({
  role: 'jobseeker' as UserRole,
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
  { label: 'Kandidatas', value: 'jobseeker' },
  { label: 'Darbdavys', value: 'employer' },
];

const canSubmit = computed(() => {
  const hasRequiredUserFields =
    form.personal_code.trim() &&
    form.email.trim() &&
    form.password &&
    form.password_confirm &&
    form.password === form.password_confirm;
  const hasCompany = form.role === 'jobseeker' || form.company_name.trim();

  return Boolean(hasRequiredUserFields && hasCompany);
});

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

async function submitSignup() {
  errorMessage.value = '';

  if (form.password !== form.password_confirm) {
    errorMessage.value = 'Slaptazodziai nesutampa.';
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

    await router.push({ name: dashboardRouteName(user.role) });
  } catch (error) {
    errorMessage.value = getErrorMessage(error);
  }
}
</script>

<template>
  <form
    class="w-full max-w-2xl rounded-lg bg-white p-8 shadow-md"
    @submit.prevent="submitSignup">
    <div class="mb-6">
      <p class="text-sm font-semibold uppercase tracking-wide text-lime-moss">
        CiVis
      </p>
      <h1 class="mt-2 text-2xl font-bold text-gray-950">Registracija</h1>
    </div>

    <div class="mb-6 grid grid-cols-2 gap-2 rounded-lg bg-primary p-1">
      <button
        v-for="option in roleOptions"
        :key="option.value"
        class="rounded-md px-4 py-2 text-sm font-semibold transition"
        :class="
          form.role === option.value
            ? 'bg-white text-attention shadow-sm'
            : 'text-gray-600 hover:text-gray-950'
        "
        type="button"
        @click="form.role = option.value">
        {{ option.label }}
      </button>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <label class="block">
        <span class="text-sm font-medium text-gray-700">Vardas</span>
        <input
          v-model="form.first_name"
          autocomplete="given-name"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
          type="text" />
      </label>

      <label class="block">
        <span class="text-sm font-medium text-gray-700">Pavarde</span>
        <input
          v-model="form.last_name"
          autocomplete="family-name"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
          type="text" />
      </label>

      <label class="block">
        <span class="text-sm font-medium text-gray-700">Asmens kodas</span>
        <input
          v-model="form.personal_code"
          autocomplete="username"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
          inputmode="numeric"
          required
          type="text" />
      </label>

      <label class="block">
        <span class="text-sm font-medium text-gray-700">El. pastas</span>
        <input
          v-model="form.email"
          autocomplete="email"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
          required
          type="email" />
      </label>

      <label class="block">
        <span class="text-sm font-medium text-gray-700">Slaptazodis</span>
        <input
          v-model="form.password"
          autocomplete="new-password"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
          required
          type="password" />
      </label>

      <label class="block">
        <span class="text-sm font-medium text-gray-700">Pakartoti slaptazodi</span>
        <input
          v-model="form.password_confirm"
          autocomplete="new-password"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
          required
          type="password" />
      </label>

      <template v-if="form.role === 'employer'">
        <label class="block md:col-span-2">
          <span class="text-sm font-medium text-gray-700">Imones pavadinimas</span>
          <input
            v-model="form.company_name"
            class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary"
            required
            type="text" />
        </label>

        <label class="block md:col-span-2">
          <span class="text-sm font-medium text-gray-700">Imones aprasymas</span>
          <textarea
            v-model="form.company_description"
            class="mt-1 min-h-24 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-lime-moss focus:ring-2 focus:ring-secondary" />
        </label>
      </template>
    </div>

    <p v-if="errorMessage" class="mt-4 text-sm text-red-600">
      {{ errorMessage }}
    </p>

    <button
      class="mt-6 w-full rounded-md bg-attention px-4 py-2 font-semibold text-white transition hover:bg-lime-moss disabled:cursor-not-allowed disabled:bg-gray-300"
      :disabled="!canSubmit || auth.state.isLoading"
      type="submit">
      {{ auth.state.isLoading ? 'Kuriama...' : 'Sukurti paskyra' }}
    </button>

    <p class="mt-4 text-center text-sm text-gray-600">
      Jau turite paskyra?
      <RouterLink class="font-semibold text-attention" to="/login">
        Prisijungti
      </RouterLink>
    </p>
  </form>
</template>
