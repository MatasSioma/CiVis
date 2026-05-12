<script setup lang="ts">
interface TeamMember {
  name: string;
  email: string;
}

const team: TeamMember[] = [
  { name: 'Tomas Petronis', email: 'tomas.petronis@mif.stud.vu.lt' },
  { name: 'Matas Semėnas', email: 'matas.semenas@mif.stud.vu.lt' },
  { name: 'Gytis Malinauskas', email: 'gytis.malinauskas@mif.stud.vu.lt' },
  { name: 'Kasparas Šumskis', email: 'kasparas.sumskis@mif.stud.vu.lt' },
];

const lecturer = {
  name: 'Asta Slotkienė',
  title: 'Doc., Dr.',
  email: 'asta.slotkiene@mif.vu.lt',
};
</script>

<template>
  <section class="max-w-3xl rounded-lg bg-white p-6 shadow-sm">
    <h1 class="text-2xl font-bold text-gray-950">Apie</h1>
    <p class="mt-3 leading-7 text-gray-700">
      CiVis yra darbo paieškos ir kandidatų atrankos sistema, skirta darbo
      ieškantiems asmenims ir darbdaviams.
    </p>

    <h2 class="mt-8 text-xl font-bold text-gray-950">Komanda</h2>
    <ul class="mt-3 grid gap-2 sm:grid-cols-2">
      <li
        v-for="member in team"
        :key="member.email"
        class="rounded-md border border-gray-200 bg-background/40 p-3">
        <p class="font-semibold text-gray-950">{{ member.name }}</p>
        <a
          class="mt-1 block break-all text-sm text-attention hover:underline"
          :href="`mailto:${member.email}`">
          {{ member.email }}
        </a>
      </li>
    </ul>

    <h2 class="mt-8 text-xl font-bold text-gray-950">Dėstytoja</h2>
    <ul class="mt-3 grid gap-2 sm:grid-cols-2">
      <li class="rounded-md border border-gray-200 bg-background/40 p-3">
        <p class="font-semibold text-gray-950">{{ lecturer.name }}</p>
        <p class="text-sm text-gray-600">{{ lecturer.title }}</p>
        <a
          class="mt-1 block break-all text-sm text-attention hover:underline"
          :href="`mailto:${lecturer.email}`">
          {{ lecturer.email }}
        </a>
      </li>
    </ul>
  </section>
</template>
