<script setup lang="ts">
import StackedLayout from './StackedLayout.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { dashboardRouteName, useAuth } from '@/stores/auth';

const links = [
  { label: 'Home', name: ROUTE_NAMES.HOME },
  { label: 'About', name: ROUTE_NAMES.ABOUT },
];

const auth = useAuth();
</script>

<template>
  <StackedLayout :links="links">
    <template #menu>
      <template v-if="auth.state.user">
        <RouterLink
          class="text-white/80 no-underline hover:text-white"
          :to="{ name: dashboardRouteName(auth.state.user.role) }">
          {{ auth.state.user.role }}
        </RouterLink>
        <button
          class="bg-secondary text-attention hover:bg-secondary rounded px-3 py-1"
          type="button"
          @click="auth.logout">
          Atsijungti
        </button>
      </template>
      <template v-else>
        <RouterLink
          class="text-white/80 no-underline hover:text-white"
          :to="{ name: ROUTE_NAMES.LOGIN }"
          >Login</RouterLink
        >
        <RouterLink
          class="bg-primary text-attention hover:bg-secondary rounded px-3 py-1 no-underline"
          :to="{ name: ROUTE_NAMES.SIGNUP }"
          >Sign Up</RouterLink
        >
      </template>
    </template>
    <main class="mx-auto max-w-7xl px-4 py-6">
      <RouterView />
    </main>
  </StackedLayout>
</template>
