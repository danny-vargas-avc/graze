<template>
  <div class="view-toggle" :class="{ 'mobile': isMobile }">
        <button
      class="toggle-button"
      :class="{ 'active': modelValue === 'list' }"
      @click="selectView('list')"
    >
      <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
      <span class="label">List</span>
    </button>
    <button
      class="toggle-button"
      :class="{ 'active': modelValue === 'map' }"
      @click="selectView('map')"
    >
      <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
      <span class="label">Map</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'map',
    validator: (value) => ['map', 'list'].includes(value)
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectView = (view) => {
  if (view !== props.modelValue) {
    emit('update:modelValue', view)
    emit('change', view)
  }
}
</script>

<style scoped>
.view-toggle {
  display: flex;
  gap: 4px;
  background-color: rgb(var(--color-surface));
  border-radius: 8px;
  padding: 4px;
}

.view-toggle.mobile {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgb(var(--color-surface-elevated));
  border-radius: 0;
  border-top: 1px solid rgb(var(--color-border));
  padding: 8px 8px calc(12px + env(safe-area-inset-bottom)) 8px;
  gap: 8px;
  z-index: 100;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
}

.toggle-button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
  color: rgb(var(--color-text-secondary));
  position: relative;
}

.toggle-button:hover {
  background-color: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
}

.toggle-button.active {
  background-color: rgb(var(--color-surface));
  color: rgb(var(--color-primary));
  /* box-shadow: var(--shadow); */
}

/* Desktop active state */
.view-toggle:not(.mobile) .toggle-button {
  flex-direction: row;
  gap: 8px;
}

.view-toggle:not(.mobile) .toggle-button.active {
  background: white;
  color: rgb(var(--color-primary));
}

/* Mobile active state - more prominent */
.mobile .toggle-button {
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  gap: 4px;
}

.mobile .toggle-button.active {
  color: rgb(var(--color-primary));
  background: transparent;
}

.mobile .toggle-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 3px;
  background: linear-gradient(135deg, rgb(var(--color-primary)) 0%, rgb(var(--color-accent)) 100%);
  border-radius: 3px 3px 0 0;
}

.icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.mobile .icon {
  width: 24px;
  height: 24px;
}

.label {
  line-height: 1;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .view-toggle:not(.mobile) {
    display: none;
  }
}
</style>
