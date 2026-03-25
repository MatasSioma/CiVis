<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand" to="/">CiVis</router-link>
      <div class="navbar-nav">
        <router-link class="nav-link" to="/">Home</router-link>
        <router-link class="nav-link" to="/about">About</router-link>
      </div>
    </div>
  </nav>
  <main class="container py-4">
    <router-view />
  </main>
</template>
