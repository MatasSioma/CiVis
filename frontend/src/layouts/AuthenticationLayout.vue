<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue';

if (import.meta.env.DEV) {
  console.debug('[layout] AuthenticationLayout setup');
}

onMounted(() => {
  if (import.meta.env.DEV) {
    console.debug('[layout] AuthenticationLayout mounted');
  }
});

onBeforeUnmount(() => {
  if (import.meta.env.DEV) {
    console.debug('[layout] AuthenticationLayout beforeUnmount');
  }
});
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-background px-4">
    <RouterView />
  </main>
</template>
