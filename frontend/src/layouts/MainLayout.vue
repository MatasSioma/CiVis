<script setup lang="ts">
import StackedLayout from './StackedLayout.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';

const links = [
  { label: 'Home', name: ROUTE_NAMES.HOME },
  { label: 'About', name: ROUTE_NAMES.ABOUT },
];
</script>

<template>
  <StackedLayout :links="links">
    <template #menu>
      <RouterLink
        class="text-white/80 no-underline hover:text-white"
        :to="{ name: ROUTE_NAMES.LOGIN }"
        >Login</RouterLink
      >
      <RouterLink
        class="rounded bg-white px-3 py-1 text-blue-600 no-underline hover:bg-white/90"
        :to="{ name: ROUTE_NAMES.SIGNUP }"
        >Sign Up</RouterLink
      >
    </template>
    <main class="mx-auto max-w-7xl px-4 py-6">
      <RouterView />
    </main>
  </StackedLayout>
</template>
