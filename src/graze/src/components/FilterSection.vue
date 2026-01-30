<script setup>
import { computed } from 'vue'
import FilterChip from './FilterChip.vue'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  options: {
    type: Array,
    required: true,
    // Each option: { label: string, min?: number, max?: number }
  },
  modelValue: {
    type: Object,
    default: () => ({ min: null, max: null }),
  },
})

const emit = defineEmits(['update:modelValue'])

function isActive(option) {
  return props.modelValue.min === option.min && props.modelValue.max === option.max
}

function select(option) {
  if (isActive(option)) {
    // Deselect
    emit('update:modelValue', { min: null, max: null })
  } else {
    emit('update:modelValue', { min: option.min, max: option.max })
  }
}
</script>

<template>
  <div>
    <label v-if="label" class="filter-label">{{ label }}</label>
    <div class="flex flex-wrap gap-2">
      <FilterChip
        v-for="option in options"
        :key="option.label"
        :label="option.label"
        :active="isActive(option)"
        @click="select(option)"
      />
    </div>
  </div>
</template>

<style scoped>
.filter-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgb(var(--color-text-secondary));
  margin-bottom: 8px;
}
</style>
