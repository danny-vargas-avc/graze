<script setup>
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
  <div class="text-center py-6">
    <button
      v-if="hasMore"
      @click="emit('click')"
      :disabled="loading"
      class="px-6 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      <span v-if="loading">Loading...</span>
      <span v-else>Load 20 more results</span>
    </button>

    <p v-else-if="total > 0" class="text-gray-500 text-sm">
      ✓ All {{ total }} results loaded
    </p>
  </div>
</template>
