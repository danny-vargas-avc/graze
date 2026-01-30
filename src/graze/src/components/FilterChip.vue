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
      'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
      active
        ? 'gradient-primary text-white shadow-custom'
        : 'bg-surface-elevated text-secondary hover:bg-surface hover:text-primary border border-border hover:border-primary'
    ]"
  >
    {{ label }}
  </button>
</template>
