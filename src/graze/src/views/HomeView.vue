<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLocationsStore } from '../stores/locations'
import { useRestaurantsStore } from '../stores/restaurants'
import { useConfigStore } from '../stores/config'
import { useSheetDrag } from '../composables/useSheetDrag'
import { getDishes } from '../api/dishes'

import MapView from '../components/MapView.vue'
import MapBottomSheet from '../components/MapBottomSheet.vue'
import SearchBar from '../components/SearchBar.vue'
import CategoryPills from '../components/CategoryPills.vue'
import CarouselSection from '../components/CarouselSection.vue'
import RestaurantCard from '../components/RestaurantCard.vue'
import DishCardCompact from '../components/DishCardCompact.vue'

const router = useRouter()
const locationsStore = useLocationsStore()
const restaurantsStore = useRestaurantsStore()
const configStore = useConfigStore()

const { locations, userLocation } = storeToRefs(locationsStore)
const { restaurants } = storeToRefs(restaurantsStore)

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

// --- Visible restaurants from map ---
const visibleRestaurantSlugs = computed(() => {
  return new Set(locations.value.map(l => l.restaurant?.slug).filter(Boolean))
})

const visibleRestaurants = computed(() => {
  if (visibleRestaurantSlugs.value.size === 0) return restaurants.value
  return restaurants.value.filter(r => visibleRestaurantSlugs.value.has(r.slug))
})

let prevSlugsKey = ''

watch(visibleRestaurantSlugs, (newSlugs) => {
  const key = [...newSlugs].sort().join(',')
  if (key !== prevSlugsKey) {
    prevSlugsKey = key
    fetchCarousels(activeCategory.value, key || null)
  }
})

// --- Carousel data ---
const activeCategory = ref(null)
const highProteinDishes = ref([])
const lowCalDishes = ref([])
const bestRatioDishes = ref([])
const bowlDishes = ref([])
const saladDishes = ref([])
const burgerDishes = ref([])
const loading = ref(true)

async function fetchCarousels(category = null, restaurantSlugs = null) {
  loading.value = true
  try {
    const base = {}
    if (category) base.category = category
    if (restaurantSlugs) base.restaurants = restaurantSlugs

    const corePromises = [
      getDishes({ ...base, sort: 'protein_desc', limit: 10 }),
      getDishes({ ...base, calories_max: 500, sort: 'protein_ratio_desc', limit: 10 }),
      getDishes({ ...base, sort: 'protein_ratio_desc', limit: 10 }),
    ]

    const categoryPromises = category ? [] : [
      getDishes({ ...base, category: 'bowl', sort: 'protein_desc', limit: 10 }),
      getDishes({ ...base, category: 'salad', sort: 'protein_desc', limit: 10 }),
      getDishes({ ...base, category: 'burger', sort: 'protein_desc', limit: 10 }),
    ]

    const results = await Promise.all([...corePromises, ...categoryPromises])

    highProteinDishes.value = results[0].data
    lowCalDishes.value = results[1].data
    bestRatioDishes.value = results[2].data

    if (!category) {
      bowlDishes.value = results[3].data
      saladDishes.value = results[4].data
      burgerDishes.value = results[5].data
    } else {
      bowlDishes.value = []
      saladDishes.value = []
      burgerDishes.value = []
    }
  } catch (e) {
    console.error('Failed to load carousel data:', e)
  } finally {
    loading.value = false
  }
}

// --- Search ---
const searchQuery = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
let searchController = null

const isSearching = computed(() => searchQuery.value.trim().length > 0)

// Filter map locations to match search results
const searchRestaurantSlugs = computed(() => {
  if (!isSearching.value || searchResults.value.length === 0) return null
  return new Set(searchResults.value.map(d => d.restaurant?.slug).filter(Boolean))
})

const mapLocations = computed(() => {
  if (!searchRestaurantSlugs.value) return locations.value
  return locations.value.filter(l => searchRestaurantSlugs.value.has(l.restaurant?.slug))
})

function handleSearch(value) {
  searchQuery.value = value

  if (searchController) searchController.abort()

  if (!value.trim()) {
    searchResults.value = []
    searchLoading.value = false
    return
  }

  searchLoading.value = true
  searchController = new AbortController()

  getDishes({ search: value.trim(), sort: 'protein_ratio_desc', limit: 50 }, searchController.signal)
    .then(result => {
      searchResults.value = result.data
      searchLoading.value = false
    })
    .catch(err => {
      if (err.name !== 'CanceledError') {
        searchLoading.value = false
      }
    })
}

function handleCategoryChange(category) {
  activeCategory.value = category
  fetchCarousels(category, prevSlugsKey || null)
}

// --- Lifecycle ---
onMounted(() => {
  desktopQuery = window.matchMedia('(min-width: 1024px)')
  isDesktop.value = desktopQuery.matches
  desktopQuery.addEventListener('change', onDesktopChange)

  restaurantsStore.fetchRestaurants()
  locationsStore.fetchLocations()
  fetchCarousels()
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
      <!-- Left panel: scrollable list -->
      <div class="desktop-list-panel">
        <div class="desktop-search">
          <SearchBar
            :model-value="searchQuery"
            @update:model-value="handleSearch"
            placeholder="Search dishes or restaurants..."
          />
        </div>

        <div class="desktop-list-content">
          <!-- Search results -->
          <template v-if="isSearching">
            <div class="search-results-header">
              <p v-if="searchLoading" class="results-info">Searching...</p>
              <p v-else class="results-info">{{ searchResults.length }} result{{ searchResults.length !== 1 ? 's' : '' }} for "{{ searchQuery }}"</p>
            </div>
            <div v-if="searchLoading" class="search-results-grid">
              <div v-for="i in 6" :key="i" class="skeleton-card search-skeleton"></div>
            </div>
            <div v-else-if="searchResults.length" class="search-results-grid">
              <DishCardCompact
                v-for="dish in searchResults"
                :key="dish.id"
                :dish="dish"
              />
            </div>
            <div v-else class="empty-search">
              <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <p class="empty-title">No results found</p>
              <p class="empty-sub">Try a different search term</p>
            </div>
          </template>

          <!-- Carousel content -->
          <template v-else>
            <CategoryPills :active="activeCategory" @change="handleCategoryChange" />

            <CarouselSection title="Restaurants" see-all-to="/restaurants">
              <div class="carousel-scroll hide-scrollbar">
                <RestaurantCard
                  v-for="restaurant in visibleRestaurants"
                  :key="restaurant.slug"
                  :restaurant="restaurant"
                />
              </div>
            </CarouselSection>

            <CarouselSection title="Highest Protein" icon="protein">
              <div class="carousel-scroll hide-scrollbar">
                <template v-if="loading">
                  <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                </template>
                <DishCardCompact v-else v-for="dish in highProteinDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection title="Under 500 Calories" icon="calories">
              <div class="carousel-scroll hide-scrollbar">
                <template v-if="loading">
                  <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                </template>
                <DishCardCompact v-else v-for="dish in lowCalDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection title="Best Protein Ratio" icon="ratio">
              <div class="carousel-scroll hide-scrollbar">
                <template v-if="loading">
                  <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                </template>
                <DishCardCompact v-else v-for="dish in bestRatioDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection v-if="bowlDishes.length" title="Top Bowls" icon="bowl">
              <div class="carousel-scroll hide-scrollbar">
                <DishCardCompact v-for="dish in bowlDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection v-if="saladDishes.length" title="Top Salads" icon="salad">
              <div class="carousel-scroll hide-scrollbar">
                <DishCardCompact v-for="dish in saladDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection v-if="burgerDishes.length" title="Top Burgers" icon="burger">
              <div class="carousel-scroll hide-scrollbar">
                <DishCardCompact v-for="dish in burgerDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>
          </template>
        </div>
      </div>

      <!-- Right panel: map -->
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

      <div ref="sheetRef" class="list-sheet" :style="sheetStyle">
        <div ref="handleRef" class="sheet-handle-area">
          <div class="handle-bar-wrapper">
            <div class="handle-bar"></div>
          </div>
          <div class="sheet-search">
            <SearchBar
              :model-value="searchQuery"
              @update:model-value="handleSearch"
              placeholder="Search dishes or restaurants..."
            />
          </div>
        </div>

        <div ref="sheetContentRef" class="sheet-content">
          <template v-if="isSearching">
            <div class="search-results-header">
              <p v-if="searchLoading" class="results-info">Searching...</p>
              <p v-else class="results-info">{{ searchResults.length }} result{{ searchResults.length !== 1 ? 's' : '' }} for "{{ searchQuery }}"</p>
            </div>
            <div v-if="searchLoading" class="search-results-grid">
              <div v-for="i in 6" :key="i" class="skeleton-card search-skeleton"></div>
            </div>
            <div v-else-if="searchResults.length" class="search-results-grid">
              <DishCardCompact
                v-for="dish in searchResults"
                :key="dish.id"
                :dish="dish"
              />
            </div>
            <div v-else class="empty-search">
              <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <p class="empty-title">No results found</p>
              <p class="empty-sub">Try a different search term</p>
            </div>
          </template>

          <template v-else>
            <CategoryPills :active="activeCategory" @change="handleCategoryChange" />

            <CarouselSection title="Restaurants" see-all-to="/restaurants">
              <div class="carousel-scroll hide-scrollbar">
                <RestaurantCard
                  v-for="restaurant in visibleRestaurants"
                  :key="restaurant.slug"
                  :restaurant="restaurant"
                />
              </div>
            </CarouselSection>

            <CarouselSection title="Highest Protein" icon="protein">
              <div class="carousel-scroll hide-scrollbar">
                <template v-if="loading">
                  <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                </template>
                <DishCardCompact v-else v-for="dish in highProteinDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection title="Under 500 Calories" icon="calories">
              <div class="carousel-scroll hide-scrollbar">
                <template v-if="loading">
                  <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                </template>
                <DishCardCompact v-else v-for="dish in lowCalDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection title="Best Protein Ratio" icon="ratio">
              <div class="carousel-scroll hide-scrollbar">
                <template v-if="loading">
                  <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                </template>
                <DishCardCompact v-else v-for="dish in bestRatioDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection v-if="bowlDishes.length" title="Top Bowls" icon="bowl">
              <div class="carousel-scroll hide-scrollbar">
                <DishCardCompact v-for="dish in bowlDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection v-if="saladDishes.length" title="Top Salads" icon="salad">
              <div class="carousel-scroll hide-scrollbar">
                <DishCardCompact v-for="dish in saladDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>

            <CarouselSection v-if="burgerDishes.length" title="Top Burgers" icon="burger">
              <div class="carousel-scroll hide-scrollbar">
                <DishCardCompact v-for="dish in burgerDishes" :key="dish.id" :dish="dish" />
              </div>
            </CarouselSection>
          </template>
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

.desktop-search {
  padding: 16px 16px 8px;
  flex-shrink: 0;
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

/* Keep search grid 2-col inside narrow desktop panel */
.desktop-list-panel .search-results-grid {
  grid-template-columns: repeat(2, 1fr);
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

.sheet-search {
  padding: 0 16px 8px;
}

.sheet-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding-bottom: calc(24px + env(safe-area-inset-bottom));
}

/* ============ SHARED ============ */
.carousel-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-padding-left: 16px;
}

.carousel-scroll::before,
.carousel-scroll::after {
  content: '';
  min-width: 16px;
  flex-shrink: 0;
}

.carousel-scroll > * {
  scroll-snap-align: start;
  flex-shrink: 0;
}

/* Skeletons */
.skeleton-card {
  width: 200px;
  height: 180px;
  border-radius: 12px;
  background: var(--color-surface);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Search results */
.search-results-header {
  padding: 12px 16px 0;
}

.results-info {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.search-results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px 16px;
}

.search-results-grid :deep(.dish-compact) {
  width: 100%;
}

.search-results-grid .search-skeleton {
  width: 100%;
  height: 200px;
  border-radius: 12px;
}

.empty-search {
  text-align: center;
  padding: 60px 16px;
  color: var(--color-text-tertiary);
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  opacity: 0.4;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.empty-sub {
  font-size: 14px;
}

@media (min-width: 640px) {
  .search-results-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
