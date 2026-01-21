<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click'])
</script>

<template>
  <button
    @click="emit('click')"
    :class="[
      'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
      active
        ? 'bg-green-600 text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    ]"
  >
    {{ label }}
  </button>
</template>
