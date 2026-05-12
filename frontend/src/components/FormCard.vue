<script setup lang="ts">
defineProps<{
  maxWidth?: string;
}>();
</script>

<template>
  <div
    class="w-full rounded-lg border border-white/70 bg-white p-5 shadow-lg sm:p-6"
    :class="maxWidth ?? 'max-w-lg'">
    <slot />
  </div>
</template>
