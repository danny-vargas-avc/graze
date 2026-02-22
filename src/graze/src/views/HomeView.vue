<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLocationsStore } from '../stores/locations'
import { useRestaurantsStore } from '../stores/restaurants'
import { useConfigStore } from '../stores/config'
import { useSheetDrag } from '../composables/useSheetDrag'
// import { getDishes } from '../api/dishes'

import MapView from '../components/MapView.vue'
import MapBottomSheet from '../components/MapBottomSheet.vue'
// import SearchBar from '../components/SearchBar.vue'

const router = useRouter()
const locationsStore = useLocationsStore()
const restaurantsStore = useRestaurantsStore()
const configStore = useConfigStore()

const { locations, userLocation } = storeToRefs(locationsStore)

// --- Desktop detection ---
const isDesktop = ref(false)
let desktopQuery = null

function onDesktopChange(e) {
  isDesktop.value = e.matches
}

// --- Map config ---
const mapViewRef = ref(null)
const center = computed(() => configStore.appSettings?.default_map_center || [-74.0060, 40.7128])
const zoom = computed(() => configStore.appSettings?.default_map_zoom || 12)

// --- Sheet setup (mobile only) ---
const PEEK_HEIGHT = 76

function calcHalf() { return window.innerHeight * 0.5 }
function calcFull() { return window.innerHeight - 80 }

const { sheetRef, handleRef, sheetStyle, currentHeight, snapTo, updateSnapPoints } = useSheetDrag({
  snapPoints: [PEEK_HEIGHT, calcHalf(), calcFull()],
  initialSnap: 1,
})

const sheetContentRef = ref(null)

function recalcSnapPoints() {
  updateSnapPoints([PEEK_HEIGHT, calcHalf(), calcFull()])
}

// Scroll content to top when sheet collapses to peek
watch(currentHeight, (height) => {
  if (height <= PEEK_HEIGHT && sheetContentRef.value) {
    sheetContentRef.value.scrollTop = 0
  }
})

// --- Location sheet (marker click) ---
const selectedLocation = ref(null)
const showLocationSheet = ref(false)

function handleMapLoad() {
  locationsStore.fetchLocations()
}

function handleMarkerClick(markerData) {
  const fullLocation = locations.value.find(l => l.id === markerData.id)
  selectedLocation.value = fullLocation || {
    id: markerData.id,
    name: markerData.name,
    restaurant: markerData.restaurant,
    latitude: markerData.coordinates[1],
    longitude: markerData.coordinates[0],
  }
  showLocationSheet.value = true
  if (!isDesktop.value) snapTo(0)
}

function handleCloseLocationSheet() {
  showLocationSheet.value = false
  selectedLocation.value = null
}

function handleViewAll(restaurantSlug) {
  router.push({ name: 'restaurant-detail', params: { slug: restaurantSlug } })
}

function handleBoundsChange(data) {
  locationsStore.setMapBounds(data)
  locationsStore.fetchLocations({ bbox: data.bbox })
}

// --- Nearby restaurants from map locations ---
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 3959
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

const nearbyRestaurants = computed(() => {
  const grouped = {}

  for (const loc of locations.value) {
    const slug = loc.restaurant?.slug
    if (!slug) continue

    if (!grouped[slug]) {
      grouped[slug] = {
        slug,
        name: loc.restaurant.name,
        logoUrl: loc.restaurant.logo_url,
        itemCount: loc.restaurant.item_count,
        locationCount: 0,
        nearestDistance: Infinity,
        nearestLocation: null,
      }
    }

    grouped[slug].locationCount++

    if (userLocation.value) {
      const dist = haversineDistance(
        userLocation.value.lat, userLocation.value.lng,
        parseFloat(loc.latitude), parseFloat(loc.longitude)
      )
      if (dist < grouped[slug].nearestDistance) {
        grouped[slug].nearestDistance = dist
        grouped[slug].nearestLocation = loc
      }
    } else if (!grouped[slug].nearestLocation) {
      grouped[slug].nearestLocation = loc
    }
  }

  let list = Object.values(grouped)

  if (userLocation.value) {
    list.sort((a, b) => a.nearestDistance - b.nearestDistance)
  } else {
    list.sort((a, b) => a.name.localeCompare(b.name))
  }

  return list
})

// --- Search (commented out — map is the search for now) ---
// const searchQuery = ref('')
// const searchResults = ref([])
// const searchLoading = ref(false)
// let searchController = null
// const isSearching = computed(() => searchQuery.value.trim().length > 0)
// const searchRestaurantSlugs = computed(() => {
//   if (!isSearching.value || searchResults.value.length === 0) return null
//   return new Set(searchResults.value.map(d => d.restaurant?.slug).filter(Boolean))
// })
// function handleSearch(value) { ... }

const mapLocations = computed(() => locations.value)
const displayedRestaurants = computed(() => nearbyRestaurants.value)

// --- Restaurant tap → fly to pin ---
function handleRestaurantTap(restaurant) {
  const loc = restaurant.nearestLocation
  if (!loc) return

  const map = mapViewRef.value?.getMap()
  if (map) {
    map.flyTo({
      center: [parseFloat(loc.longitude), parseFloat(loc.latitude)],
      zoom: 15,
      duration: 800,
    })
  }

  handleMarkerClick({
    id: loc.id,
    name: loc.name,
    restaurant: loc.restaurant,
    coordinates: [parseFloat(loc.longitude), parseFloat(loc.latitude)],
  })
}

// --- Config helpers ---
const getColor = (slug) => configStore.getRestaurantColor(slug)
const getIcon = (slug) => configStore.getRestaurantIcon(slug)

// --- Locate me ---
let hasAutoFlown = false

function flyToUser() {
  const loc = userLocation.value
  const map = mapViewRef.value?.getMap()
  if (!loc || !map) return
  map.flyTo({ center: [loc.lng, loc.lat], zoom: 13, duration: 1000 })
}

function handleLocateMe() {
  if (userLocation.value) {
    flyToUser()
  } else {
    locationsStore.requestUserLocation()
      .then(() => flyToUser())
      .catch(() => {})
  }
}

// Auto-fly to user on first location grant
watch(userLocation, (loc) => {
  if (loc && !hasAutoFlown) {
    hasAutoFlown = true
    flyToUser()
  }
})

// --- Lifecycle ---
onMounted(() => {
  desktopQuery = window.matchMedia('(min-width: 1024px)')
  isDesktop.value = desktopQuery.matches
  desktopQuery.addEventListener('change', onDesktopChange)

  restaurantsStore.fetchRestaurants()
  locationsStore.fetchLocations()
  window.addEventListener('resize', recalcSnapPoints)

  locationsStore.requestUserLocation().catch(() => {})
})

onUnmounted(() => {
  window.removeEventListener('resize', recalcSnapPoints)
  if (desktopQuery) {
    desktopQuery.removeEventListener('change', onDesktopChange)
  }
})
</script>

<template>
  <div class="home-view" :class="{ 'home-desktop': isDesktop }">
    <!-- ============ DESKTOP LAYOUT (1024px+) ============ -->
    <template v-if="isDesktop">
      <div class="desktop-list-panel">
        <div class="desktop-list-content">
          <div class="list-header">
            <p class="list-summary">
              {{ displayedRestaurants.length }} restaurant{{ displayedRestaurants.length !== 1 ? 's' : '' }} nearby
            </p>
          </div>

          <div class="restaurant-list">
            <button
              v-for="r in displayedRestaurants"
              :key="r.slug"
              class="restaurant-row"
              @click="handleRestaurantTap(r)"
            >
              <div class="row-icon">
                <img v-if="getIcon(r.slug) || r.logoUrl" :src="getIcon(r.slug) || r.logoUrl" :alt="r.name" />
                <div v-else class="icon-fallback" :style="{ backgroundColor: getColor(r.slug) }">
                  {{ r.name.charAt(0) }}
                </div>
              </div>
              <div class="row-info">
                <span class="row-name">{{ r.name }}</span>
                <span class="row-meta">{{ r.itemCount }} items · {{ r.locationCount }} location{{ r.locationCount !== 1 ? 's' : '' }}</span>
              </div>
              <div v-if="r.nearestDistance < Infinity" class="row-distance">
                {{ r.nearestDistance < 10 ? r.nearestDistance.toFixed(1) : Math.round(r.nearestDistance) }} mi
              </div>
              <svg class="row-chevron" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <div v-if="!displayedRestaurants.length" class="empty-list">
            <p class="empty-title">No restaurants in view</p>
            <p class="empty-sub">Pan or zoom the map to explore</p>
          </div>
        </div>
      </div>

      <div class="desktop-map-panel">
        <MapView
          ref="mapViewRef"
          :center="center"
          :zoom="zoom"
          :locations="mapLocations"
          :userLocation="userLocation"
          @load="handleMapLoad"
          @marker-click="handleMarkerClick"
          @bounds-change="handleBoundsChange"
        />
        <button class="locate-btn" @click="handleLocateMe" aria-label="Center on my location">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke-linecap="round" />
          </svg>
        </button>
        <MapBottomSheet
          v-if="showLocationSheet && selectedLocation"
          :location="selectedLocation"
          @close="handleCloseLocationSheet"
          @view-all="handleViewAll"
        />
      </div>
    </template>

    <!-- ============ MOBILE LAYOUT (<1024px) ============ -->
    <template v-else>
      <MapView
        ref="mapViewRef"
        :center="center"
        :zoom="zoom"
        :locations="mapLocations"
        :userLocation="userLocation"
        @load="handleMapLoad"
        @marker-click="handleMarkerClick"
        @bounds-change="handleBoundsChange"
      />

      <button class="locate-btn mobile-locate" @click="handleLocateMe" aria-label="Center on my location">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke-linecap="round" />
        </svg>
      </button>

      <div ref="sheetRef" class="list-sheet" :style="sheetStyle">
        <div ref="handleRef" class="sheet-handle-area">
          <div class="handle-bar-wrapper">
            <div class="handle-bar"></div>
          </div>
        </div>

        <div ref="sheetContentRef" class="sheet-content">
          <div class="list-header">
            <p class="list-summary">
              {{ displayedRestaurants.length }} restaurant{{ displayedRestaurants.length !== 1 ? 's' : '' }} nearby
            </p>
          </div>

          <div class="restaurant-list">
            <button
              v-for="r in displayedRestaurants"
              :key="r.slug"
              class="restaurant-row"
              @click="handleRestaurantTap(r)"
            >
              <div class="row-icon">
                <img v-if="getIcon(r.slug) || r.logoUrl" :src="getIcon(r.slug) || r.logoUrl" :alt="r.name" />
                <div v-else class="icon-fallback" :style="{ backgroundColor: getColor(r.slug) }">
                  {{ r.name.charAt(0) }}
                </div>
              </div>
              <div class="row-info">
                <span class="row-name">{{ r.name }}</span>
                <span class="row-meta">{{ r.itemCount }} items · {{ r.locationCount }} location{{ r.locationCount !== 1 ? 's' : '' }}</span>
              </div>
              <div v-if="r.nearestDistance < Infinity" class="row-distance">
                {{ r.nearestDistance < 10 ? r.nearestDistance.toFixed(1) : Math.round(r.nearestDistance) }} mi
              </div>
              <svg class="row-chevron" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <div v-if="!displayedRestaurants.length" class="empty-list">
            <p class="empty-title">No restaurants in view</p>
            <p class="empty-sub">Pan or zoom the map to explore</p>
          </div>
        </div>
      </div>

      <MapBottomSheet
        v-if="showLocationSheet && selectedLocation"
        :location="selectedLocation"
        @close="handleCloseLocationSheet"
        @view-all="handleViewAll"
      />
    </template>
  </div>
</template>

<style scoped>
.home-view {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

/* ============ DESKTOP ============ */
.home-desktop {
  display: flex;
  flex-direction: row;
}

.desktop-list-panel {
  width: 40%;
  min-width: 380px;
  max-width: 520px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface-elevated);
  border-right: 1px solid var(--color-border);
  z-index: 5;
}

.desktop-list-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding-bottom: 24px;
}

.desktop-map-panel {
  flex: 1;
  height: 100%;
  position: relative;
}

/* ============ MOBILE (sheet) ============ */
.list-sheet {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface-elevated);
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15), 0 200px 0 0 var(--color-surface-elevated);
  z-index: 5;
}

.sheet-handle-area {
  cursor: grab;
  touch-action: none;
  flex-shrink: 0;
}

.sheet-handle-area:active {
  cursor: grabbing;
}

.handle-bar-wrapper {
  display: flex;
  justify-content: center;
  padding: 10px 0 6px;
}

.handle-bar {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background-color: var(--color-border);
}

.sheet-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding-bottom: calc(24px + env(safe-area-inset-bottom));
}

/* ============ RESTAURANT LIST ============ */
.list-header {
  padding: 12px 16px 4px;
}

.list-summary {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-tertiary);
}

.restaurant-list {
  display: flex;
  flex-direction: column;
}

.restaurant-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background-color 150ms ease;
}

.restaurant-row:hover {
  background-color: var(--color-surface);
}

.restaurant-row:active {
  background-color: var(--color-border);
}

.row-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.row-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.icon-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  border-radius: 6px;
}

.row-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.row-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-meta {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 1px;
}

.row-distance {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background-color: var(--color-surface);
  padding: 3px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.row-chevron {
  width: 16px;
  height: 16px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

/* ============ LOCATE BUTTON ============ */
.locate-btn {
  position: absolute;
  bottom: 24px;
  right: 16px;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: var(--color-surface-elevated);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4;
  transition: background-color 150ms ease;
}

.locate-btn:hover {
  background-color: var(--color-surface);
}

.locate-btn:active {
  background-color: var(--color-border);
}

.locate-btn svg {
  width: 20px;
  height: 20px;
  color: var(--color-text-primary);
}

.mobile-locate {
  bottom: auto;
  top: 16px;
  right: 16px;
}

/* ============ EMPTY STATE ============ */
.empty-list {
  text-align: center;
  padding: 48px 16px;
  color: var(--color-text-tertiary);
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.empty-sub {
  font-size: 13px;
}
</style>
