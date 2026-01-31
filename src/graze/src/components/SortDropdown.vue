<script setup>
import { ref, computed } from 'vue'
import { useConfigStore } from '../stores/config'

const configStore = useConfigStore()

const props = defineProps({
  modelValue: {
    type: String,
    default: 'protein_ratio_desc',
  },
  showDistance: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

// Get sort options from config store
const options = computed(() => {
  const hasLocation = props.showDistance
  return configStore.getSortOptions(hasLocation)
})

const selectedLabel = computed(() => {
  const option = options.value.find(o => o.value === props.modelValue)
  return option ? option.label : 'Sort'
})

function select(value) {
  emit('update:modelValue', value)
  isOpen.value = false
}

function handleClickOutside(event) {
  if (!event.target.closest('.sort-dropdown')) {
    isOpen.value = false
  }
}

// Close on click outside
if (typeof window !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}
</script>

<template>
  <div class="relative sort-dropdown">
    <button
      @click.stop="isOpen = !isOpen"
      class="sort-button"
    >
      <span>{{ selectedLabel }}</span>
      <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div
      v-if="isOpen"
      class="dropdown-menu"
    >
      <button
        v-for="option in options"
        :key="option.value"
        @click="select(option.value)"
        :class="[
          'dropdown-item',
          { 'active': option.value === modelValue }
        ]"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.sort-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 200ms ease;
}

.sort-button:hover {
  background-color: var(--color-surface);
  border-color: var(--color-primary);
}

.icon {
  width: 16px;
  height: 16px;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  margin-top: 4px;
  width: 200px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  z-index: 10;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 200ms ease;
}

.dropdown-item:hover {
  background-color: var(--color-surface);
}

.dropdown-item.active {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: white;
  font-weight: 600;
}
</style>
