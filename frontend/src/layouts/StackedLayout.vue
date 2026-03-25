<script lang="ts" setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { ROUTE_NAMES, type RouteNamesValues } from '@/router/enums/routeNames';

const { links } = defineProps<{
  links: {
    label: string;
    name: RouteNamesValues;
  }[];
}>();

const route = useRoute();

const navigation = computed(() =>
  links.map((item) => ({
    ...item,
    isActive: route.name === item.name,
  })),
);
</script>

<template>
  <nav class="bg-blue-600 text-white">
    <div class="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3">
      <RouterLink
        class="text-lg font-bold text-white no-underline"
        :to="{ name: ROUTE_NAMES.HOME }"
        >CiVis</RouterLink
      >
      <div class="flex gap-4">
        <RouterLink
          v-for="link in navigation"
          :key="link.name"
          class="no-underline"
          :class="
            link.isActive
              ? 'font-semibold text-white'
              : 'text-white/80 hover:text-white'
          "
          :to="{ name: link.name }"
          >{{ link.label }}</RouterLink
        >
      </div>

      <div class="ml-auto flex items-center gap-4">
        <slot name="menu" />
      </div>
    </div>
  </nav>

  <slot />
</template>
