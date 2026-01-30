<script setup>
import { onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useDishesStore } from '../stores/dishes'
import { useLocationsStore } from '../stores/locations'

import SearchBar from '../components/SearchBar.vue'
import FilterChip from '../components/FilterChip.vue'
import FilterSection from '../components/FilterSection.vue'
import RestaurantFilter from '../components/RestaurantFilter.vue'
import SortDropdown from '../components/SortDropdown.vue'
import DishCard from '../components/DishCard.vue'
import LoadMoreButton from '../components/LoadMoreButton.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'

const route = useRoute()
const router = useRouter()
const dishesStore = useDishesStore()
const locationsStore = useLocationsStore()

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

// Quick filter presets
const quickFilters = computed(() => {
  const filters = [
    { id: 'high-protein', label: 'High Protein 40g+' },
    { id: 'under-500', label: 'Under 500 cal' },
    { id: 'best-ratio', label: 'Best Ratio' },
    { id: 'low-carb', label: 'Low Carb' },
  ]

  // Add "Nearby" filter only if user location is available
  if (dishesStore.userLocation) {
    filters.unshift({ id: 'nearby-5mi', label: 'Nearby 5 mi' })
  }

  return filters
})

// Computed values for two-way binding
const caloriesFilter = computed({
  get: () => ({ min: caloriesMin.value, max: caloriesMax.value }),
  set: (val) => dishesStore.setCaloriesFilter(val.min, val.max),
})

const proteinFilter = computed({
  get: () => ({ min: proteinMin.value, max: proteinMax.value }),
  set: (val) => dishesStore.setProteinFilter(val.min, val.max),
})

// Show more filters
const showMoreFilters = computed(() => {
  return carbsMax.value || fatMin.value || fatMax.value
})

// Load initial data
onMounted(() => {
  // Parse URL params
  const params = route.query
  if (params.search) dishesStore.search = params.search
  if (params.protein_min) dishesStore.proteinMin = Number(params.protein_min)
  if (params.calories_max) dishesStore.caloriesMax = Number(params.calories_max)

  // Sync user location from locations store
  if (locationsStore.userLocation) {
    dishesStore.setUserLocation(
      locationsStore.userLocation.lat,
      locationsStore.userLocation.lng
    )
  }

  dishesStore.fetchDishes()
})

// Watch for changes to user location in locations store
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

function handleSearch(value) {
  dishesStore.setSearch(value)
}

function handleQuickFilter(preset) {
  dishesStore.applyQuickFilter(preset)
}

function handleRestaurantToggle(slug) {
  dishesStore.toggleRestaurant(slug)
}

function handleSort(value) {
  dishesStore.setSort(value)
}

function handleLoadMore() {
  dishesStore.loadMore()
}

function handleClearFilters() {
  dishesStore.clearFilters()
}

function handleRetry() {
  dishesStore.fetchDishes()
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <!-- Search -->
    <SearchBar :model-value="search" @update:model-value="handleSearch" />

    <!-- Quick filters -->
    <div class="flex flex-wrap gap-2 mt-4">
      <FilterChip
        v-for="filter in quickFilters"
        :key="filter.id"
        :label="filter.label"
        @click="handleQuickFilter(filter.id)"
      />
    </div>

    <!-- Main filters -->
    <div class="mt-6 space-y-4">
      <FilterSection
        label="Calories"
        :options="calorieOptions"
        v-model="caloriesFilter"
      />

      <FilterSection
        label="Protein"
        :options="proteinOptions"
        v-model="proteinFilter"
      />

      <!-- More filters (collapsible) -->
      <details class="mt-4">
        <summary class="cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-800">
          More filters (Carbs, Fat)
        </summary>
        <div class="mt-4 space-y-4 pl-4 border-l-2 border-gray-200">
          <FilterSection
            label="Carbs"
            :options="carbsOptions"
            :model-value="{ min: null, max: carbsMax }"
            @update:model-value="(val) => dishesStore.setCarbsFilter(val.max)"
          />
          <FilterSection
            label="Fat"
            :options="fatOptions"
            :model-value="{ min: fatMin, max: fatMax }"
            @update:model-value="(val) => dishesStore.setFatFilter(val.min, val.max)"
          />
        </div>
      </details>

      <!-- Restaurant filter -->
      <RestaurantFilter
        :selected="selectedRestaurants"
        @toggle="handleRestaurantToggle"
      />
    </div>

    <!-- Results header -->
    <div class="flex items-center justify-between mt-8 mb-4">
      <p class="text-sm text-gray-600">
        <span v-if="loading && dishes.length === 0">Loading...</span>
        <span v-else>Showing {{ dishes.length }} of {{ total }} results</span>
      </p>
      <SortDropdown
        :model-value="sort"
        :show-distance="!!dishesStore.userLocation"
        @update:model-value="handleSort"
      />
    </div>

    <!-- Error state -->
    <ErrorState v-if="error && dishes.length === 0" :error="error" @retry="handleRetry" />

    <!-- Empty state -->
    <EmptyState
      v-else-if="!loading && dishes.length === 0"
      title="No exact matches for your filters"
      message="Try adjusting your filters or clear them to see all results."
      :show-clear-filters="activeFilterCount > 0"
      @clear="handleClearFilters"
    />

    <!-- Results grid -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <DishCard v-for="dish in dishes" :key="dish.id" :dish="dish" />
    </div>

    <!-- Load more -->
    <LoadMoreButton
      :loading="loading"
      :has-more="hasMore"
      :shown="dishes.length"
      :total="total"
      @click="handleLoadMore"
    />
  </div>
</template>
