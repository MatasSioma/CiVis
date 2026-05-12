<script setup lang="ts">
import { computed } from 'vue';
import { getRoleLabel, useAuth } from '@/stores/auth';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import DashboardCard from '@/components/DashboardCard.vue';

const { state } = useAuth();
const user = computed(() => state.user);
</script>

<template>
  <section v-if="user" class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Darbo ieškančio asmens paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ user.first_name || user.email }}
      </h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <DashboardCard title="CV" description="Profilis ir CV duomenys susieti su šia sesija.">
        <div class="mt-3 flex justify-between">
          <RouterLink
            class="text-secondary hover:text-secondary/80 text-sm font-medium"
            :to="{ name: ROUTE_NAMES.MY_CV }">
            Peržiūrėti CV →
          </RouterLink>
          <RouterLink
            class="text-secondary hover:text-secondary/80 text-sm font-medium"
            :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
            Įkelti CV →
          </RouterLink>
        </div>
      </DashboardCard>
      <DashboardCard
        title="Paraiškos"
        description="Matysite tik savo darbo paraiškas." />
      <DashboardCard title="Rolė" :description="getRoleLabel(user.role)" />
    </div>
  </section>
  <section v-else class="rounded-lg bg-white p-6 text-gray-700 shadow-sm">
    Paskyros būsena atnaujinama.
  </section>
</template>
