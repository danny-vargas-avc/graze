<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const localValue = ref(props.modelValue)
let debounceTimer = null

watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

function onInput(event) {
  localValue.value = event.target.value

  // Debounce the emit
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('update:modelValue', localValue.value)
  }, 300)
}

function clear() {
  localValue.value = ''
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="search-bar">
    <label for="search-input" class="sr-only">Search dishes or restaurants</label>
    <div class="search-icon" aria-hidden="true">
      <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
    <input
      id="search-input"
      type="search"
      :value="localValue"
      @input="onInput"
      placeholder="Search dishes or restaurants..."
      class="search-input"
      aria-label="Search dishes or restaurants"
    />
    <button
      v-if="localValue"
      @click="clear"
      class="clear-button"
      aria-label="Clear search"
    >
      <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.search-bar {
  position: relative;
  width: 100%;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.search-icon {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 12px;
  display: flex;
  align-items: center;
  pointer-events: none;
}

.search-icon .icon {
  width: 20px;
  height: 20px;
  color: var(--color-text-tertiary);
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 44px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-surface-elevated);
  color: var(--color-text-primary);
  font-size: 14px;
  transition: all 200ms ease;
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background-color: var(--color-background);
  box-shadow: 0 0 0 3px rgba(var(--color-primary), 0.1);
}

.clear-button {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 8px;
  display: flex;
  align-items: center;
  padding: 8px;
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: color 200ms ease;
}

.clear-button:hover {
  color: var(--color-text-primary);
}

.clear-button .icon {
  width: 20px;
  height: 20px;
}
</style>
