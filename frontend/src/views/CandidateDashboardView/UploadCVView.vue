<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useToasts } from '@/stores/toasts';
import { cvApi, type ExtractedSkill } from '@/services/cv';
import { ApiError } from '@/services/api';
import FormCard from '@/components/FormCard.vue';
import SkillRowEditor from '@/components/SkillRowEditor.vue';

const { showToast } = useToasts();

type SkillType = 'hard' | 'soft' | 'experience';
type Step = 'upload' | SkillType;

const step = ref<Step>('upload');
const isUploading = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref('');
const fileKey = ref('');
const selectedFile = ref<File | null>(null);

interface SkillRow {
  name: string;
  type: SkillType;
  description: string;
}

const hardSkills = reactive<SkillRow[]>([]);
const softSkills = reactive<SkillRow[]>([]);
const experienceSkills = reactive<SkillRow[]>([]);

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const SKILL_STEPS = [
  {
    key: 'hard' as const,
    label: 'Techniniai įgūdžiai (Hard skills)',
    description:
      'Kalbos, įrankiai, technologijos ir kiti pamatuojami gebėjimai.',
  },
  {
    key: 'soft' as const,
    label: 'Socialiniai įgūdžiai (Soft skills)',
    description:
      'Komandinis darbas, komunikacija, lyderystė ir kiti socialiniai gebėjimai.',
  },
  {
    key: 'experience' as const,
    label: 'Patirtis',
    description:
      'Eitos pareigos, pramonės šakos ir kita patirtis.',
  },
];

const currentStepIndex = computed(() =>
  SKILL_STEPS.findIndex((s) => s.key === step.value),
);

const currentConfig = computed(() => {
  const idx = currentStepIndex.value;
  return idx >= 0 ? SKILL_STEPS[idx] : SKILL_STEPS[0];
});

const isLastSkillStep = computed(
  () => currentStepIndex.value === SKILL_STEPS.length - 1,
);

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  errorMessage.value = '';

  if (!file) {
    selectedFile.value = null;
    return;
  }

  if (file.type !== 'application/pdf') {
    errorMessage.value = 'Leidžiami tik PDF failai.';
    selectedFile.value = null;
    input.value = '';
    return;
  }

  if (file.size > MAX_FILE_SIZE) {
    errorMessage.value = 'Failo dydis negali viršyti 10 MB.';
    selectedFile.value = null;
    input.value = '';
    return;
  }

  selectedFile.value = file;
}

function distributeSkills(extracted: ExtractedSkill[]) {
  hardSkills.length = 0;
  softSkills.length = 0;
  experienceSkills.length = 0;

  for (const s of extracted) {
    const row: SkillRow = {
      name: s.name.charAt(0).toUpperCase() + s.name.slice(1),
      type: s.type,
      description: s.description ?? '',
    };
    if (s.type === 'hard') hardSkills.push(row);
    else if (s.type === 'soft') softSkills.push(row);
    else experienceSkills.push(row);
  }
}

async function handleUpload() {
  if (!selectedFile.value) {
    errorMessage.value = 'Pasirinkite PDF failą.';
    return;
  }

  errorMessage.value = '';
  isUploading.value = true;

  try {
    const data = await cvApi.upload(selectedFile.value);
    fileKey.value = data.file_key;
    distributeSkills(data.skills);
    step.value = 'hard';
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.details &&
      typeof error.details === 'object'
    ) {
      const firstMsg = Object.values(
        error.details as Record<string, string[]>,
      ).flat()[0];
      errorMessage.value =
        firstMsg ?? 'Įvyko klaida įkeliant failą. Bandykite dar kartą.';
    } else {
      errorMessage.value = 'Įvyko klaida įkeliant failą. Bandykite dar kartą.';
    }
    showToast(errorMessage.value, 'error');
  } finally {
    isUploading.value = false;
  }
}

function goToStep(key: SkillType) {
  errorMessage.value = '';
  step.value = key;
}

function goNext() {
  const idx = currentStepIndex.value;
  if (idx < SKILL_STEPS.length - 1) {
    goToStep(SKILL_STEPS[idx + 1].key);
  }
}

function goBack() {
  const idx = currentStepIndex.value;
  if (idx > 0) {
    goToStep(SKILL_STEPS[idx - 1].key);
  } else {
    errorMessage.value = '';
    step.value = 'upload';
  }
}

function addSkill(type: SkillType) {
  const arr =
    type === 'hard'
      ? hardSkills
      : type === 'soft'
        ? softSkills
        : experienceSkills;
  arr.push({ name: '', type, description: '' });
}

function removeSkill(type: SkillType, index: number) {
  const arr =
    type === 'hard'
      ? hardSkills
      : type === 'soft'
        ? softSkills
        : experienceSkills;
  arr.splice(index, 1);
}

function getAllSkills(): SkillRow[] {
  return [...hardSkills, ...softSkills, ...experienceSkills];
}

function validateSkills(): string {
  const all = getAllSkills();
  if (all.length === 0) return 'Pridėkite bent vieną įgūdį.';

  for (const skill of all) {
    if (!skill.name.trim()) return 'Visi įgūdžiai turi turėti pavadinimą.';
  }

  const names = all.map((s) => s.name.trim().toLowerCase());
  if (new Set(names).size !== names.length)
    return 'Įgūdžių pavadinimai negali kartotis.';

  return '';
}

async function handleSubmit() {
  errorMessage.value = '';

  const validationError = validateSkills();
  if (validationError) {
    errorMessage.value = validationError;
    showToast(validationError, 'error');
    return;
  }

  isSubmitting.value = true;

  try {
    const payload: ExtractedSkill[] = getAllSkills().map((s) => ({
      name: s.name.trim(),
      type: s.type,
      description: s.description.trim(),
    }));

    const { checkout_url } = await cvApi.checkout({
      file_key: fileKey.value,
      skills: payload,
    });
    window.location.href = checkout_url;
  } catch (error) {
    if (error instanceof ApiError) {
      const details = error.details as Record<string, string[]>;
      const firstMsg = Object.values(details).flat()[0];
      errorMessage.value = firstMsg ?? 'Įvyko klaida kuriant mokėjimą.';
    } else {
      errorMessage.value = 'Įvyko klaida kuriant mokėjimą.';
    }
    showToast(errorMessage.value, 'error');
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="flex justify-center py-8">
    <!-- Upload PDF -->
    <FormCard v-if="step === 'upload'">
      <form @submit.prevent="handleUpload">
        <h1 class="text-2xl leading-tight font-bold text-gray-950">
          Įkelti CV
        </h1>
        <p class="mt-1 text-sm text-gray-600">
          Pasirinkite PDF failą (maks. 10 MB). Sistema automatiškai išgaus
          įgūdžius.
        </p>

        <label class="mt-4 block">
          <span class="text-sm font-medium text-gray-700">PDF failas</span>
          <input
            accept=".pdf,application/pdf"
            class="focus:border-secondary focus:ring-secondary/40 mt-1 w-full cursor-pointer rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-950 transition outline-none file:mr-3 file:cursor-pointer file:rounded file:border-0 file:bg-gray-100 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-gray-700 hover:file:bg-gray-200 focus:ring-2"
            type="file"
            @change="onFileChange" />
        </label>

        <p v-if="errorMessage" class="mt-4 text-sm text-red-600">
          {{ errorMessage }}
        </p>

        <button
          class="bg-attention hover:bg-secondary mt-4 h-11 w-full cursor-pointer rounded-md px-4 font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isUploading || !selectedFile"
          type="submit">
          {{ isUploading ? 'Apdorojama...' : 'Įkelti ir analizuoti' }}
        </button>
      </form>
    </FormCard>

    <!-- Skill editors (3 steps) -->
    <FormCard v-else max-width="max-w-3xl">
      <!-- Step indicator -->
      <nav class="mb-6 flex items-center justify-center gap-2">
        <template v-for="(cfg, i) in SKILL_STEPS" :key="cfg.key">
          <button
            type="button"
            class="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-full text-sm font-semibold transition"
            :class="{
              'bg-secondary text-white': cfg.key === step,
              'bg-secondary/20 text-secondary': currentStepIndex > i,
              'bg-gray-200 text-gray-500': currentStepIndex < i,
            }"
            @click="goToStep(cfg.key)">
            {{ i + 1 }}
          </button>
          <div
            v-if="i < SKILL_STEPS.length - 1"
            class="h-0.5 w-12 transition-colors"
            :class="currentStepIndex > i ? 'bg-secondary' : 'bg-gray-200'" />
        </template>
      </nav>

      <form @submit.prevent="isLastSkillStep ? handleSubmit() : goNext()">
        <h1 class="text-2xl leading-tight font-bold text-gray-950">
          {{ currentConfig.label }}
        </h1>
        <p class="mt-1 text-sm text-gray-600">
          {{ currentConfig.description }}
        </p>

        <!-- Hard skills -->
        <div v-if="step === 'hard'" class="mt-4 space-y-3">
          <SkillRowEditor
            v-for="(_, index) in hardSkills"
            :key="index"
            v-model="hardSkills[index]"
            hide-type
            name-placeholder="pvz. Python, React, AWS"
            @remove="removeSkill('hard', index)" />
        </div>

        <!-- Soft skills -->
        <div v-else-if="step === 'soft'" class="mt-4 space-y-3">
          <SkillRowEditor
            v-for="(_, index) in softSkills"
            :key="index"
            v-model="softSkills[index]"
            hide-type
            name-placeholder="pvz. komandinis darbas, lyderystė"
            @remove="removeSkill('soft', index)" />
        </div>

        <!-- Experience -->
        <div v-else class="mt-4 space-y-3">
          <SkillRowEditor
            v-for="(_, index) in experienceSkills"
            :key="index"
            v-model="experienceSkills[index]"
            hide-type
            name-placeholder="pvz. projektų valdymas, DevOps"
            @remove="removeSkill('experience', index)" />
        </div>

        <button
          class="border-secondary text-secondary hover:bg-secondary/10 mt-3 flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-md border px-4 font-semibold transition"
          type="button"
          @click="addSkill(currentConfig.key)">
          <svg
            class="h-5 w-5"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24">
            <path
              d="M12 5v14m-7-7h14"
              stroke-linecap="round"
              stroke-linejoin="round" />
          </svg>
          Pridėti įgūdį
        </button>

        <p v-if="errorMessage" class="mt-4 text-sm text-red-600">
          {{ errorMessage }}
        </p>

        <div class="mt-4 flex gap-3">
          <button
            class="h-11 flex-1 cursor-pointer rounded-md border border-gray-300 px-4 font-semibold text-gray-700 transition hover:bg-gray-50"
            type="button"
            @click="goBack">
            Atgal
          </button>

          <button
            v-if="!isLastSkillStep"
            class="bg-attention hover:bg-secondary h-11 flex-1 cursor-pointer rounded-md px-4 font-semibold text-white transition"
            type="submit">
            Toliau
          </button>

          <button
            v-else
            class="bg-attention hover:bg-secondary h-11 flex-1 cursor-pointer rounded-md px-4 font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="isSubmitting"
            type="submit">
            {{ isSubmitting ? 'Saugoma...' : 'Išsaugoti CV' }}
          </button>
        </div>
      </form>
    </FormCard>
  </div>
</template>
