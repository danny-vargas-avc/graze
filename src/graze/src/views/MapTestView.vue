<template>
  <div class="map-test-view">
    <div class="map-wrapper">
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
    <div class="info-panel">
      <h2>Map Test View</h2>
      <div v-if="mapLoaded">
        <p>✓ Map loaded successfully</p>
        <p>Locations: {{ locations.length }}</p>
        <p>Zoom: {{ mapInfo.zoom?.toFixed(1) }}</p>

        <h3>Bounds Tracking</h3>
        <p>Bounds changes (debounced): {{ boundsChangeCount }}</p>
        <p v-if="lastBoundsChange">Last change: {{ lastBoundsChange }}</p>
        <p class="help-text">Pan/zoom the map to trigger bounds-change events (300ms debounce)</p>

        <div class="button-group">
          <button @click="loadLocations" :disabled="loading">
            {{ loading ? 'Loading...' : 'Load Locations' }}
          </button>
        </div>

        <h3>User Location</h3>
        <div class="button-group">
          <button @click="setUserLocation" :disabled="!!userLocation">
            Set SF Location
          </button>
          <button @click="getUserLocation" :disabled="!!userLocation">
            Get My Location
          </button>
          <button @click="clearUserLocation" :disabled="!userLocation">
            Clear Location
          </button>
        </div>
        <p v-if="userLocation">
          📍 {{ userLocation.lat.toFixed(4) }}, {{ userLocation.lng.toFixed(4) }}
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
import { ref } from 'vue'
import axios from 'axios'
import MapView from '../components/MapView.vue'

const center = ref([-122.4194, 37.7749]) // San Francisco
const zoom = ref(9)  // Zoomed out to see clustering
const mapLoaded = ref(false)
const loading = ref(false)
const locations = ref([])
const selectedMarker = ref(null)
const userLocation = ref(null)
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
  // Auto-load locations on map load
  loadLocations()
}

const handleMapMove = (data) => {
  mapInfo.value = data
  console.log('Map moved:', data)
}

const handleMarkerClick = (location) => {
  selectedMarker.value = location
  console.log('Marker clicked:', location)
}

const handleBoundsChange = (data) => {
  boundsChangeCount.value++
  lastBoundsChange.value = new Date().toLocaleTimeString()
  console.log('Bounds changed (debounced):', data)
  console.log('Bbox string:', data.bbox)
}

const loadLocations = async () => {
  loading.value = true
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    // Load all locations in viewport without radius filter to see clustering
    const response = await axios.get(`${apiUrl}/locations`, {
      params: {
        lat: 37.7749,
        lng: -122.4194,
        radius: 100,  // Increased radius to get more locations
        limit: 100
      }
    })
    locations.value = response.data.data
    console.log('Loaded locations:', locations.value.length)
  } catch (error) {
    console.error('Error loading locations:', error)
  } finally {
    loading.value = false
  }
}

const setUserLocation = () => {
  // Set user location to downtown SF
  userLocation.value = {
    lat: 37.7749,
    lng: -122.4194
  }
  console.log('User location set:', userLocation.value)
}

const getUserLocation = () => {
  // Use browser geolocation API
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userLocation.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        }
        console.log('Got user location:', userLocation.value)
      },
      (error) => {
        console.error('Error getting location:', error)
        // Fallback to SF
        setUserLocation()
      }
    )
  } else {
    console.error('Geolocation not supported')
    setUserLocation()
  }
}

const clearUserLocation = () => {
  userLocation.value = null
  console.log('User location cleared')
}
</script>

<style scoped>
.map-test-view {
  display: flex;
  width: 100vw;
  height: 100vh;
}

.map-wrapper {
  flex: 1;
  height: 100%;
}

.info-panel {
  width: 300px;
  padding: 20px;
  background: white;
  overflow-y: auto;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);
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
</style>
