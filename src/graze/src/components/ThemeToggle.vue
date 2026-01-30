<template>
  <button
    @click="toggleTheme"
    class="theme-toggle"
    :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <svg v-if="isDark" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
    <svg v-else class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  </button>
</template>

<script setup>
import { useTheme } from '../composables/useTheme'

const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  color: rgb(var(--color-text-secondary));
  cursor: pointer;
  transition: all 200ms ease;
}

.theme-toggle:hover {
  background-color: rgb(var(--color-surface-elevated));
  border-color: rgb(var(--color-border-hover));
  color: rgb(var(--color-text-primary));
  transform: scale(1.05);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.icon {
  width: 20px;
  height: 20px;
}
</style>
