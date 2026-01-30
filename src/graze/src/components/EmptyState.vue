<script setup>
defineProps({
  title: {
    type: String,
    default: 'No results found',
  },
  message: {
    type: String,
    default: '',
  },
  showClearFilters: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['clear'])
</script>

<template>
  <div class="empty-state">
    <div class="icon-container">
      <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
    <h3 class="title">{{ title }}</h3>
    <p v-if="message" class="message">{{ message }}</p>

    <button
      v-if="showClearFilters"
      @click="emit('clear')"
      class="clear-button"
    >
      Clear all filters
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.icon-container {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface-elevated);
  border-radius: 16px;
  margin-bottom: 16px;
  border: 1px solid var(--color-border);
}

.icon {
  width: 32px;
  height: 32px;
  color: var(--color-text-tertiary);
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.message {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 0 24px 0;
  max-width: 400px;
}

.clear-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 200ms ease, box-shadow 200ms ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.clear-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.clear-button:active {
  transform: translateY(0);
}
</style>
