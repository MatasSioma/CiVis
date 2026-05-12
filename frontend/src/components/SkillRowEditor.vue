<script setup lang="ts">
const skill = defineModel<{
  name: string;
  type: 'hard' | 'soft' | 'experience';
  years_of_experience: number;
}>({ required: true });

withDefaults(
  defineProps<{
    hideType?: boolean;
    namePlaceholder?: string;
  }>(),
  {
    hideType: false,
    namePlaceholder: 'pvz. python',
  },
);

defineEmits<{
  remove: [];
}>();
</script>

<template>
  <div
    class="flex items-end gap-3 rounded-md border border-gray-200 bg-gray-50 p-3">
    <label class="block flex-1">
      <span class="text-sm font-medium text-gray-700">Pavadinimas</span>
      <input
        v-model="skill.name"
        class="focus:border-secondary focus:ring-secondary/40 mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 transition outline-none placeholder:text-gray-400 focus:ring-2"
        :placeholder="namePlaceholder"
        required
        type="text" />
    </label>

    <label v-if="!hideType" class="block w-40">
      <span class="text-sm font-medium text-gray-700">Tipas</span>
      <select
        v-model="skill.type"
        class="focus:border-secondary focus:ring-secondary/40 mt-1 h-11 w-full cursor-pointer rounded-md border border-gray-300 bg-white px-3 text-gray-950 transition outline-none focus:ring-2">
        <option value="hard">Techniniai</option>
        <option value="soft">Socialiniai</option>
        <option value="experience">Patirtis</option>
      </select>
    </label>

    <label class="block w-28">
      <span class="text-sm font-medium text-gray-700">Metai</span>
      <input
        v-model.number="skill.years_of_experience"
        class="focus:border-secondary focus:ring-secondary/40 mt-1 h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 transition outline-none placeholder:text-gray-400 focus:ring-2"
        min="0"
        placeholder="0"
        required
        step="1"
        type="number" />
    </label>

    <button
      class="mb-0.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-md border border-red-200 text-red-500 transition hover:bg-red-50 hover:text-red-700"
      type="button"
      @click="$emit('remove')">
      <svg
        class="h-5 w-5"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24">
        <path
          d="M6 18L18 6M6 6l12 12"
          stroke-linecap="round"
          stroke-linejoin="round" />
      </svg>
    </button>
  </div>
</template>
