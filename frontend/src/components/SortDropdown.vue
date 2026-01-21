<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'protein_ratio_desc',
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

const options = [
  { value: 'protein_ratio_desc', label: 'Best Protein/Cal' },
  { value: 'protein_desc', label: 'Highest Protein' },
  { value: 'protein_asc', label: 'Lowest Protein' },
  { value: 'calories_asc', label: 'Lowest Calories' },
  { value: 'calories_desc', label: 'Highest Calories' },
  { value: 'carbs_asc', label: 'Lowest Carbs' },
  { value: 'fat_desc', label: 'Highest Fat' },
  { value: 'fat_asc', label: 'Lowest Fat' },
  { value: 'alpha_asc', label: 'A-Z' },
]

const selectedLabel = computed(() => {
  const option = options.find(o => o.value === props.modelValue)
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
      class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
    >
      <span>{{ selectedLabel }}</span>
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div
      v-if="isOpen"
      class="absolute right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
    >
      <button
        v-for="option in options"
        :key="option.value"
        @click="select(option.value)"
        :class="[
          'block w-full text-left px-4 py-2 text-sm hover:bg-gray-50',
          option.value === modelValue ? 'text-green-600 font-medium' : 'text-gray-700'
        ]"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>
