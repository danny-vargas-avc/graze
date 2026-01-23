<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'

const route = useRoute()
const isLanding = computed(() => route.name === 'landing')
</script>

<template>
  <!-- Landing page renders standalone -->
  <router-view v-if="isLanding" />

  <!-- Other pages get header/footer wrapper -->
  <div v-else class="min-h-screen flex flex-col bg-gray-50">
    <!-- <AppHeader /> -->
    <main class="flex-1">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>
