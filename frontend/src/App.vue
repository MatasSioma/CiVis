<template>
  <nav class="bg-blue-600 text-white">
    <div class="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3">
      <router-link class="text-lg font-bold text-white no-underline" to="/"
        >CiVis</router-link
      >
      <div class="flex gap-4">
        <router-link class="text-white/80 no-underline hover:text-white" to="/"
          >Home</router-link
        >
        <router-link
          class="text-white/80 no-underline hover:text-white"
          to="/about"
          >About</router-link
        >
      </div>
    </div>
  </nav>
  <main class="mx-auto max-w-7xl px-4 py-6">
    <router-view />
  </main>
</template>
