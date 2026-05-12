<script setup lang="ts">
import StackedLayout from './StackedLayout.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { useRouter } from 'vue-router';
import { dashboardRouteName, getRoleLabel, useAuth } from '@/stores/auth';
import { useToasts } from '@/stores/toasts';

const links = [
  { label: 'Pradžia', name: ROUTE_NAMES.HOME },
  { label: 'Apie', name: ROUTE_NAMES.ABOUT },
];

const auth = useAuth();
const router = useRouter();
const { showToast } = useToasts();

async function handleLogout() {
  try {
    await auth.logout();
  } catch {
    // Local auth state is cleared in the store even when the server session is already gone.
  } finally {
    await router.push({ name: ROUTE_NAMES.HOME });
    showToast('Sėkmingai atsijungėte.', 'success');
  }
}
</script>

<template>
  <StackedLayout :links="links">
    <template #menu>
      <template v-if="auth.state.user">
        <RouterLink
          class="text-white/80 no-underline hover:text-white"
          :to="{ name: dashboardRouteName(auth.state.user.role) }">
          {{ getRoleLabel(auth.state.user.role) }}
        </RouterLink>
        <button
          class="bg-primary text-attention hover:bg-secondary cursor-pointer rounded px-3 py-1 leading-tight"
          type="button"
          @click="handleLogout">
          Atsijungti
        </button>
      </template>
      <template v-else>
        <RouterLink
          class="text-white/80 no-underline hover:text-white"
          :to="{ name: ROUTE_NAMES.LOGIN }"
          >Prisijungti</RouterLink
        >
        <RouterLink
          class="bg-primary text-attention hover:bg-secondary rounded px-3 py-1 leading-tight no-underline"
          :to="{ name: ROUTE_NAMES.SIGNUP }"
          >Registruotis</RouterLink
        >
      </template>
    </template>
    <main
      class="bg-background mx-auto min-h-[calc(100vh-64px)] max-w-7xl px-4 py-6">
      <RouterView />
    </main>
  </StackedLayout>
</template>
