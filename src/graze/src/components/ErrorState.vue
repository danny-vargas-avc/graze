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
  <div class="text-center py-12">
    <div class="text-4xl mb-4">😕</div>
    <h3 class="text-lg font-semibold text-gray-900 mb-2">Having trouble connecting</h3>
    <p class="text-gray-500 mb-4">{{ error.message }}</p>

    <button
      @click="emit('retry')"
      class="px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
    >
      Retry now
    </button>
  </div>
</template>
