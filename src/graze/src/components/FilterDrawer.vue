<template>
  <!-- Backdrop -->
  <Transition name="fade">
    <div
      v-if="modelValue"
      class="filter-backdrop"
      @click="close"
      aria-hidden="true"
    ></div>
  </Transition>

  <!-- Drawer -->
  <Transition name="slide-up">
    <div
      v-if="modelValue"
      ref="drawerRef"
      class="filter-drawer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="drawer-title"
    >
      <!-- Header -->
      <div class="drawer-header">
        <h2 id="drawer-title" class="drawer-title">Filters</h2>
        <div class="drawer-actions">
          <button
            class="clear-button"
            @click="handleClearFilters"
            aria-label="Clear all filters"
          >
            Clear All
          </button>
          <button
            ref="closeButtonRef"
            class="close-button"
            @click="close"
            aria-label="Close filters"
          >
            <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="drawer-content">
        <slot></slot>
      </div>

      <!-- Footer with Apply button -->
      <div class="drawer-footer">
        <button class="apply-button" @click="close" aria-label="Apply filters and close">
          <span>Apply Filters</span>
          <span v-if="activeFilterCount > 0" class="filter-badge" aria-label="`${activeFilterCount} filters active`">{{ activeFilterCount }}</span>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { watch, onMounted, onUnmounted, ref, nextTick } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  activeFilterCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue', 'clear-filters'])

const drawerRef = ref(null)
const closeButtonRef = ref(null)

const close = () => {
  emit('update:modelValue', false)
}

const handleClearFilters = () => {
  emit('clear-filters')
}

// Handle ESC key
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.modelValue) {
    close()
  }
}

// Focus trapping
const handleFocusTrap = (e) => {
  if (!props.modelValue || !drawerRef.value) return

  const focusableElements = drawerRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  if (e.key === 'Tab') {
    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault()
        lastElement.focus()
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    }
  }
}

// Prevent body scroll and manage focus when drawer is open
watch(() => props.modelValue, async (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
    // Focus close button when drawer opens
    await nextTick()
    closeButtonRef.value?.focus()
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('keydown', handleFocusTrap)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('keydown', handleFocusTrap)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.filter-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 200;
}

.filter-drawer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  max-height: 85vh;
  background-color: var(--color-background);
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
  z-index: 201;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.drawer-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.drawer-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.clear-button {
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 200ms ease;
}

.clear-button:hover {
  color: var(--color-error);
}

.close-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: var(--color-surface);
  border: none;
  border-radius: 8px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 200ms ease;
}

.close-button:hover {
  background-color: var(--color-surface-elevated);
  color: var(--color-text-primary);
}

.close-button .icon {
  width: 20px;
  height: 20px;
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0;
}

/* Filter content styling */
.drawer-content :deep(.quick-filters) {
  margin-top: 16px;
  margin-bottom: 24px;
}

.drawer-content :deep(.main-filters) {
  margin-top: 8px;
}

/* Add top border to first accordion */
.drawer-content :deep(.filter-accordion:first-child) {
  border-top: 1px solid var(--color-border);
}

.drawer-footer {
  padding: 16px 20px 20px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.apply-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 200ms ease, box-shadow 200ms ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.apply-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.apply-button:active {
  transform: translateY(0);
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 250ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
</style>
