<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BrandLogo from '@/components/BrandLogo.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ApiError } from '@/services/api';
import { dashboardRouteName, getRoleLabel, useAuth } from '@/stores/auth';
import { useToasts } from '@/stores/toasts';
import type { UserRole } from '@/shared/types';

type LoginStep = 'role' | 'identity';

const route = useRoute();
const router = useRouter();
const auth = useAuth();
const { showToast } = useToasts();

const currentStep = ref<LoginStep>('role');
const selectedRole = ref<UserRole | null>(null);
const identityForm = reactive({
  personalCode: '',
  password: '',
});
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

const selectedRoleLabel = computed(() => getRoleLabel(selectedRole.value));
const isIdentityStep = computed(() => currentStep.value === 'identity');
const alternativeRole = computed<UserRole>(() =>
  selectedRole.value === 'employer' ? 'job_seeker' : 'employer',
);
const alternativeRoleLabel = computed(() => getRoleLabel(alternativeRole.value));
const signupRoute = computed(() => ({
  name: ROUTE_NAMES.SIGNUP,
  query: selectedRole.value ? { role: selectedRole.value } : undefined,
}));

function clearIdentityForm() {
  fieldError.value = '';
  identityForm.personalCode = '';
  identityForm.password = '';
}

function continueToIdentity() {
  fieldError.value = '';

  if (!selectedRole.value) {
    fieldError.value = 'Pasirinkite naudotojo tipą.';
    showToast(fieldError.value, 'error');
    return;
  }

  currentStep.value = 'identity';
}

function switchRole() {
  selectedRole.value = alternativeRole.value;
  clearIdentityForm();
}

function validateIdentity() {
  const personalCode = identityForm.personalCode.trim();

  if (!personalCode) {
    return 'Įveskite asmens kodą.';
  }

  if (!/^\d{11}$/.test(personalCode)) {
    return 'Asmens kodą turi sudaryti 11 skaitmenų.';
  }

  if (!identityForm.password) {
    return 'Įveskite slaptažodį.';
  }

  return '';
}

function getLoginErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.details) {
    const details = error.details as { non_field_errors?: string[]; detail?: string };

    return (
      details.non_field_errors?.[0] ??
      details.detail ??
      'Nepavyko prisijungti. Patikrinkite įvestus duomenis.'
    );
  }

  return 'Nepavyko prisijungti. Patikrinkite įvestus duomenis.';
}

async function submitLogin() {
  fieldError.value = '';

  if (!selectedRole.value) {
    fieldError.value = 'Pasirinkite naudotojo tipą.';
    showToast(fieldError.value, 'error');
    currentStep.value = 'role';
    return;
  }

  const validationError = validateIdentity();

  if (validationError) {
    fieldError.value = validationError;
    showToast(validationError, 'error');
    return;
  }

  try {
    const user = await auth.login({
      personal_code: identityForm.personalCode.trim(),
      password: identityForm.password,
      role: selectedRole.value,
    });

    if (!user) {
      throw new Error('Missing user');
    }

    showToast('Sėkmingai prisijungėte.', 'success');

    await router.push(
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : { name: dashboardRouteName(user.role) },
    );
  } catch (error) {
    const errorMessage = getLoginErrorMessage(error);
    fieldError.value = errorMessage;
    showToast(errorMessage, 'error');
  }
}
</script>

<template>
  <section class="grid w-full max-w-5xl gap-6 lg:grid-cols-[0.9fr_1.1fr]">
    <div class="rounded-lg bg-white p-8 shadow-md">
      <BrandLogo large />
      <p class="mt-8 text-sm font-semibold uppercase tracking-wide text-secondary">
        Semėno vartai
      </p>
      <h1 class="mt-3 text-3xl font-bold leading-tight text-gray-950">
        Prisijungimas per Semėno vartus
      </h1>
      <p class="mt-4 leading-7 text-gray-700">
        Pasirinkite naudotojo tipą ir patvirtinkite tapatybę, kad galėtumėte
        naudotis CiVis sistema.
      </p>

      <div class="mt-6 rounded-lg border border-primary bg-background p-4">
        <div class="flex items-start gap-3">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-attention text-lg font-bold text-white">
            ID
          </div>
          <div>
            <h2 class="font-semibold text-gray-950">Saugus prisijungimas</h2>
            <p class="mt-1 text-sm leading-6 text-gray-600">
              Įveskite prisijungimo duomenis, kad tęstumėte.
            </p>
          </div>
        </div>
      </div>
    </div>

    <form
      class="rounded-lg border border-white/80 bg-white p-8 shadow-md"
      @submit.prevent="isIdentityStep ? submitLogin() : continueToIdentity()">
      <div class="border-b border-gray-200 pb-5">
        <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
          {{ isIdentityStep ? 'Tapatybės patvirtinimas' : 'Prisijungimo pasirinkimas' }}
        </p>
        <h2 class="mt-2 text-2xl font-bold text-gray-950">
          {{ isIdentityStep ? 'Tapatybės patvirtinimas' : 'Naudotojo tipas' }}
        </h2>
      </div>

      <template v-if="!isIdentityStep">
        <div class="mt-6 grid gap-3">
          <button
            v-for="option in roleOptions"
            :key="option.value"
            class="rounded-lg border p-4 text-left transition"
            :class="
              selectedRole === option.value
                ? 'border-attention bg-primary shadow-sm'
                : 'border-gray-200 bg-white hover:border-secondary hover:bg-background'
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
          class="mt-6 w-full rounded-md bg-attention px-4 py-3 font-semibold text-white transition hover:bg-secondary"
          type="submit">
          Tęsti
        </button>
      </template>

      <template v-else>
        <div class="mt-6 rounded-lg bg-background p-4 text-sm text-gray-700">
          Prisijungiate kaip:
          <span class="font-semibold text-gray-950">{{ selectedRoleLabel }}</span>
        </div>

        <div class="mt-5 grid gap-4">
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Asmens kodas</span>
            <input
              v-model="identityForm.personalCode"
              autocomplete="username"
              class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-secondary focus:ring-2 focus:ring-secondary"
              inputmode="numeric"
              maxlength="11"
              type="text" />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">Slaptažodis</span>
            <input
              v-model="identityForm.password"
              autocomplete="current-password"
              class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-secondary focus:ring-2 focus:ring-secondary"
              type="password" />
          </label>
        </div>

        <button
          class="mt-6 w-full rounded-md bg-attention px-4 py-3 font-semibold text-white transition hover:bg-secondary disabled:cursor-not-allowed disabled:bg-gray-300"
          :disabled="auth.state.isLoading"
          type="submit">
          {{ auth.state.isLoading ? 'Jungiama...' : 'Prisijungti' }}
        </button>

        <div class="mt-4 text-center">
          <button
            class="text-sm font-semibold text-attention underline-offset-4 hover:underline"
            type="button"
            @click="switchRole">
            Jungtis kaip {{ alternativeRoleLabel.toLowerCase() }}
          </button>
        </div>
      </template>

      <p v-if="fieldError" class="mt-4 text-sm text-red-600">
        {{ fieldError }}
      </p>

      <p class="mt-4 text-center text-sm text-gray-600">
        Neturite paskyros?
        <RouterLink class="font-semibold text-attention" :to="signupRoute">
          Registruotis
        </RouterLink>
      </p>
    </form>
  </section>
</template>
