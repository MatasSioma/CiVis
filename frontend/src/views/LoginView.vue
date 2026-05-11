<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ApiError } from '@/services/api';
import { dashboardRouteName, useAuth } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const auth = useAuth();

const form = reactive({
  personal_code: '',
  password: '',
});
const errorMessage = ref('');

const canSubmit = computed(
  () => form.personal_code.trim().length > 0 && form.password.length > 0,
);

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.details) {
    const details = error.details as { non_field_errors?: string[]; detail?: string };

    return details.non_field_errors?.[0] ?? details.detail ?? 'Prisijungti nepavyko.';
  }

  return 'Prisijungti nepavyko.';
}

async function submitLogin() {
  errorMessage.value = '';

  try {
    const user = await auth.login(form);

    if (!user) {
      errorMessage.value = 'Sesija nesukurta.';
      return;
    }

    await router.push(
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : { name: dashboardRouteName(user.role) },
    );
  } catch (error) {
    errorMessage.value = getErrorMessage(error);
  }
}
</script>

<template>
  <form
    class="w-full max-w-md rounded-lg bg-white p-8 shadow-md"
    @submit.prevent="submitLogin">
    <div class="mb-6">
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        CiVis
      </p>
      <h1 class="mt-2 text-2xl font-bold text-gray-950">Prisijungimas</h1>
    </div>

    <div class="space-y-4">
      <label class="block">
        <span class="text-sm font-medium text-gray-700">Asmens kodas</span>
        <input
          v-model="form.personal_code"
          autocomplete="username"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-secondary focus:ring-2 focus:ring-secondary"
          inputmode="numeric"
          name="personal_code"
          required
          type="text" />
      </label>

      <label class="block">
        <span class="text-sm font-medium text-gray-700">Slaptazodis</span>
        <input
          v-model="form.password"
          autocomplete="current-password"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-secondary focus:ring-2 focus:ring-secondary"
          name="password"
          required
          type="password" />
      </label>
    </div>

    <p v-if="errorMessage" class="mt-4 text-sm text-red-600">
      {{ errorMessage }}
    </p>

    <button
      class="mt-6 w-full rounded-md bg-attention px-4 py-2 font-semibold text-white transition hover:bg-secondary disabled:cursor-not-allowed disabled:bg-gray-300"
      :disabled="!canSubmit || auth.state.isLoading"
      type="submit">
      {{ auth.state.isLoading ? 'Jungiama...' : 'Prisijungti' }}
    </button>

    <p class="mt-4 text-center text-sm text-gray-600">
      Neturite paskyros?
      <RouterLink class="font-semibold text-attention" to="/signup">
        Registruotis
      </RouterLink>
    </p>
  </form>
</template>
