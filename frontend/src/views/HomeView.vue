<template>
  <div>
    <h1>Documents</h1>
    <div v-if="loading" class="text-muted">Loading...</div>
    <div v-else-if="documents.length === 0" class="text-muted">
      No documents yet.
    </div>
    <div v-else class="list-group">
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="list-group-item"
      >
        <h5 class="mb-1">{{ doc.title }}</h5>
        <p class="mb-0 text-muted">{{ doc.content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const documents = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await fetch("/api/documents/");
    documents.value = await res.json();
  } catch {
    console.error("Failed to fetch documents");
  } finally {
    loading.value = false;
  }
});
</script>
