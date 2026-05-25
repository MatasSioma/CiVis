<script setup lang="ts">
import FormCard from '@/components/FormCard.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
</script>

<template>
  <div class="flex justify-center py-8">
    <FormCard max-width="max-w-2xl">
      <p class="text-secondary text-sm font-semibold tracking-wide uppercase">
        Page not found
      </p>
      <h1 class="mt-2 text-3xl leading-tight font-bold text-gray-950">
        Puslapis nerastas
      </h1>
      <p class="mt-3 leading-7 text-gray-700">
        Requested page does not exist. Please check the address or return to the
        home page.
      </p>
      <RouterLink
        class="bg-attention hover:bg-secondary mt-5 inline-block rounded-md px-4 py-2.5 font-semibold text-white transition"
        :to="{ name: ROUTE_NAMES.HOME }">
        Back to home
      </RouterLink>
    </FormCard>
  </div>
</template>
