<script setup lang="ts">
import { useAuth } from '@/stores/auth';

const { state } = useAuth();
</script>

<template>
  <section class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-lime-moss">
        Darbdavio paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ state.user?.first_name || state.user?.email }}
      </h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Imone</h2>
        <p class="mt-2 text-sm text-gray-600">
          Imones ir darbo skelbimu duomenys bus filtruojami pagal jusu sesija.
        </p>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Skelbimai</h2>
        <p class="mt-2 text-sm text-gray-600">
          Darbdavys valdys tik savo imones skelbimus.
        </p>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-950">Role</h2>
        <p class="mt-2 text-sm text-gray-600">{{ state.user?.role }}</p>
      </article>
    </div>
  </section>
</template>
