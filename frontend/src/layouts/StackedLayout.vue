<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import BrandLogo from '@/components/BrandLogo.vue';
import { ROUTE_NAMES, type RouteNamesValues } from '@/router/enums/routeNames';

const { links } = defineProps<{
  links: {
    label: string;
    name: RouteNamesValues;
  }[];
}>();

const route = useRoute();

if (import.meta.env.DEV) {
  console.debug('[layout] StackedLayout setup');
}

const navigation = computed(() =>
  links.map((item) => ({
    ...item,
    isActive: route.name === item.name,
  })),
);

onMounted(() => {
  if (import.meta.env.DEV) {
    console.debug('[layout] StackedLayout mounted');
  }
});

onBeforeUnmount(() => {
  if (import.meta.env.DEV) {
    console.debug('[layout] StackedLayout beforeUnmount');
  }
});
</script>

<template>
  <nav class="bg-attention text-white">
    <div class="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 py-0">
      <RouterLink
        class="flex shrink-0 items-center self-center no-underline leading-none"
        :to="{ name: ROUTE_NAMES.HOME }">
        <BrandLogo compact />
      </RouterLink>
      <div class="flex h-full items-center gap-4">
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

      <div class="ml-auto flex h-full items-center gap-3">
        <slot name="menu" />
      </div>
    </div>
  </nav>

  <slot />
</template>
