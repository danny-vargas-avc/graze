<script setup>
import { ref } from 'vue'
import { useLocationsStore } from '../stores/locations'
import { storeToRefs } from 'pinia'

const locationsStore = useLocationsStore()
const { userLocation } = storeToRefs(locationsStore)

const requesting = ref(false)
const errorMessage = ref(null)
const showErrorTooltip = ref(false)

const handleRequestLocation = async () => {
  requesting.value = true
  errorMessage.value = null
  showErrorTooltip.value = false

  try {
    await locationsStore.requestUserLocation()
    // Success - location is now set in store
  } catch (error) {
    errorMessage.value = error.message
    showErrorTooltip.value = true
    // Auto-hide error tooltip after 5 seconds
    setTimeout(() => {
      showErrorTooltip.value = false
    }, 5000)
  } finally {
    requesting.value = false
  }
}

const clearLocation = () => {
  locationsStore.clearUserLocation()
  errorMessage.value = null
  showErrorTooltip.value = false
}

const closeError = () => {
  showErrorTooltip.value = false
}
</script>

<template>
  <div class="geolocation-button">
    <!-- Active state - location is set -->
    <button
      v-if="userLocation"
      class="location-button active"
      @click="clearLocation"
      aria-label="Location enabled. Click to disable location services"
    >
      <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </button>

    <!-- Inactive/requesting state -->
    <button
      v-else
      class="location-button"
      :class="{ requesting }"
      @click="handleRequestLocation"
      :disabled="requesting"
      :aria-label="requesting ? 'Requesting location...' : 'Enable location services'"
    >
      <svg v-if="!requesting" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <svg v-else class="icon spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </button>

    <!-- Error tooltip -->
    <Transition name="fade">
      <div
        v-if="showErrorTooltip && errorMessage"
        class="error-tooltip"
        role="alert"
        aria-live="polite"
      >
        <div class="error-content">
          <svg class="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="error-text">{{ errorMessage }}</p>
          <button class="close-button" @click="closeError" aria-label="Close error message">
            <svg class="close-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.geolocation-button {
  position: relative;
}

.location-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 200ms ease;
}

.location-button:hover {
  background-color: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.location-button.active {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border-color: transparent;
  color: white;
}

.location-button.requesting {
  cursor: wait;
  opacity: 0.7;
}

.location-button:disabled {
  cursor: not-allowed;
}

.icon {
  width: 20px;
  height: 20px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-tooltip {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 250px;
  max-width: 300px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  padding: 12px;
  z-index: 100;
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.error-icon {
  width: 20px;
  height: 20px;
  color: var(--color-error);
  flex-shrink: 0;
  margin-top: 1px;
}

.error-text {
  flex: 1;
  margin: 0;
  font-size: 13px;
  color: var(--color-text-primary);
  line-height: 1.5;
}

.close-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  flex-shrink: 0;
  transition: color 200ms ease;
}

.close-button:hover {
  color: var(--color-text-primary);
}

.close-icon {
  width: 16px;
  height: 16px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
