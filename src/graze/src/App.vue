<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import { useTransitionStore } from './stores/transition'

const route = useRoute()
const transitionStore = useTransitionStore()
const isFullscreen = computed(() => route.name === 'landing' || route.name === 'loading')
</script>

<template>
  <div>
    <!-- Screenshot overlay for seamless landing → loading handoff -->
    <img
      v-if="transitionStore.screenshotDataUrl"
      :src="transitionStore.screenshotDataUrl"
      class="screenshot-overlay"
    />

    <!-- Fullscreen pages (landing, loading) render standalone -->
    <router-view v-if="isFullscreen" />

    <!-- Other pages get header/footer wrapper -->
    <div v-else class="min-h-screen flex flex-col bg-gray-50">
      <AppHeader />
      <main class="flex-1">
        <router-view />
      </main>
      <AppFooter />
    </div>
  </div>
</template>

<style>
.screenshot-overlay {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 9999;
  pointer-events: none;
}
</style>
