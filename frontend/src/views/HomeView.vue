<template>
  <div>
    <h1 class="mb-4 text-2xl font-bold">Documents</h1>
    <div v-if="loading" class="text-gray-500">Loading...</div>
    <div v-else-if="documents.length === 0" class="text-gray-500">
      No documents yet.
    </div>
    <div v-else class="flex flex-col gap-2">
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="rounded border border-gray-200 px-4 py-3">
        <h5 class="font-semibold">{{ doc.title }}</h5>
        <p class="text-gray-500">{{ doc.content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Document {
  id: number;
  title: string;
  content: string;
}

const documents = ref<Document[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await fetch('/api/documents/');
    documents.value = await res.json();
  } catch {
    console.error('Failed to fetch documents');
  } finally {
    loading.value = false;
  }
});
</script>
