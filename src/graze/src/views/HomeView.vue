<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRestaurantsStore } from '../stores/restaurants'
import { storeToRefs } from 'pinia'
import { getDishes } from '../api/dishes'
import CategoryPills from '../components/CategoryPills.vue'
import CarouselSection from '../components/CarouselSection.vue'
import RestaurantCard from '../components/RestaurantCard.vue'
import DishCardCompact from '../components/DishCardCompact.vue'
import SearchBar from '../components/SearchBar.vue'

const restaurantsStore = useRestaurantsStore()
const { restaurants } = storeToRefs(restaurantsStore)

const activeCategory = ref(null)
const highProteinDishes = ref([])
const lowCalDishes = ref([])
const bestRatioDishes = ref([])
const bowlDishes = ref([])
const saladDishes = ref([])
const burgerDishes = ref([])
const loading = ref(true)

const searchQuery = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
let searchController = null

const isSearching = computed(() => searchQuery.value.trim().length > 0)

async function fetchCarousels(category = null) {
  loading.value = true
  try {
    const base = category ? { category } : {}

    const corePromises = [
      getDishes({ ...base, sort: 'protein_desc', limit: 10 }),
      getDishes({ ...base, calories_max: 500, sort: 'protein_ratio_desc', limit: 10 }),
      getDishes({ ...base, sort: 'protein_ratio_desc', limit: 10 }),
    ]

    const categoryPromises = category ? [] : [
      getDishes({ category: 'bowl', sort: 'protein_desc', limit: 10 }),
      getDishes({ category: 'salad', sort: 'protein_desc', limit: 10 }),
      getDishes({ category: 'burger', sort: 'protein_desc', limit: 10 }),
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
  fetchCarousels(category)
}

onMounted(() => {
  restaurantsStore.fetchRestaurants()
  fetchCarousels()
})
</script>

<template>
  <div class="home-view">
    <!-- Search bar -->
    <div class="search-section">
      <SearchBar :model-value="searchQuery" @update:model-value="handleSearch" placeholder="Search dishes or restaurants..." />
    </div>

    <!-- Category pills (hidden during search) -->
    <CategoryPills v-if="!isSearching" :active="activeCategory" @change="handleCategoryChange" />

    <!-- Search results -->
    <div v-if="isSearching" class="home-content">
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
    </div>

    <!-- Normal carousel content -->
    <div v-else class="home-content">
      <!-- Restaurants carousel -->
      <CarouselSection title="Restaurants" see-all-to="/restaurants">
        <div class="carousel-scroll hide-scrollbar">
          <RestaurantCard
            v-for="restaurant in restaurants"
            :key="restaurant.slug"
            :restaurant="restaurant"
          />
        </div>
      </CarouselSection>

      <!-- Highest Protein carousel -->
      <CarouselSection title="Highest Protein" icon="protein">
        <div class="carousel-scroll hide-scrollbar">
          <template v-if="loading">
            <div v-for="i in 4" :key="i" class="skeleton-card"></div>
          </template>
          <DishCardCompact
            v-else
            v-for="dish in highProteinDishes"
            :key="dish.id"
            :dish="dish"
          />
        </div>
      </CarouselSection>

      <!-- Under 500 Cal carousel -->
      <CarouselSection title="Under 500 Calories" icon="calories">
        <div class="carousel-scroll hide-scrollbar">
          <template v-if="loading">
            <div v-for="i in 4" :key="i" class="skeleton-card"></div>
          </template>
          <DishCardCompact
            v-else
            v-for="dish in lowCalDishes"
            :key="dish.id"
            :dish="dish"
          />
        </div>
      </CarouselSection>

      <!-- Best Ratio carousel -->
      <CarouselSection title="Best Protein Ratio" icon="ratio">
        <div class="carousel-scroll hide-scrollbar">
          <template v-if="loading">
            <div v-for="i in 4" :key="i" class="skeleton-card"></div>
          </template>
          <DishCardCompact
            v-else
            v-for="dish in bestRatioDishes"
            :key="dish.id"
            :dish="dish"
          />
        </div>
      </CarouselSection>

      <!-- Category carousels (shown when no category filter is active) -->
      <CarouselSection v-if="bowlDishes.length" title="Top Bowls" icon="bowl">
        <div class="carousel-scroll hide-scrollbar">
          <DishCardCompact
            v-for="dish in bowlDishes"
            :key="dish.id"
            :dish="dish"
          />
        </div>
      </CarouselSection>

      <CarouselSection v-if="saladDishes.length" title="Top Salads" icon="salad">
        <div class="carousel-scroll hide-scrollbar">
          <DishCardCompact
            v-for="dish in saladDishes"
            :key="dish.id"
            :dish="dish"
          />
        </div>
      </CarouselSection>

      <CarouselSection v-if="burgerDishes.length" title="Top Burgers" icon="burger">
        <div class="carousel-scroll hide-scrollbar">
          <DishCardCompact
            v-for="dish in burgerDishes"
            :key="dish.id"
            :dish="dish"
          />
        </div>
      </CarouselSection>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.search-section {
  padding: 12px 16px 0;
  flex-shrink: 0;
}

.home-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 24px;
}

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

@media (min-width: 1024px) {
  .search-results-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
