<script setup lang="ts">
import logoUrl from '@/assets/brand/civis-logo.svg';

withDefaults(
  defineProps<{
    compact?: boolean;
    large?: boolean;
  }>(),
  {
    compact: false,
    large: false,
  },
);
</script>

<template>
  <div class="flex items-center leading-none">
    <img
      alt="CiVis"
      class="block h-12 w-auto shrink-0 object-contain align-middle"
      :class="{ 'h-13': compact, 'h-16': large }"
      :src="logoUrl" />
  </div>
</template>
