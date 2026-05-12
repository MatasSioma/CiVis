<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>

<template>
  <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
    <h2 class="text-lg font-semibold text-gray-950">{{ title }}</h2>
    <p v-if="description" class="mt-2 text-sm text-gray-600">
      {{ description }}
    </p>
    <slot />
  </article>
</template>
