<script setup lang="ts">
import { useAuth } from '@/stores/auth';

const { state } = useAuth();
</script>

<template>
  <section class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Kandidato paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ state.user?.first_name || state.user?.email }}
      </h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">CV</h2>
        <p class="mt-2 text-sm text-gray-600">
          Kandidato profilis ir CV duomenys bus susieti su sia sesija.
        </p>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Paraiskos</h2>
        <p class="mt-2 text-sm text-gray-600">
          Matysite tik savo darbo paraiskas.
        </p>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Role</h2>
        <p class="mt-2 text-sm text-gray-600">{{ state.user?.role }}</p>
      </article>
    </div>
  </section>
</template>
