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
    <div v-else class="app-wrapper">
      <a href="#main-content" class="skip-link">Skip to main content</a>
      <AppHeader />
      <main id="main-content" class="app-main" tabindex="-1">
        <router-view />
      </main>
      <!-- <AppFooter /> -->
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

.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  z-index: 1000;
  padding: 12px 16px;
  background: var(--color-primary);
  color: white;
  text-decoration: none;
  font-weight: 600;
  border-radius: 0 0 4px 0;
  transition: top 200ms ease;
}

.skip-link:focus {
  top: 0;
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--color-surface);
  position: relative;
}

.app-main {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.app-main:focus {
  outline: none;
}
</style>
