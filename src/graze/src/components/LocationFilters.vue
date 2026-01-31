<template>
  <div class="location-filters">
    <div class="filter-section">
      <label class="filter-label">Search Radius</label>
      <div class="radius-options">
        <button
          v-for="option in radiusOptions"
          :key="option"
          class="radius-button"
          :class="{ 'active': modelRadius === option }"
          @click="selectRadius(option)"
        >
          {{ option }} mi
        </button>
      </div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Restaurants</label>
      <div class="restaurant-chips">
        <button
          v-for="restaurant in restaurants"
          :key="restaurant.slug"
          class="restaurant-chip"
          :class="{ 'active': isSelected(restaurant.slug) }"
          @click="toggleRestaurant(restaurant.slug)"
        >
          {{ restaurant.name }}
        </button>
      </div>
      <button
        v-if="selectedRestaurants.length > 0"
        class="clear-button"
        @click="clearRestaurants"
      >
        Clear All
      </button>
    </div>

    <div v-if="userLocation" class="filter-section">
      <label class="filter-label">User Location</label>
      <div class="location-info">
        <span class="location-text">
          📍 {{ userLocation.lat.toFixed(4) }}, {{ userLocation.lng.toFixed(4) }}
        </span>
        <button class="text-button" @click="clearLocation">
          Clear
        </button>
      </div>
    </div>

    <div v-else class="filter-section">
      <button class="action-button" @click="requestLocation">
        📍 Use My Location
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useConfigStore } from '../stores/config'

const configStore = useConfigStore()

const props = defineProps({
  modelRadius: {
    type: Number,
    default: 25
  },
  selectedRestaurants: {
    type: Array,
    default: () => []
  },
  restaurants: {
    type: Array,
    default: () => []
  },
  userLocation: {
    type: Object,
    default: null
  }
})

const emit = defineEmits([
  'update:modelRadius',
  'update:selectedRestaurants',
  'radius-change',
  'restaurant-change',
  'request-location',
  'clear-location'
])

// Get radius options from config store
const radiusOptions = computed(() => configStore.appSettings?.radius_options || [5, 10, 25, 50])

const selectRadius = (radius) => {
  emit('update:modelRadius', radius)
  emit('radius-change', radius)
}

const isSelected = (slug) => {
  return props.selectedRestaurants.includes(slug)
}

const toggleRestaurant = (slug) => {
  const selected = [...props.selectedRestaurants]
  const index = selected.indexOf(slug)

  if (index > -1) {
    selected.splice(index, 1)
  } else {
    selected.push(slug)
  }

  emit('update:selectedRestaurants', selected)
  emit('restaurant-change', selected)
}

const clearRestaurants = () => {
  emit('update:selectedRestaurants', [])
  emit('restaurant-change', [])
}

const requestLocation = () => {
  emit('request-location')
}

const clearLocation = () => {
  emit('clear-location')
}
</script>

<style scoped>
.location-filters {
  padding: 16px;
  background: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
}

.filter-section {
  margin-bottom: 16px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.radius-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.radius-button {
  padding: 8px 16px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.radius-button:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

.radius-button.active {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border-color: transparent;
  color: white;
}

.restaurant-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.restaurant-chip {
  padding: 6px 12px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.restaurant-chip:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

.restaurant-chip.active {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border-color: transparent;
  color: white;
}

.clear-button {
  margin-top: 8px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.clear-button:hover {
  color: var(--color-error);
}

.location-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.location-text {
  font-size: 13px;
  color: var(--color-text-primary);
  font-family: monospace;
}

.text-button {
  padding: 4px 8px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.text-button:hover {
  color: var(--color-error);
}

.action-button {
  width: 100%;
  padding: 10px 16px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.action-button:hover {
  opacity: 0.9;
}
</style>
