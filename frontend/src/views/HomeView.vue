<script setup lang="ts">
import { watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { dashboardRouteName, useAuth } from '@/stores/auth';

const auth = useAuth();
const router = useRouter();

watchEffect(() => {
  if (auth.state.user) {
    router.replace({ name: dashboardRouteName(auth.state.user.role) });
  }
});
</script>

<template>
  <section
    v-if="!auth.state.user"
    class="grid min-h-[calc(100vh-112px)] items-center gap-10 py-10 lg:grid-cols-[1.1fr_0.9fr]">
    <div class="max-w-2xl">
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Darbo paieškos ir įdarbinimo sistema
      </p>
      <h1 class="mt-3 text-4xl font-bold leading-tight text-gray-950 md:text-5xl">
        Darbo paieška ir kandidatų atranka vienoje vietoje
      </h1>
      <p class="mt-5 text-lg leading-8 text-gray-700">
        Platforma padeda darbo ieškantiems asmenims pristatyti savo patirtį, o
        darbdaviams patogiai valdyti įmonės skelbimus ir paraiškas.
      </p>

      <div class="mt-8 flex flex-wrap gap-3">
        <RouterLink
          class="rounded-md bg-attention px-5 py-3 font-semibold text-white no-underline transition hover:bg-secondary"
          :to="{ name: ROUTE_NAMES.LOGIN }">
          Prisijungti
        </RouterLink>
        <RouterLink
          class="rounded-md bg-primary px-5 py-3 font-semibold text-attention no-underline transition hover:bg-secondary"
          :to="{ name: ROUTE_NAMES.SIGNUP }">
          Registruotis
        </RouterLink>
      </div>
    </div>

    <div class="grid gap-4">
      <article class="rounded-lg border border-white/70 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Darbo ieškantiems asmenims</h2>
        <p class="mt-2 text-sm leading-6 text-gray-600">
          Kurkite profilį, valdykite CV ir sekite savo paraiškas be papildomo
          triukšmo.
        </p>
      </article>
      <article class="rounded-lg border border-white/70 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Darbdaviams</h2>
        <p class="mt-2 text-sm leading-6 text-gray-600">
          Tvarkykite įmonės informaciją, skelbimus ir kandidatų paraiškas vienoje
          darbo erdvėje.
        </p>
      </article>
    </div>
  </section>
</template>
