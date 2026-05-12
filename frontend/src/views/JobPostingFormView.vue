<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import ComboboxCreate from '@/components/ComboboxCreate.vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ApiError } from '@/services/api';
import {
  industryApi,
  jobPostingApi,
  JOB_STATUS_LABELS,
  JOB_TYPE_LABELS,
  SKILL_TYPE_LABELS,
  WORKPLACE_TYPE_LABELS,
  type Industry,
  type JobPostingPayload,
  type JobPostingSkillInput,
  type JobStatus,
  type JobType,
  type SkillType,
  type WorkplaceType,
} from '@/services/employer';
import { useToasts } from '@/stores/toasts';

interface SkillRow extends JobPostingSkillInput {
  uid: number;
}

const route = useRoute();
const router = useRouter();
const { showToast } = useToasts();

const postingId = computed(() => {
  const id = route.params.id;
  return typeof id === 'string' ? id : null;
});
const isEditMode = computed(() => Boolean(postingId.value));

const industries = ref<Industry[]>([]);
const isLoading = ref(true);
const isSaving = ref(false);
const isDeleting = ref(false);
const notFound = ref(false);

const form = reactive({
  title: '',
  description: '',
  workplace_type: 'on_site' as WorkplaceType,
  location: '' as string,
  salary_min: '' as string,
  salary_max: '' as string,
  job_type: 'full_time' as JobType,
  status: 'draft' as JobStatus,
});

const selectedIndustry = ref<{ id?: string; name: string } | null>(null);
const skillRows = ref<SkillRow[]>([]);
let nextUid = 0;

const jobTypeOptions = Object.entries(JOB_TYPE_LABELS) as [JobType, string][];
const statusOptions = Object.entries(JOB_STATUS_LABELS) as [JobStatus, string][];
const skillTypeOptions = Object.entries(SKILL_TYPE_LABELS) as [SkillType, string][];
const workplaceTypeOptions = Object.entries(WORKPLACE_TYPE_LABELS) as [
  WorkplaceType,
  string,
][];

const errorMessage = ref('');

function makeRow(overrides: Partial<JobPostingSkillInput> = {}): SkillRow {
  nextUid += 1;
  return {
    uid: nextUid,
    name: '',
    type: 'hard',
    description: '',
    is_required: false,
    ...overrides,
  };
}

function addSkillRow() {
  if (skillRows.value.length >= 20) {
    return;
  }

  skillRows.value.push(makeRow());
}

function removeSkillRow(uid: number) {
  skillRows.value = skillRows.value.filter((row) => row.uid !== uid);
}

async function loadCommonData() {
  industries.value = await industryApi.list();
}

async function loadPosting(id: string) {
  try {
    const posting = await jobPostingApi.get(id);
    form.title = posting.title;
    form.description = posting.description;
    form.workplace_type = posting.workplace_type;
    form.location = posting.location ?? '';
    form.salary_min = posting.salary_min == null ? '' : String(posting.salary_min);
    form.salary_max = posting.salary_max == null ? '' : String(posting.salary_max);
    form.job_type = posting.job_type;
    form.status = posting.status;

    const matchedIndustry = industries.value.find((i) => i.id === posting.industry);
    selectedIndustry.value = matchedIndustry ?? null;

    skillRows.value = posting.skills_detail.map((s) =>
      makeRow({
        name: s.name,
        type: s.type,
        description: s.description,
        is_required: s.is_required,
      }),
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound.value = true;
      return;
    }

    showToast('Nepavyko įkelti skelbimo.', 'error');
  }
}

async function handleCreateIndustry(name: string) {
  const created = await industryApi.create(name);

  if (!industries.value.find((i) => i.id === created.id)) {
    industries.value = [...industries.value, created];
  }

  return created;
}

function validate(): string {
  if (!form.title.trim()) {
    return 'Įveskite pavadinimą.';
  }

  if (!selectedIndustry.value?.id) {
    return 'Pasirinkite veiklos sritį.';
  }

  if (!form.description.trim()) {
    return 'Įveskite aprašymą.';
  }

  const min = form.salary_min === '' ? null : Number(form.salary_min);
  const max = form.salary_max === '' ? null : Number(form.salary_max);

  if (min !== null && Number.isNaN(min)) {
    return 'Atlyginimas „nuo“ turi būti skaičius.';
  }

  if (max !== null && Number.isNaN(max)) {
    return 'Atlyginimas „iki“ turi būti skaičius.';
  }

  if (min !== null && max !== null && min > max) {
    return 'Minimalus atlyginimas negali būti didesnis už maksimalų.';
  }

  if (skillRows.value.length > 20) {
    return 'Galima nurodyti daugiausiai 20 įgūdžių.';
  }

  const namesLower: string[] = [];

  for (const row of skillRows.value) {
    const name = row.name.trim();

    if (!name) {
      return 'Visi įgūdžiai turi turėti pavadinimą.';
    }

    if (namesLower.includes(name.toLowerCase())) {
      return `Įgūdis „${name}“ nurodytas du kartus.`;
    }

    namesLower.push(name.toLowerCase());
  }

  return '';
}

function buildPayload(): JobPostingPayload | null {
  if (!selectedIndustry.value?.id) {
    return null;
  }

  return {
    industry: selectedIndustry.value.id,
    title: form.title.trim(),
    description: form.description.trim(),
    workplace_type: form.workplace_type,
    location:
      form.workplace_type === 'on_site' ? form.location.trim() || null : null,
    salary_min: form.salary_min === '' ? null : Number(form.salary_min),
    salary_max: form.salary_max === '' ? null : Number(form.salary_max),
    job_type: form.job_type,
    status: form.status,
    skills: skillRows.value.map((row) => ({
      name: row.name.trim(),
      type: row.type,
      description: row.description,
      is_required: row.is_required,
    })),
  };
}

function extractApiError(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return 'Nepavyko išsaugoti skelbimo.';
  }

  const details = error.details as Record<string, unknown> | null | undefined;

  if (details && typeof details === 'object') {
    for (const value of Object.values(details)) {
      if (typeof value === 'string') {
        return value;
      }

      if (Array.isArray(value) && value.length > 0) {
        const first = value[0];

        if (typeof first === 'string') {
          return first;
        }

        if (first && typeof first === 'object') {
          for (const nested of Object.values(first)) {
            if (typeof nested === 'string') {
              return nested;
            }

            if (Array.isArray(nested) && typeof nested[0] === 'string') {
              return nested[0];
            }
          }
        }
      }
    }
  }

  return 'Nepavyko išsaugoti skelbimo.';
}

async function onSubmit() {
  errorMessage.value = '';
  const validationError = validate();

  if (validationError) {
    errorMessage.value = validationError;
    showToast(validationError, 'error');
    return;
  }

  const payload = buildPayload();

  if (!payload) {
    return;
  }

  isSaving.value = true;

  try {
    if (isEditMode.value && postingId.value) {
      await jobPostingApi.update(postingId.value, payload);
      showToast('Skelbimas atnaujintas.', 'success');
    } else {
      await jobPostingApi.create(payload);
      showToast('Skelbimas sukurtas.', 'success');
    }

    await router.push({ name: ROUTE_NAMES.EMPLOYER_DASHBOARD });
  } catch (error) {
    const message = extractApiError(error);
    errorMessage.value = message;
    showToast(message, 'error');
  } finally {
    isSaving.value = false;
  }
}

async function onDelete() {
  if (!postingId.value) {
    return;
  }

  if (!window.confirm('Ar tikrai norite ištrinti šį skelbimą?')) {
    return;
  }

  isDeleting.value = true;

  try {
    await jobPostingApi.delete(postingId.value);
    showToast('Skelbimas ištrintas.', 'success');
    await router.push({ name: ROUTE_NAMES.EMPLOYER_DASHBOARD });
  } catch {
    showToast('Nepavyko ištrinti skelbimo.', 'error');
  } finally {
    isDeleting.value = false;
  }
}

function onCancel() {
  router.push({ name: ROUTE_NAMES.EMPLOYER_DASHBOARD });
}

onMounted(async () => {
  isLoading.value = true;

  try {
    await loadCommonData();

    if (isEditMode.value && postingId.value) {
      await loadPosting(postingId.value);
    } else {
      skillRows.value = [makeRow()];
    }
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <section v-if="notFound" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
    <h1 class="text-xl font-semibold text-gray-950">Skelbimas nerastas</h1>
    <p class="mt-2 text-sm text-gray-600">
      Skelbimas neegzistuoja arba neturite teisės jo matyti.
    </p>
    <button
      class="mt-4 rounded-md bg-primary px-3 py-2 text-sm font-semibold text-attention transition hover:bg-secondary"
      type="button"
      @click="onCancel">
      Grįžti į suvestinę
    </button>
  </section>

  <section v-else class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        {{ isEditMode ? 'Skelbimo redagavimas' : 'Naujas skelbimas' }}
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        {{ isEditMode ? form.title || 'Skelbimas' : 'Sukurti darbo skelbimą' }}
      </h1>
    </div>

    <p v-if="isLoading" class="rounded-md bg-white p-4 text-sm text-gray-600 shadow-sm">
      Kraunama...
    </p>

    <form
      v-else
      class="space-y-6 rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
      @submit.prevent="onSubmit">
      <section class="grid gap-4 md:grid-cols-2">
        <label class="block md:col-span-2">
          <span class="text-sm font-medium text-gray-700">Pavadinimas</span>
          <input
            v-model="form.title"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Pvz. Programuotojas"
            required
            type="text" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Veiklos sritis</span>
          <ComboboxCreate
            v-model="selectedIndustry"
            class="mt-1 block"
            :items="industries"
            placeholder="Pasirinkite arba sukurkite"
            :on-create="handleCreateIndustry" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Darbo vieta</span>
          <select
            v-model="form.workplace_type"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40">
            <option
              v-for="[value, label] in workplaceTypeOptions"
              :key="value"
              :value="value">
              {{ label }}
            </option>
          </select>
        </label>

        <label v-if="form.workplace_type === 'on_site'" class="block md:col-span-2">
          <span class="text-sm font-medium text-gray-700">Adresas</span>
          <input
            v-model="form.location"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Pvz. Vilnius, Gedimino pr. 1"
            type="text" />
        </label>

        <label class="block md:col-span-2">
          <span class="text-sm font-medium text-gray-700">Aprašymas</span>
          <textarea
            v-model="form.description"
            class="mt-1 min-h-32 w-full resize-y rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Pareigybės aprašymas, atsakomybės, galimos naudos (privilegijos, papildomos atostogos, sveikatos draudimas ir pan.)"
            required></textarea>
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Atlyginimas nuo</span>
          <input
            v-model="form.salary_min"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            min="0"
            placeholder="€"
            type="number" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Atlyginimas iki</span>
          <input
            v-model="form.salary_max"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            min="0"
            placeholder="€"
            type="number" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Darbo tipas</span>
          <select
            v-model="form.job_type"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40">
            <option v-for="[value, label] in jobTypeOptions" :key="value" :value="value">
              {{ label }}
            </option>
          </select>
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">Darbo skelbimo būsena</span>
          <select
            v-model="form.status"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40">
            <option v-for="[value, label] in statusOptions" :key="value" :value="value">
              {{ label }}
            </option>
          </select>
        </label>
      </section>

      <section class="rounded-lg border border-primary bg-background/40 p-4">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
              Reikalavimai ir įgūdžiai
            </p>
          </div>
          <span class="text-xs font-semibold text-gray-600">
            {{ skillRows.length }} / 20
          </span>
        </div>

        <div class="mt-3 space-y-3">
          <div
            v-for="(row, index) in skillRows"
            :key="row.uid"
            class="rounded-md border border-gray-200 bg-white p-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center gap-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
                  #{{ index + 1 }}
                </p>
                <label class="flex items-center gap-2">
                  <input
                    v-model="row.is_required"
                    type="checkbox"
                    class="size-4 accent-secondary" />
                  <span class="text-sm text-gray-700">Privalomas</span>
                </label>
              </div>
              <button
                class="text-xs font-semibold text-red-600 hover:text-red-700"
                type="button"
                @click="removeSkillRow(row.uid)">
                Pašalinti
              </button>
            </div>
            <div class="mt-2 grid gap-3 md:grid-cols-2">
              <label class="block">
                <span class="text-sm font-medium text-gray-700">Įgūdis</span>
                <input
                  v-model="row.name"
                  class="mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
                  placeholder="Įgūdžio pavadinimas"
                  type="text" />
              </label>
              <label class="block">
                <span class="text-sm font-medium text-gray-700">Tipas</span>
                <select
                  v-model="row.type"
                  class="mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition focus:border-secondary focus:ring-2 focus:ring-secondary/40">
                  <option v-for="[value, label] in skillTypeOptions" :key="value" :value="value">
                    {{ label }}
                  </option>
                </select>
              </label>
              <label class="block md:col-span-2">
                <span class="text-sm font-medium text-gray-700">Aprašymas</span>
                <textarea
                  v-model="row.description"
                  class="mt-1 min-h-16 w-full resize-y rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
                  placeholder="Tikslesnis aprašymas lems tikslesnį kandidato atitikimo įvertinimą"></textarea>
              </label>
            </div>
          </div>
        </div>

        <button
          class="mt-3 rounded-md bg-primary px-3 py-2 text-sm font-semibold text-attention transition hover:bg-secondary disabled:opacity-50"
          :disabled="skillRows.length >= 20"
          type="button"
          @click="addSkillRow">
          + Pridėti įgūdį
        </button>
      </section>

      <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div class="flex flex-wrap gap-2">
        <button
          class="rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary disabled:opacity-60"
          :disabled="isSaving"
          type="submit">
          {{ isSaving ? 'Išsaugoma...' : 'Išsaugoti' }}
        </button>
        <button
          class="rounded-md bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-200"
          type="button"
          @click="onCancel">
          Atšaukti
        </button>
        <button
          v-if="isEditMode"
          class="ml-auto rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
          :disabled="isDeleting"
          type="button"
          @click="onDelete">
          {{ isDeleting ? 'Ištrinama...' : 'Ištrinti' }}
        </button>
      </div>
    </form>
  </section>
</template>
