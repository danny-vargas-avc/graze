<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLocationsStore } from '../stores/locations'
import { useConfigStore } from '../stores/config'
import MapView from '../components/MapView.vue'
import MapBottomSheet from '../components/MapBottomSheet.vue'

const router = useRouter()
const locationsStore = useLocationsStore()
const configStore = useConfigStore()
const { locations, userLocation } = storeToRefs(locationsStore)

const mapViewRef = ref(null)
const selectedLocation = ref(null)
const showSheet = ref(false)

const center = computed(() => configStore.appSettings?.default_map_center || [-74.0060, 40.7128])
const zoom = computed(() => configStore.appSettings?.default_map_zoom || 12)

function handleMapLoad() {
  locationsStore.fetchLocations()
}

function handleMarkerClick(location) {
  selectedLocation.value = location
  showSheet.value = true
}

function handleBoundsChange(data) {
  locationsStore.setMapBounds(data)
  locationsStore.fetchLocations({ bbox: data.bbox })
}

function handleViewAll(restaurantSlug) {
  router.push({ name: 'restaurant-detail', params: { slug: restaurantSlug } })
}

function handleCloseSheet() {
  showSheet.value = false
  selectedLocation.value = null
}

onMounted(() => {
  locationsStore.fetchLocations()
})
</script>

<template>
  <div class="map-explore">
    <MapView
      ref="mapViewRef"
      :center="center"
      :zoom="zoom"
      :locations="locations"
      :userLocation="userLocation"
      @load="handleMapLoad"
      @marker-click="handleMarkerClick"
      @bounds-change="handleBoundsChange"
    />

    <!-- Bottom sheet for selected location -->
    <MapBottomSheet
      v-if="showSheet && selectedLocation"
      :location="selectedLocation"
      @close="handleCloseSheet"
      @view-all="handleViewAll"
    />
  </div>
</template>

<style scoped>
.map-explore {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
