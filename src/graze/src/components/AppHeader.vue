<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="bg-white text-white border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
      <RouterLink to="/search" class="flex items-center gap-2 text-xl font-bold text-gray-900">
        <span>Graze</span>
      </RouterLink>
    </div>
  </header>
</template>
