<template>
  <div class="map-test-view">
    <div class="view-controls">
      <ViewToggle v-model="currentView" :is-mobile="isMobile" @change="handleViewChange" />
    </div>

    <div class="content-area">
      <div v-show="currentView === 'list' || !isMobile" class="list-panel">
        <LocationFilters
          v-model:model-radius="radius"
          v-model:selected-restaurants="selectedRestaurants"
          :restaurants="restaurants"
          :user-location="userLocation"
          @radius-change="handleRadiusChange"
          @restaurant-change="handleRestaurantChange"
          @request-location="handleRequestLocation"
          @clear-location="handleClearLocation"
        />
        <LocationList
          :locations="locations"
          :total="locationsStore.total"
          :radius="locationsStore.radius"
          :loading="loading"
          :error="locationsStore.error"
          :highlighted-id="highlightedLocationId"
          @location-click="handleLocationClick"
          @view-menu="handleViewMenu"
          @report-issue="handleReportIssue"
        />
      </div>

      <div v-show="currentView === 'map' || !isMobile" class="map-panel">
        <MapView
          :center="center"
          :zoom="zoom"
          :locations="locations"
          :userLocation="userLocation"
          @move="handleMapMove"
          @load="handleMapLoad"
          @marker-click="handleMarkerClick"
          @bounds-change="handleBoundsChange"
        />
      </div>
    </div>

    <div class="debug-panel">
      <h2>Map Test View</h2>
      <div v-if="mapLoaded">
        <p>✓ Map loaded successfully</p>
        <p>Store locations: {{ locationsStore.total }}</p>
        <p>Displayed: {{ locations.length }}</p>
        <p>Zoom: {{ mapInfo.zoom?.toFixed(1) }}</p>
        <p v-if="loading" class="loading-text">⏳ Loading...</p>

        <h3>Bounds Tracking</h3>
        <p>Bounds changes: {{ boundsChangeCount }}</p>
        <p v-if="lastBoundsChange">Last: {{ lastBoundsChange }}</p>
        <p class="help-text">Pan/zoom triggers auto-fetch (300ms debounce)</p>

        <div class="button-group">
          <button @click="loadLocations" :disabled="loading">
            {{ loading ? 'Loading...' : 'Load Locations' }}
          </button>
        </div>

        <h3>User Location</h3>
        <div class="button-group">
          <button @click="setUserLocation" :disabled="loading || !!userLocation">
            Set SF Location
          </button>
          <button @click="getUserLocation" :disabled="loading || !!userLocation">
            Get My Location
          </button>
          <button @click="clearUserLocation" :disabled="loading || !userLocation">
            Clear Location
          </button>
        </div>
        <p v-if="userLocation">
          📍 {{ userLocation.lat.toFixed(4) }}, {{ userLocation.lng.toFixed(4) }}
        </p>
        <p v-if="locationsStore.error" class="error-text">
          ❌ {{ locationsStore.error.message }}
        </p>

        <div v-if="selectedMarker" class="selected-marker">
          <h3>Selected Location</h3>
          <p><strong>{{ selectedMarker.name }}</strong></p>
          <p>{{ selectedMarker.restaurant.name }}</p>
        </div>
      </div>
      <div v-else>
        <p>Loading map...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import MapView from '../components/MapView.vue'
import ViewToggle from '../components/ViewToggle.vue'
import LocationList from '../components/LocationList.vue'
import LocationFilters from '../components/LocationFilters.vue'
import { useLocationsStore } from '../stores/locations'
import { useRestaurantsStore } from '../stores/restaurants'

const locationsStore = useLocationsStore()
const { locations, userLocation, loading, radius, selectedRestaurants } = storeToRefs(locationsStore)

const restaurantsStore = useRestaurantsStore()
const { restaurants } = storeToRefs(restaurantsStore)

const currentView = ref('map')
const isMobile = ref(window.innerWidth < 768)
const highlightedLocationId = ref(null)

const center = ref([-74.0060, 40.7128]) // New York City
const zoom = ref(9)  // Zoomed out to see clustering
const mapLoaded = ref(false)
const selectedMarker = ref(null)
const mapInfo = ref({
  center: [],
  zoom: 0,
  bounds: {
    sw: [],
    ne: []
  }
})
const boundsChangeCount = ref(0)
const lastBoundsChange = ref(null)

const handleMapLoad = (map) => {
  mapLoaded.value = true
  console.log('Map loaded:', map)
  // Fetch restaurants for filter
  restaurantsStore.fetchRestaurants()
  // Auto-load locations on map load
  loadLocations()
}

// Watch for store locations updates
watch(() => locationsStore.locations, (newLocations) => {
  console.log('Store locations updated:', newLocations.length, 'locations')
}, { deep: true })

const handleViewChange = (view) => {
  console.log('View changed to:', view)
}

const handleLocationClick = (location) => {
  highlightedLocationId.value = location.id
  selectedMarker.value = location
  console.log('Location clicked from list:', location)
}

const handleViewMenu = (location) => {
  console.log('View menu for:', location.restaurant.name)
  // TODO: Navigate to /search with restaurant filter
}

const handleReportIssue = (location) => {
  console.log('Report issue for:', location.name)
  // TODO: Open flag form modal
}

// Handle window resize for mobile detection
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const handleMapMove = (data) => {
  mapInfo.value = data
  console.log('Map moved:', data)
}

const handleMarkerClick = (location) => {
  highlightedLocationId.value = location.id
  selectedMarker.value = location
  console.log('Marker clicked from map:', location)

  // Switch to list view on mobile to show the selected location
  if (isMobile.value) {
    currentView.value = 'list'
  }
}

const handleBoundsChange = (data) => {
  boundsChangeCount.value++
  lastBoundsChange.value = new Date().toLocaleTimeString()
  console.log('Bounds changed (debounced):', data)

  // Update store with new bounds
  locationsStore.setMapBounds(data)

  // Fetch locations for new bounds
  locationsStore.fetchLocations({ bbox: data.bbox })
}

const loadLocations = async () => {
  // Set initial user location to NYC
  locationsStore.setUserLocation(40.7128, -74.0060)

  // Fetch locations near NYC
  await locationsStore.fetchLocations()
  console.log('Loaded locations:', locations.value.length)
}

const setUserLocation = () => {
  // Set user location to downtown NYC
  locationsStore.setUserLocation(40.7128, -74.0060)
  console.log('User location set:', userLocation.value)
}

const getUserLocation = async () => {
  try {
    await locationsStore.requestUserLocation()
    console.log('Got user location:', userLocation.value)
  } catch (error) {
    console.error('Error getting location:', error)
    // Fallback to SF
    setUserLocation()
  }
}

const clearUserLocation = () => {
  locationsStore.clearUserLocation()
  console.log('User location cleared')
}

const handleRadiusChange = (newRadius) => {
  console.log('Radius changed to:', newRadius)
  locationsStore.setRadius(newRadius)
}

const handleRestaurantChange = (restaurants) => {
  console.log('Selected restaurants:', restaurants)
  locationsStore.setRestaurants(restaurants)
}

const handleRequestLocation = async () => {
  try {
    await locationsStore.requestUserLocation()
    // Fetch locations near user
    await locationsStore.fetchLocations()
    console.log('User location set and locations fetched')
  } catch (error) {
    console.error('Failed to get user location:', error)
  }
}

const handleClearLocation = () => {
  locationsStore.clearUserLocation()
  console.log('User location cleared from filter')
}
</script>

<style scoped>
.map-test-view {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
}

.view-controls {
  padding: 16px;
  background: white;
  border-bottom: 1px solid #E2E8F0;
  display: none;
}

.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.list-panel {
  width: 40%;
  background: #F8FAFC;
  border-right: 1px solid #E2E8F0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-panel > * {
  flex-shrink: 0;
}

.list-panel > :last-child {
  flex: 1;
  min-height: 0;
}

.map-panel {
  flex: 1;
  position: relative;
}

.debug-panel {
  width: 300px;
  padding: 20px;
  background: white;
  overflow-y: auto;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);
  display: none;
}

.info-panel h2 {
  margin-top: 0;
  font-size: 18px;
  font-weight: 600;
}

.info-panel h3 {
  margin-top: 16px;
  font-size: 16px;
  font-weight: 600;
}

.info-panel p {
  margin: 8px 0;
  font-size: 14px;
  font-family: monospace;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 12px 0;
}

.info-panel button {
  padding: 8px 16px;
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.info-panel button:disabled {
  background: #94A3B8;
  cursor: not-allowed;
}

.info-panel button:hover:not(:disabled) {
  background: #2563EB;
}

.selected-marker {
  margin-top: 16px;
  padding: 12px;
  background: #F1F5F9;
  border-radius: 4px;
}

.selected-marker p {
  font-family: system-ui, -apple-system, sans-serif;
}

.help-text {
  font-size: 12px;
  color: #64748B;
  font-style: italic;
}

.loading-text {
  color: #3B82F6;
  font-weight: 500;
}

.error-text {
  color: #EF4444;
  font-size: 13px;
}

/* Mobile styles */
@media (max-width: 768px) {
  .view-controls {
    display: block;
  }

  .content-area {
    position: relative;
    padding-bottom: 60px; /* Space for bottom tabs */
  }

  .list-panel,
  .map-panel {
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }

  .list-panel {
    border-right: none;
  }
}
</style>
