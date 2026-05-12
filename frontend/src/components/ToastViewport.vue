<script setup lang="ts">
import { useToasts, type ToastType } from '@/stores/toasts';

const { removeToast, toasts } = useToasts();

const toastClasses: Record<ToastType, string> = {
  success: 'border-secondary bg-white text-gray-950',
  error: 'border-red-300 bg-white text-gray-950',
  info: 'border-gray-300 bg-white text-gray-950',
};

const markerClasses: Record<ToastType, string> = {
  success: 'bg-secondary',
  error: 'bg-red-400',
  info: 'bg-primary',
};
</script>

<template>
  <div
    aria-live="polite"
    class="fixed right-4 bottom-4 z-50 flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-3">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="flex items-start gap-3 rounded-lg border p-4 shadow-lg"
      :class="toastClasses[toast.type]">
      <span
        class="mt-1 h-2.5 w-2.5 shrink-0 rounded-full"
        :class="markerClasses[toast.type]" />
      <p class="min-w-0 flex-1 text-sm leading-5 font-medium">
        {{ toast.message }}
      </p>
      <button
        aria-label="Uždaryti pranešimą"
        class="hover:bg-background cursor-pointer rounded px-1 text-gray-500 hover:text-gray-950"
        type="button"
        @click="removeToast(toast.id)">
        ×
      </button>
    </div>
  </div>
</template>
