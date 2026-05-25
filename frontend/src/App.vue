<script setup lang="ts">
import { onBeforeUnmount, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import ToastViewport from '@/components/ToastViewport.vue';

const route = useRoute();

if (import.meta.env.DEV) {
  console.debug('[app] setup');
}

watch(
  () => route.fullPath,
  (fullPath, previousPath) => {
    if (import.meta.env.DEV) {
      console.debug('[app] route changed', {
        from: previousPath,
        to: fullPath,
        name: route.name,
        matched: route.matched.map((record) => record.path),
      });
    }
  },
);

onMounted(() => {
  if (import.meta.env.DEV) {
    console.debug('[app] mounted');
  }
});

onBeforeUnmount(() => {
  if (import.meta.env.DEV) {
    console.debug('[app] beforeUnmount');
  }
});
</script>

<template>
  <RouterView />
  <ToastViewport />
</template>
