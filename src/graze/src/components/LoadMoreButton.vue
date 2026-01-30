<script setup>
import LoadingSpinner from './LoadingSpinner.vue'

defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  hasMore: {
    type: Boolean,
    default: false,
  },
  shown: {
    type: Number,
    default: 0,
  },
  total: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['click'])
</script>

<template>
  <div class="load-more-container">
    <button
      v-if="hasMore"
      @click="emit('click')"
      :disabled="loading"
      class="load-more-button"
    >
      <LoadingSpinner v-if="loading" size="sm" />
      <span v-else>Load 20 more</span>
    </button>

    <div v-else-if="total > 0" class="all-loaded">
      <svg class="check-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <span>All {{ total }} results loaded</span>
    </div>
  </div>
</template>

<style scoped>
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

.load-more-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 200ms ease, box-shadow 200ms ease, opacity 200ms ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 160px;
}

.load-more-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.load-more-button:active:not(:disabled) {
  transform: translateY(0);
}

.load-more-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.all-loaded {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.check-icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
}
</style>
