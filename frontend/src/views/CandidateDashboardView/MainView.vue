<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useAuth } from '@/stores/auth';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { cvApi } from '@/services/cv';
import { ApiError } from '@/services/api';
import DashboardCard from '@/components/DashboardCard.vue';

const { state } = useAuth();
const user = computed(() => state.user);

type CVStatus = 'loading' | 'uploaded' | 'missing';
const cvStatus = ref<CVStatus>('loading');

function formatDate(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('lt-LT', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function vocative(name: string): string {
  if (name.endsWith('s')) return `${name.slice(0, -1)}i`;
  if (name.endsWith('ė')) return `${name.slice(0, -1)}e`;
  return name;
}

onMounted(async () => {
  try {
    await cvApi.getMyCV();
    cvStatus.value = 'uploaded';
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      cvStatus.value = 'missing';
    } else {
      cvStatus.value = 'missing';
    }
  }
});
</script>

<template>
  <section v-if="user" class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Darbo ieškančio asmens paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ user.first_name ? vocative(user.first_name) : user.email }}
      </h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <DashboardCard title="Profilis">
        <dl class="mt-3 space-y-2 text-sm">
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">
              Vardas, pavardė
            </dt>
            <dd class="text-gray-900">
              {{ user.first_name }} {{ user.last_name }}
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-500">El. paštas</dt>
            <dd class="text-gray-900">{{ user.email }}</dd>
          </div>
          <div v-if="user.date_of_birth">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Gimimo data</dt>
            <dd class="text-gray-900">{{ formatDate(user.date_of_birth) }}</dd>
          </div>
        </dl>
      </DashboardCard>

      <DashboardCard title="CV">
        <p v-if="cvStatus === 'loading'" class="mt-3 text-sm text-gray-500">
          Kraunama...
        </p>
        <template v-else-if="cvStatus === 'uploaded'">
          <p class="mt-3 text-sm text-gray-700">CV įkeltas.</p>
          <RouterLink
            class="bg-attention hover:bg-secondary mt-4 inline-block cursor-pointer rounded-md px-4 py-2 text-sm font-semibold text-white transition"
            :to="{ name: ROUTE_NAMES.MY_CV }">
            Peržiūrėti CV →
          </RouterLink>
        </template>
        <template v-else>
          <p class="mt-3 text-sm text-gray-700">CV dar neįkeltas.</p>
          <RouterLink
            class="bg-attention hover:bg-secondary mt-4 inline-block cursor-pointer rounded-md px-4 py-2 text-sm font-semibold text-white transition"
            :to="{ name: ROUTE_NAMES.UPLOAD_CV }">
            Įkelti CV →
          </RouterLink>
        </template>
      </DashboardCard>

      <DashboardCard title="Paraiškos">
        <p class="mt-3 text-sm text-gray-700">
          Dar nepateikėte paraiškų į jokius darbo skelbimus.
        </p>
      </DashboardCard>
    </div>
  </section>
  <section v-else class="rounded-lg bg-white p-6 text-gray-700 shadow-sm">
    Paskyros būsena atnaujinama.
  </section>
</template>
