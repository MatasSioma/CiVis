<script setup lang="ts">
import { computed, ref, watch } from 'vue';

interface ComboboxItem {
  id?: string;
  name: string;
}

const props = defineProps<{
  modelValue: ComboboxItem | null;
  items: ComboboxItem[];
  placeholder?: string;
  onCreate?: (name: string) => Promise<ComboboxItem>;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: ComboboxItem | null): void;
}>();

const query = ref(props.modelValue?.name ?? '');
const isOpen = ref(false);
const isCreating = ref(false);
const highlightedIndex = ref(0);

watch(
  () => props.modelValue,
  (next) => {
    if (next?.name !== query.value) {
      query.value = next?.name ?? '';
    }
  },
);

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();

  if (!q) {
    return props.items.slice(0, 50);
  }

  return props.items
    .filter((item) => item.name.toLowerCase().includes(q))
    .slice(0, 50);
});

const hasExactMatch = computed(() => {
  const q = query.value.trim().toLowerCase();
  return props.items.some((item) => item.name.toLowerCase() === q);
});

const showCreate = computed(() => {
  return Boolean(query.value.trim()) && !hasExactMatch.value;
});

const options = computed<Array<ComboboxItem | { __create: true; name: string }>>(() => {
  if (showCreate.value) {
    return [...filtered.value, { __create: true as const, name: query.value.trim() }];
  }

  return filtered.value;
});

function openList() {
  isOpen.value = true;
  highlightedIndex.value = 0;
}

function closeList() {
  setTimeout(() => {
    isOpen.value = false;
  }, 120);
}

function selectItem(item: ComboboxItem) {
  query.value = item.name;
  emit('update:modelValue', item);
  isOpen.value = false;
}

async function selectCreate(name: string) {
  if (!props.onCreate) {
    selectItem({ name });
    return;
  }

  isCreating.value = true;

  try {
    const created = await props.onCreate(name);
    selectItem(created);
  } finally {
    isCreating.value = false;
  }
}

function onInput(event: Event) {
  const value = (event.target as HTMLInputElement).value;
  query.value = value;
  isOpen.value = true;
  highlightedIndex.value = 0;

  if (props.modelValue && props.modelValue.name !== value) {
    emit('update:modelValue', value.trim() ? { name: value.trim() } : null);
  } else if (!value.trim()) {
    emit('update:modelValue', null);
  }
}

function moveHighlight(direction: 1 | -1) {
  const total = options.value.length;

  if (total === 0) {
    return;
  }

  highlightedIndex.value = (highlightedIndex.value + direction + total) % total;
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowDown') {
    event.preventDefault();
    isOpen.value = true;
    moveHighlight(1);
  } else if (event.key === 'ArrowUp') {
    event.preventDefault();
    moveHighlight(-1);
  } else if (event.key === 'Enter') {
    if (!isOpen.value) {
      return;
    }

    event.preventDefault();
    const opt = options.value[highlightedIndex.value];

    if (!opt) {
      return;
    }

    if ('__create' in opt) {
      void selectCreate(opt.name);
    } else {
      selectItem(opt);
    }
  } else if (event.key === 'Escape') {
    isOpen.value = false;
  }
}
</script>

<template>
  <div class="relative">
    <input
      :value="query"
      class="h-11 w-full rounded-md border border-gray-300 bg-white px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
      :placeholder="placeholder"
      type="text"
      @input="onInput"
      @focus="openList"
      @blur="closeList"
      @keydown="onKeydown" />

    <ul
      v-if="isOpen && options.length > 0"
      class="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border border-gray-200 bg-white py-1 shadow-lg">
      <li
        v-for="(opt, idx) in options"
        :key="('__create' in opt) ? `__create_${opt.name}` : (opt.id ?? opt.name)"
        :class="[
          'cursor-pointer px-3 py-2 text-sm',
          idx === highlightedIndex ? 'bg-primary text-attention' : 'text-gray-800 hover:bg-gray-100',
        ]"
        @mousedown.prevent="('__create' in opt) ? selectCreate(opt.name) : selectItem(opt)"
        @mouseenter="highlightedIndex = idx">
        <template v-if="'__create' in opt">
          <span class="font-semibold">Sukurti</span> „{{ opt.name }}“
          <span v-if="isCreating" class="ml-1 text-xs text-gray-500">(kuriama...)</span>
        </template>
        <template v-else>
          {{ opt.name }}
        </template>
      </li>
    </ul>
  </div>
</template>
