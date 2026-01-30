<script setup>
defineProps({
  error: {
    type: Object,
    default: () => ({ message: 'Something went wrong' }),
  },
})

const emit = defineEmits(['retry'])
</script>

<template>
  <div class="error-state">
    <div class="icon-container">
      <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    </div>
    <h3 class="title">Connection Issue</h3>
    <p class="message">{{ error.message }}</p>

    <button
      @click="emit('retry')"
      class="retry-button"
    >
      <svg class="button-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      Retry
    </button>
  </div>
</template>

<style scoped>
.error-state {
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
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 16px;
  margin-bottom: 16px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.icon {
  width: 32px;
  height: 32px;
  color: var(--color-error);
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

.retry-button {
  display: flex;
  align-items: center;
  gap: 8px;
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

.retry-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.retry-button:active {
  transform: translateY(0);
}

.button-icon {
  width: 18px;
  height: 18px;
}
</style>
