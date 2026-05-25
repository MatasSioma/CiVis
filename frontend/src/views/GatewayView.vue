<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ApiError } from '@/services/api';
import { dashboardRouteName, getRoleLabel, useAuth } from '@/stores/auth';
import { useGateway, type GatewaySignupPayload } from '@/stores/gateway';
import { useToasts } from '@/stores/toasts';

const router = useRouter();
const auth = useAuth();
const gateway = useGateway();
const { showToast } = useToasts();

const personalCode = ref('');
const password = ref('');
const passwordConfirm = ref('');
const fieldError = ref('');

if (import.meta.env.DEV) {
  console.debug('[view] GatewayView setup');
}

onMounted(() => {
  if (import.meta.env.DEV) {
    console.debug('[view] GatewayView mounted', {
      hasFlow: gateway.hasFlow.value,
      flow: gateway.state.flow,
    });
  }

  if (!gateway.hasFlow.value) {
    router.replace({ name: ROUTE_NAMES.LOGIN });
  }
});

onBeforeUnmount(() => {
  if (import.meta.env.DEV) {
    console.debug('[view] GatewayView beforeUnmount');
  }
});

const flow = computed(() => gateway.state.flow);
const isSignup = computed(() => flow.value === 'signup');

const title = computed(() =>
  isSignup.value ? 'Registracija' : 'Prisijungimas',
);
const subtitle = computed(() =>
  isSignup.value
    ? 'Lietuvos Respublikos piliečiui — patvirtinkite tapatybę, kad užbaigtumėte registraciją.'
    : 'Lietuvos Respublikos piliečiui — patvirtinkite tapatybę, kad galėtumėte prisijungti.',
);
const submitLabel = computed(() =>
  isSignup.value ? 'Registruotis' : 'Prisijungti',
);
const loadingLabel = computed(() =>
  isSignup.value ? 'Kuriama...' : 'Jungiama...',
);

const summaryRows = computed<{ label: string; value: string }[]>(() => {
  const payload = gateway.state.payload;

  if (!payload) {
    return [];
  }

  const rows: { label: string; value: string }[] = [
    { label: 'Naudotojo tipas', value: getRoleLabel(payload.role) },
  ];

  if (isSignup.value) {
    const signupPayload = payload as GatewaySignupPayload;

    if (signupPayload.first_name) {
      rows.push({ label: 'Vardas', value: signupPayload.first_name });
    }

    if (signupPayload.last_name) {
      rows.push({ label: 'Pavardė', value: signupPayload.last_name });
    }

    if (signupPayload.email) {
      rows.push({ label: 'El. paštas', value: signupPayload.email });
    }

    if (signupPayload.role === 'job_seeker' && signupPayload.date_of_birth) {
      rows.push({ label: 'Gimimo data', value: signupPayload.date_of_birth });
    }

    if (signupPayload.role === 'employer') {
      if (signupPayload.company_name) {
        rows.push({
          label: 'Įmonės pavadinimas',
          value: signupPayload.company_name,
        });
      }

      if (signupPayload.company_description) {
        rows.push({
          label: 'Įmonės aprašymas',
          value: signupPayload.company_description,
        });
      }
    }
  }

  return rows;
});

function validate() {
  const code = personalCode.value.trim();

  if (!code) {
    return 'Įveskite asmens kodą.';
  }

  if (!/^\d{11}$/.test(code)) {
    return 'Asmens kodą turi sudaryti 11 skaitmenų.';
  }

  if (!password.value) {
    return isSignup.value
      ? 'Slaptažodis negali būti tuščias.'
      : 'Įveskite slaptažodį.';
  }

  if (isSignup.value && password.value !== passwordConfirm.value) {
    return 'Slaptažodžiai nesutampa.';
  }

  return '';
}

function getLoginErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.details) {
    const details = error.details as {
      non_field_errors?: string[];
      detail?: string;
    };

    return (
      details.non_field_errors?.[0] ??
      details.detail ??
      'Nepavyko prisijungti. Patikrinkite įvestus duomenis.'
    );
  }

  return 'Nepavyko prisijungti. Patikrinkite įvestus duomenis.';
}

function getSignupErrorMessage(error: unknown) {
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

async function submit() {
  fieldError.value = '';

  if (!gateway.hasFlow.value || !gateway.state.payload || !gateway.state.flow) {
    router.replace({ name: ROUTE_NAMES.LOGIN });
    return;
  }

  const validationError = validate();

  if (validationError) {
    fieldError.value = validationError;
    showToast(validationError, 'error');
    return;
  }

  const code = personalCode.value.trim();

  try {
    if (gateway.state.flow === 'signup') {
      const signupPayload = gateway.state.payload as GatewaySignupPayload;
      const user = await auth.signup({
        role: signupPayload.role,
        email: signupPayload.email,
        first_name: signupPayload.first_name,
        last_name: signupPayload.last_name,
        password: password.value,
        personal_code: code,
        date_of_birth:
          signupPayload.role === 'job_seeker'
            ? signupPayload.date_of_birth
            : undefined,
        company_name:
          signupPayload.role === 'employer'
            ? signupPayload.company_name
            : undefined,
        company_description:
          signupPayload.role === 'employer'
            ? signupPayload.company_description
            : undefined,
      });

      if (!user) {
        fieldError.value = 'Sesija nesukurta.';
        return;
      }

      gateway.clear();
      showToast('Registracija sėkminga.', 'success');
      await router.push({ name: dashboardRouteName(user.role) });
      return;
    }

    const user = await auth.login({
      role: gateway.state.payload.role,
      password: password.value,
      personal_code: code,
    });

    if (!user) {
      throw new Error('Missing user');
    }

    const redirect = gateway.state.redirect;
    gateway.clear();
    showToast('Sėkmingai prisijungėte.', 'success');

    await router.push(
      redirect && typeof redirect === 'string'
        ? redirect
        : { name: dashboardRouteName(user.role) },
    );
  } catch (error) {
    const message =
      gateway.state.flow === 'signup'
        ? getSignupErrorMessage(error)
        : getLoginErrorMessage(error);
    fieldError.value = message;
    showToast(message, 'error');
  }
}

function cancel() {
  const targetName = isSignup.value ? ROUTE_NAMES.SIGNUP : ROUTE_NAMES.LOGIN;
  const redirect = gateway.state.redirect;
  router.push({
    name: targetName,
    query: redirect ? { redirect } : undefined,
  });
}
</script>

<template>
  <div
    class="font-gateway fixed inset-0 z-10 overflow-y-auto bg-[#F5F7FA] text-[#1A1A1A]">
    <header
      class="border-b-4 border-[#FFC107] bg-[#1F4E79] text-white shadow-sm">
      <div class="mx-auto flex max-w-4xl items-center gap-3 px-6 py-3">
        <span
          class="flex h-9 w-9 items-center justify-center rounded-sm bg-[#FFC107] text-sm font-bold text-[#1F4E79]"
          aria-hidden="true">
          SV
        </span>
        <div class="leading-tight">
          <p class="text-base font-bold tracking-wide">Semėno vartai</p>
          <p class="text-xs text-[#C9D9EA]">Elektroninių paslaugų portalas</p>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-8 sm:py-12">
      <p
        class="text-xs font-semibold tracking-[0.18em] text-[#1F4E79] uppercase">
        E. valdžios vartų imitacija
      </p>
      <h1
        class="mt-2 text-3xl font-bold tracking-tight text-[#1A1A1A] sm:text-4xl">
        {{ title }}
      </h1>
      <p class="mt-2 max-w-2xl text-[15px] leading-7 text-[#3D3D3D]">
        {{ subtitle }}
      </p>

      <details
        class="mt-6 rounded-md border border-[#D1D9E0] bg-white shadow-sm">
        <summary
          class="flex cursor-pointer list-none items-center justify-between gap-3 px-5 py-3 text-sm font-semibold text-[#1F4E79] hover:bg-[#F0F4F8]">
          <span>Peržiūrėti įvestus duomenis</span>
          <span
            class="rounded-sm border border-[#C7D2DC] px-2 py-0.5 text-[11px] font-medium tracking-wider text-[#5A6B7B] uppercase">
            {{ summaryRows.length }}
            {{ summaryRows.length === 1 ? 'įrašas' : 'įrašai' }}
          </span>
        </summary>
        <dl
          class="divide-y divide-[#E5EAF0] border-t border-[#E5EAF0] px-5 py-3 text-sm">
          <div
            v-for="row in summaryRows"
            :key="row.label"
            class="grid grid-cols-1 gap-1 py-2 sm:grid-cols-[200px_1fr] sm:items-baseline sm:gap-4">
            <dt
              class="text-[13px] font-medium tracking-wide text-[#5A6B7B] uppercase">
              {{ row.label }}
            </dt>
            <dd class="wrap-break-word whitespace-pre-wrap text-[#1A1A1A]">
              {{ row.value }}
            </dd>
          </div>
        </dl>
      </details>

      <h2
        class="mt-8 text-sm font-semibold tracking-[0.16em] text-[#1F4E79] uppercase">
        Pasirinkite prisijungimo būdą
      </h2>

      <form
        class="mt-3 overflow-hidden rounded-md border border-[#D1D9E0] bg-white shadow-sm"
        @submit.prevent="submit">
        <div
          class="flex items-center gap-3 border-b border-[#E5EAF0] bg-[#F7F9FC] px-5 py-3">
          <span
            class="flex h-8 w-8 items-center justify-center rounded-sm bg-[#1F4E79] text-xs font-bold text-white"
            aria-hidden="true">
            AK
          </span>
          <div>
            <p class="text-sm font-semibold text-[#1A1A1A]">Asmens kodas</p>
            <p class="text-xs text-[#5A6B7B]">
              Prisijungimas naudojant asmens kodą ir slaptažodį
            </p>
          </div>
        </div>

        <div class="grid gap-4 px-5 py-5">
          <label class="block">
            <span class="text-sm font-semibold text-[#1A1A1A]"
              >Asmens kodas</span
            >
            <input
              v-model="personalCode"
              autocomplete="username"
              class="mt-1 h-11 w-full rounded-sm border border-[#C7D2DC] bg-white px-3 text-[15px] text-[#1A1A1A] transition outline-none placeholder:text-[#8A98A6] focus:border-[#1F4E79] focus:ring-2 focus:ring-[#FFC107]/60"
              inputmode="numeric"
              maxlength="11"
              placeholder="11 skaitmenų"
              type="text" />
          </label>

          <label class="block">
            <span class="text-sm font-semibold text-[#1A1A1A]"
              >Slaptažodis</span
            >
            <input
              v-model="password"
              :autocomplete="isSignup ? 'new-password' : 'current-password'"
              class="mt-1 h-11 w-full rounded-sm border border-[#C7D2DC] bg-white px-3 text-[15px] text-[#1A1A1A] transition outline-none placeholder:text-[#8A98A6] focus:border-[#1F4E79] focus:ring-2 focus:ring-[#FFC107]/60"
              placeholder="Įveskite slaptažodį"
              type="password" />
          </label>

          <label v-if="isSignup" class="block">
            <span class="text-sm font-semibold text-[#1A1A1A]"
              >Pakartoti slaptažodį</span
            >
            <input
              v-model="passwordConfirm"
              autocomplete="new-password"
              class="mt-1 h-11 w-full rounded-sm border border-[#C7D2DC] bg-white px-3 text-[15px] text-[#1A1A1A] transition outline-none placeholder:text-[#8A98A6] focus:border-[#1F4E79] focus:ring-2 focus:ring-[#FFC107]/60"
              placeholder="Pakartokite slaptažodį"
              type="password" />
          </label>

          <p v-if="fieldError" class="text-sm font-medium text-[#B23A48]">
            {{ fieldError }}
          </p>

          <button
            class="mt-1 h-11 w-full cursor-pointer rounded-sm bg-[#1F4E79] px-4 font-semibold tracking-wide text-white uppercase transition hover:bg-[#15375A] focus:ring-2 focus:ring-[#FFC107] focus:outline-none disabled:cursor-not-allowed disabled:bg-[#8A98A6]"
            :disabled="auth.state.isLoading"
            type="submit">
            {{ auth.state.isLoading ? loadingLabel : submitLabel }}
          </button>
        </div>
      </form>

      <button
        class="mt-4 cursor-pointer text-sm font-semibold text-[#1F4E79] underline-offset-4 hover:underline"
        type="button"
        @click="cancel">
        ← Atšaukti ir grįžti
      </button>

      <p
        class="mt-10 border-t border-[#E5EAF0] pt-4 text-center text-xs text-[#5A6B7B]">
        Šis puslapis yra elektroninių valdžios vartų imitacija edukaciniais
        tikslais ir nesusijęs su Lietuvos Respublikos elektroninių valdžios
        vartų portalu.
      </p>
    </main>
  </div>
</template>

<style scoped>
.font-gateway {
  font-family:
    'Open Sans',
    -apple-system,
    'Segoe UI',
    Roboto,
    sans-serif;
}

.font-gateway summary::-webkit-details-marker {
  display: none;
}

.font-gateway details[open] > summary > span:first-child::before {
  content: '▾ ';
}

.font-gateway details:not([open]) > summary > span:first-child::before {
  content: '▸ ';
}
</style>
