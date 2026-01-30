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

const radiusOptions = [5, 10, 25, 50]

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
  background: white;
  border-bottom: 1px solid #E2E8F0;
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
  color: #1E293B;
  margin-bottom: 8px;
}

.radius-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.radius-button {
  padding: 8px 16px;
  background: #F1F5F9;
  border: 2px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s;
}

.radius-button:hover {
  background: #E2E8F0;
  color: #475569;
}

.radius-button.active {
  background: #EFF6FF;
  border-color: #3B82F6;
  color: #3B82F6;
}

.restaurant-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.restaurant-chip {
  padding: 6px 12px;
  background: #F1F5F9;
  border: 2px solid transparent;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s;
}

.restaurant-chip:hover {
  background: #E2E8F0;
  color: #475569;
}

.restaurant-chip.active {
  background: #EFF6FF;
  border-color: #3B82F6;
  color: #3B82F6;
}

.clear-button {
  margin-top: 8px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: #64748B;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.clear-button:hover {
  color: #EF4444;
}

.location-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #F1F5F9;
  border-radius: 6px;
}

.location-text {
  font-size: 13px;
  color: #475569;
  font-family: monospace;
}

.text-button {
  padding: 4px 8px;
  background: transparent;
  border: none;
  color: #64748B;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.text-button:hover {
  color: #EF4444;
}

.action-button {
  width: 100%;
  padding: 10px 16px;
  background: #3B82F6;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.action-button:hover {
  background: #2563EB;
}
</style>
