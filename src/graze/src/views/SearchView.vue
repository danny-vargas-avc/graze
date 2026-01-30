<template>
  <div class="search-view">
    <!-- Mobile view toggle -->
    <div class="view-controls">
      <ViewToggle v-model="currentView" :is-mobile="isMobile" @change="handleViewChange" />
    </div>

    <div class="content-area">
      <!-- Left panel: Dish filters and list -->
      <div v-show="currentView === 'list' || !isMobile" class="list-panel">
        <!-- Filters - Desktop only -->
        <div class="filters-section desktop-only">
          <SearchBar :model-value="search" @update:model-value="handleSearch" />

          <!-- Quick filters -->
          <div class="quick-filters">
            <FilterChip
              v-for="filter in quickFilters"
              :key="filter.id"
              :label="filter.label"
              @click="handleQuickFilter(filter.id)"
            />
          </div>

          <!-- Main filters -->
          <div class="main-filters">
            <FilterAccordion title="Calories" :default-open="true">
              <FilterSection
                label=""
                :options="calorieOptions"
                v-model="caloriesFilter"
              />
            </FilterAccordion>

            <FilterAccordion title="Protein" :default-open="true">
              <FilterSection
                label=""
                :options="proteinOptions"
                v-model="proteinFilter"
              />
            </FilterAccordion>

            <FilterAccordion title="Carbs">
              <FilterSection
                label=""
                :options="carbsOptions"
                :model-value="{ min: null, max: carbsMax }"
                @update:model-value="(val) => dishesStore.setCarbsFilter(val.max)"
              />
            </FilterAccordion>

            <FilterAccordion title="Fat">
              <FilterSection
                label=""
                :options="fatOptions"
                :model-value="{ min: fatMin, max: fatMax }"
                @update:model-value="(val) => dishesStore.setFatFilter(val.min, val.max)"
              />
            </FilterAccordion>

            <FilterAccordion title="Restaurants">
              <RestaurantFilter
                :selected="selectedRestaurants"
                @toggle="handleRestaurantToggle"
              />
            </FilterAccordion>
          </div>
        </div>

        <!-- Results header -->
        <div class="results-header">
          <div class="results-info">
            <!-- Mobile filter button -->
            <button class="filter-button mobile-only" @click="showFilterDrawer = true">
              <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>Filters</span>
              <span v-if="activeFilterCount > 0" class="filter-count">{{ activeFilterCount }}</span>
            </button>

            <p class="results-count">
              <span v-if="loading && dishes.length === 0">Loading...</span>
              <span v-else>{{ dishes.length }} of {{ total }} dishes</span>
            </p>
          </div>
          <SortDropdown
            :model-value="sort"
            :show-distance="!!dishesStore.userLocation"
            @update:model-value="handleSort"
          />
        </div>

        <!-- Dish list -->
        <div class="dish-list">
          <ErrorState v-if="error && dishes.length === 0" :error="error" @retry="handleRetry" />

          <EmptyState
            v-else-if="!loading && dishes.length === 0"
            title="No dishes match your filters"
            message="Try adjusting your filters or clear them to see all dishes."
            :show-clear-filters="activeFilterCount > 0"
            @clear="handleClearFilters"
          />

          <div v-else class="dish-grid">
            <div
              v-for="dish in dishes"
              :key="dish.id"
              :data-dish-id="dish.id"
              @mouseenter="handleDishHover(dish)"
              @mouseleave="handleDishHover(null)"
            >
              <DishCard
                :dish="dish"
                :class="{ 'highlighted': highlightedDishId === dish.id }"
              />
            </div>
          </div>

          <LoadMoreButton
            :loading="loading"
            :has-more="hasMore"
            :shown="dishes.length"
            :total="total"
            @click="handleLoadMore"
          />
        </div>
      </div>

      <!-- Right panel: Map -->
      <div v-show="currentView === 'map' || !isMobile" class="map-panel">
        <!-- Loading overlay -->
        <div v-if="locationsStore.loading" class="map-loading-overlay">
          <div class="loading-spinner">
            <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-sm text-secondary mt-2">Loading locations...</p>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="!locationsStore.loading && matchingLocations.length === 0" class="map-empty-overlay">
          <div class="empty-content">
            <svg class="w-16 h-16 text-tertiary mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h3 class="text-lg font-semibold text-primary mb-2">No locations found</h3>
            <p class="text-sm text-secondary">Try adjusting your filters or clearing them</p>
          </div>
        </div>

        <MapView
          ref="mapViewRef"
          :center="center"
          :zoom="zoom"
          :locations="matchingLocations"
          :dishes="dishes"
          :userLocation="userLocation"
          :highlightedRestaurantSlug="highlightedRestaurantSlug"
          @load="handleMapLoad"
          @marker-click="handleMarkerClick"
          @bounds-change="handleBoundsChange"
          @dish-click="handleMapDishClick"
          @view-all-dishes="handleViewAllDishes"
        />
      </div>
    </div>

    <!-- Mobile Filter Drawer -->
    <FilterDrawer
      v-model="showFilterDrawer"
      :active-filter-count="activeFilterCount"
      @clear-filters="handleClearFilters"
    >
      <SearchBar :model-value="search" @update:model-value="handleSearch" />

      <!-- Quick filters -->
      <div class="quick-filters">
        <FilterChip
          v-for="filter in quickFilters"
          :key="filter.id"
          :label="filter.label"
          @click="handleQuickFilter(filter.id)"
        />
      </div>

      <!-- Main filters -->
      <div class="main-filters">
        <FilterAccordion title="Calories" :default-open="true">
          <FilterSection
            label=""
            :options="calorieOptions"
            v-model="caloriesFilter"
          />
        </FilterAccordion>

        <FilterAccordion title="Protein" :default-open="true">
          <FilterSection
            label=""
            :options="proteinOptions"
            v-model="proteinFilter"
          />
        </FilterAccordion>

        <FilterAccordion title="Carbs">
          <FilterSection
            label=""
            :options="carbsOptions"
            :model-value="{ min: null, max: carbsMax }"
            @update:model-value="(val) => dishesStore.setCarbsFilter(val.max)"
          />
        </FilterAccordion>

        <FilterAccordion title="Fat">
          <FilterSection
            label=""
            :options="fatOptions"
            :model-value="{ min: fatMin, max: fatMax }"
            @update:model-value="(val) => dishesStore.setFatFilter(val.min, val.max)"
          />
        </FilterAccordion>

        <FilterAccordion title="Restaurants">
          <RestaurantFilter
            :selected="selectedRestaurants"
            @toggle="handleRestaurantToggle"
          />
        </FilterAccordion>
      </div>
    </FilterDrawer>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import MapView from '../components/MapView.vue'
import ViewToggle from '../components/ViewToggle.vue'
import SearchBar from '../components/SearchBar.vue'
import FilterChip from '../components/FilterChip.vue'
import FilterSection from '../components/FilterSection.vue'
import RestaurantFilter from '../components/RestaurantFilter.vue'
import SortDropdown from '../components/SortDropdown.vue'
import DishCard from '../components/DishCard.vue'
import LoadMoreButton from '../components/LoadMoreButton.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'
import FilterDrawer from '../components/FilterDrawer.vue'
import FilterAccordion from '../components/FilterAccordion.vue'
import { useDishesStore } from '../stores/dishes'
import { useLocationsStore } from '../stores/locations'
import { useRestaurantsStore } from '../stores/restaurants'

const route = useRoute()
const router = useRouter()
const dishesStore = useDishesStore()
const locationsStore = useLocationsStore()
const restaurantsStore = useRestaurantsStore()

// Dishes store refs
const {
  dishes,
  total,
  loading,
  error,
  search,
  caloriesMin,
  caloriesMax,
  proteinMin,
  proteinMax,
  carbsMax,
  fatMin,
  fatMax,
  selectedRestaurants,
  sort,
  hasMore,
  activeFilterCount,
} = storeToRefs(dishesStore)

// Locations store refs
const { locations, userLocation } = storeToRefs(locationsStore)
const { restaurants } = storeToRefs(restaurantsStore)

// View state
const currentView = ref('list')
const isMobile = ref(window.innerWidth < 768)
const highlightedDishId = ref(null)
const highlightedRestaurantSlug = ref(null)
const showFilterDrawer = ref(false)
const mapViewRef = ref(null)

// Map state
const center = ref([-74.0060, 40.7128]) // New York City
const zoom = ref(12)
const mapLoaded = ref(false)

// Filter options
const calorieOptions = [
  { label: 'Any', min: null, max: null },
  { label: '0-300', min: 0, max: 300 },
  { label: '300-500', min: 300, max: 500 },
  { label: '500-700', min: 500, max: 700 },
  { label: '700+', min: 700, max: null },
]

const proteinOptions = [
  { label: 'Any', min: null, max: null },
  { label: '0-20g', min: 0, max: 20 },
  { label: '20-40g', min: 20, max: 40 },
  { label: '40-60g', min: 40, max: 60 },
  { label: '60g+', min: 60, max: null },
]

const carbsOptions = [
  { label: 'Any', min: null, max: null },
  { label: '0-30g', min: null, max: 30 },
  { label: '30-60g', min: null, max: 60 },
  { label: '60-100g', min: null, max: 100 },
  { label: '100g+', min: null, max: null },
]

const fatOptions = [
  { label: 'Any', min: null, max: null },
  { label: '0-15g', min: 0, max: 15 },
  { label: '15-30g', min: 15, max: 30 },
  { label: '30-50g', min: 30, max: 50 },
  { label: '50g+', min: 50, max: null },
]

// Quick filters
const quickFilters = computed(() => {
  const filters = [
    { id: 'high-protein', label: 'High Protein 40g+' },
    { id: 'under-500', label: 'Under 500 cal' },
    { id: 'best-ratio', label: 'Best Ratio' },
    { id: 'low-carb', label: 'Low Carb' },
  ]

  if (dishesStore.userLocation) {
    filters.unshift({ id: 'nearby-5mi', label: 'Nearby 5 mi' })
  }

  return filters
})

// Computed filters for two-way binding
const caloriesFilter = computed({
  get: () => ({ min: caloriesMin.value, max: caloriesMax.value }),
  set: (val) => dishesStore.setCaloriesFilter(val.min, val.max),
})

const proteinFilter = computed({
  get: () => ({ min: proteinMin.value, max: proteinMax.value }),
  set: (val) => dishesStore.setProteinFilter(val.min, val.max),
})

// Get unique restaurant slugs from filtered dishes
const matchingRestaurantSlugs = computed(() => {
  if (!dishes.value || dishes.value.length === 0) return []
  const slugs = new Set()
  dishes.value.forEach(dish => {
    if (dish.restaurant?.slug) {
      slugs.add(dish.restaurant.slug)
    }
  })
  return Array.from(slugs)
})

// Filter locations to only show restaurants with matching dishes
const matchingLocations = computed(() => {
  if (!locations.value || locations.value.length === 0) return []
  if (matchingRestaurantSlugs.value.length === 0) return []

  return locations.value.filter(location => {
    return matchingRestaurantSlugs.value.includes(location.restaurant.slug)
  })
})

// Handlers
const handleMapLoad = (map) => {
  mapLoaded.value = true
  console.log('Map loaded:', map)
  // Fetch restaurants for filter
  restaurantsStore.fetchRestaurants()
  // Fetch initial locations
  locationsStore.fetchLocations()
}

const handleViewChange = (view) => {
  console.log('View changed to:', view)
}

const handleMarkerClick = (location) => {
  console.log('Marker clicked:', location)

  // Highlight the restaurant
  highlightedRestaurantSlug.value = location.restaurant.slug
}

const handleMapDishClick = (dishId) => {
  // Navigate to dish detail page from map popup
  router.push({ name: 'dish-detail', params: { id: dishId } })
}

const handleViewAllDishes = (restaurantSlug) => {
  // Clear existing restaurant filter
  dishesStore.setRestaurants([])

  // Set filter to this restaurant only
  dishesStore.setRestaurants([restaurantSlug])

  // Switch to list view on mobile
  if (isMobile.value) {
    currentView.value = 'list'
  }

  // Highlight the restaurant
  highlightedRestaurantSlug.value = restaurantSlug
}

const handleBoundsChange = (data) => {
  console.log('Bounds changed:', data)
  locationsStore.setMapBounds(data)
  locationsStore.fetchLocations({ bbox: data.bbox })
}

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

const handleSearch = (value) => {
  dishesStore.setSearch(value)
}

const handleQuickFilter = (preset) => {
  dishesStore.applyQuickFilter(preset)
}

const handleRestaurantToggle = (slug) => {
  dishesStore.toggleRestaurant(slug)
}

const handleSort = (value) => {
  dishesStore.setSort(value)
}

const handleLoadMore = () => {
  dishesStore.loadMore()
}

const handleClearFilters = () => {
  dishesStore.clearFilters()
}

const handleRetry = () => {
  dishesStore.fetchDishes()
}

const handleDishHover = (dish) => {
  if (dish) {
    highlightedRestaurantSlug.value = dish.restaurant.slug
  } else {
    highlightedRestaurantSlug.value = null
  }
}

const handleDishClick = (dish) => {
  // Keep the logic from router navigation in DishCard
  // Just ensure highlighting works
  highlightedRestaurantSlug.value = dish.restaurant.slug
}

// Lifecycle
onMounted(() => {
  window.addEventListener('resize', handleResize)

  // Parse URL params
  const params = route.query
  if (params.search) dishesStore.search = params.search
  if (params.protein_min) dishesStore.proteinMin = Number(params.protein_min)
  if (params.calories_max) dishesStore.caloriesMax = Number(params.calories_max)

  // Sync user location
  if (locationsStore.userLocation) {
    dishesStore.setUserLocation(
      locationsStore.userLocation.lat,
      locationsStore.userLocation.lng
    )
  }

  // Fetch initial data
  dishesStore.fetchDishes()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Watch for user location changes
watch(
  () => locationsStore.userLocation,
  (newLocation) => {
    if (newLocation) {
      dishesStore.setUserLocation(newLocation.lat, newLocation.lng)
    } else {
      dishesStore.setUserLocation(null, null)
    }
  },
  { deep: true }
)

// Sync filters to URL
watch(
  [search, proteinMin, proteinMax, caloriesMin, caloriesMax, sort],
  () => {
    const query = {}
    if (search.value) query.search = search.value
    if (proteinMin.value) query.protein_min = proteinMin.value
    if (proteinMax.value) query.protein_max = proteinMax.value
    if (caloriesMin.value) query.calories_min = caloriesMin.value
    if (caloriesMax.value) query.calories_max = caloriesMax.value
    if (sort.value !== 'protein_ratio_desc') query.sort = sort.value

    router.replace({ query })
  },
  { deep: true }
)

// Resize map when switching to map view on mobile
watch(currentView, (newView) => {
  if (newView === 'map' && isMobile.value && mapViewRef.value) {
    // Show loading spinner
    mapViewRef.value.setLoading(true)

    // Wait for DOM update then resize map
    setTimeout(() => {
      const map = mapViewRef.value.getMap()
      if (map) {
        map.resize()
        // Hide loading spinner after resize
        setTimeout(() => {
          mapViewRef.value.setLoading(false)
        }, 300)
      }
    }, 100)
  }
})
</script>

<style scoped>
.search-view {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.view-controls {
  padding: 16px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: none;
}

.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.list-panel {
  width: 40%;
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-panel {
  flex: 1;
  position: relative;
}

.map-loading-overlay,
.map-empty-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(var(--color-background), 0.8);
  backdrop-filter: blur(4px);
  z-index: 10;
  pointer-events: none;
}

.loading-spinner,
.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 24px;
}

.animate-spin {
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

/* Filters section */
.filters-section {
  padding: 16px;
  background-color: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.quick-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.main-filters {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
}

/* Results header */
.results-header {
  padding: 12px 16px;
  background-color: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  gap: 12px;
}

.results-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.results-count {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.filter-button {
  display: none;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms ease;
  white-space: nowrap;
}

.filter-button:hover {
  background-color: var(--color-surface-elevated);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-button .icon {
  width: 18px;
  height: 18px;
}

.filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border-radius: 9px;
  color: white;
  font-size: 11px;
  font-weight: 700;
}

/* Dish list */
.dish-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
}

.dish-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dish-grid .highlighted {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 8px;
}

/* Utility classes */
.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
}

/* Tablet styles */
@media (min-width: 769px) and (max-width: 1024px) {
  .list-panel {
    width: 50%;
  }

  /* Larger touch targets for tablet */
  .filter-button {
    padding: 10px 14px;
    font-size: 15px;
  }

  /* Better spacing for dish grid */
  .dish-grid {
    gap: 16px;
    padding: 16px;
  }

  /* Adjust results header for tablet */
  .results-header {
    padding: 14px 16px;
  }
}

/* Mobile styles */
@media (max-width: 768px) {
  .view-controls {
    display: block;
    padding: 0;
    border: none;
    height: 0;
    overflow: visible;
  }

  .content-area {
    position: relative;
  }

  .list-panel,
  .map-panel {
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: calc(68px + env(safe-area-inset-bottom));
  }

  .list-panel {
    border-right: none;
  }

  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: flex;
  }

  .filter-button {
    display: flex;
  }

  /* Make dish list scrollable on mobile */
  .dish-list {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  /* Adjust results header for mobile */
  .results-header {
    padding: 10px 12px;
  }

  .results-count {
    font-size: 13px;
  }
}
</style>
