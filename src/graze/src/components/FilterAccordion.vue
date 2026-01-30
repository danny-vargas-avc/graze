<template>
  <details class="filter-accordion" :open="defaultOpen">
    <summary class="accordion-header">
      <span class="accordion-title">{{ title }}</span>
      <svg class="accordion-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </summary>
    <div class="accordion-content">
      <slot></slot>
    </div>
  </details>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  defaultOpen: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.filter-accordion {
  border-bottom: 1px solid rgb(var(--color-border));
}

.accordion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  cursor: pointer;
  user-select: none;
  list-style: none;
  transition: all 200ms ease;
}

.accordion-header::-webkit-details-marker {
  display: none;
}

.accordion-header:hover {
  color: rgb(var(--color-primary));
}

.accordion-title {
  font-size: 15px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
}

.accordion-icon {
  width: 20px;
  height: 20px;
  color: rgb(var(--color-text-tertiary));
  transition: transform 200ms ease;
  flex-shrink: 0;
}

.filter-accordion[open] .accordion-icon {
  transform: rotate(180deg);
}

.accordion-content {
  padding-bottom: 20px;
  animation: slideDown 200ms ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
