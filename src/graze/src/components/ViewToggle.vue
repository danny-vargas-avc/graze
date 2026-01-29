<template>
  <div class="view-toggle" :class="{ 'mobile': isMobile }">
    <button
      class="toggle-button"
      :class="{ 'active': modelValue === 'map' }"
      @click="selectView('map')"
    >
      <span class="icon">🗺️</span>
      <span class="label">Map</span>
    </button>
    <button
      class="toggle-button"
      :class="{ 'active': modelValue === 'list' }"
      @click="selectView('list')"
    >
      <span class="icon">📋</span>
      <span class="label">List</span>
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
  background: #F1F5F9;
  border-radius: 8px;
  padding: 4px;
}

.view-toggle.mobile {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-radius: 0;
  border-top: 1px solid #E2E8F0;
  padding: 8px;
  gap: 8px;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.toggle-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
  color: #64748B;
}

.toggle-button:hover {
  background: #E2E8F0;
  color: #334155;
}

.toggle-button.active {
  background: white;
  color: #1E293B;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.mobile .toggle-button {
  padding: 12px 20px;
  font-size: 15px;
}

.mobile .toggle-button .icon {
  font-size: 20px;
}

.icon {
  font-size: 16px;
  line-height: 1;
}

.label {
  line-height: 1;
}

@media (max-width: 768px) {
  .view-toggle:not(.mobile) {
    display: none;
  }
}
</style>
