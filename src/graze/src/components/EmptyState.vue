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
  <div class="text-center py-12">
    <div class="text-4xl mb-4">🔍</div>
    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
    <p v-if="message" class="text-gray-500 mb-4">{{ message }}</p>

    <button
      v-if="showClearFilters"
      @click="emit('clear')"
      class="px-4 py-2 text-green-600 font-medium hover:bg-green-50 rounded-lg transition-colors"
    >
      Clear all filters
    </button>
  </div>
</template>
