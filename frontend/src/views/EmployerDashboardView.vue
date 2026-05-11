<script setup lang="ts">
import { computed } from 'vue';
import { getRoleLabel, useAuth } from '@/stores/auth';

const { state } = useAuth();
const user = computed(() => state.user);
</script>

<template>
  <section v-if="user" class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Darbdavio paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ user.first_name || user.email }}
      </h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Įmonė</h2>
        <p class="mt-2 text-sm text-gray-600">
          Įmonės ir darbo skelbimų duomenys filtruojami pagal jūsų sesiją.
        </p>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Skelbimai</h2>
        <p class="mt-2 text-sm text-gray-600">
          Darbdavys valdo tik savo įmonės skelbimus.
        </p>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Rolė</h2>
        <p class="mt-2 text-sm text-gray-600">{{ getRoleLabel(user.role) }}</p>
      </article>
    </div>
  </section>
  <section v-else class="rounded-lg bg-white p-6 text-gray-700 shadow-sm">
    Paskyros būsena atnaujinama.
  </section>
</template>
