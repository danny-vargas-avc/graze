<script setup>
import { RouterLink } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
</script>

<template>
  <header class="bg-surface border-b border-border sticky top-0 z-50 backdrop-blur-sm bg-opacity-90">
    <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
      <RouterLink to="/search" class="flex items-center gap-2 text-xl font-bold text-gradient-primary hover:opacity-80 transition-opacity">
        <span>Graze</span>
      </RouterLink>
      <div class="flex items-center gap-3">
        <ThemeToggle />
      </div>
    </div>
  </header>
</template>
