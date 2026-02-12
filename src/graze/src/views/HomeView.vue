<script setup>
import { ref, onMounted } from 'vue'
import { useRestaurantsStore } from '../stores/restaurants'
import { useDishesStore } from '../stores/dishes'
import { storeToRefs } from 'pinia'
import { getDishes } from '../api/dishes'
import CategoryPills from '../components/CategoryPills.vue'
import CarouselSection from '../components/CarouselSection.vue'
import RestaurantCard from '../components/RestaurantCard.vue'
import DishCardCompact from '../components/DishCardCompact.vue'
import SearchBar from '../components/SearchBar.vue'

const restaurantsStore = useRestaurantsStore()
const dishesStore = useDishesStore()
const { restaurants } = storeToRefs(restaurantsStore)

const activeCategory = ref(null)
const highProteinDishes = ref([])
const lowCalDishes = ref([])
const bestRatioDishes = ref([])
const loading = ref(true)

async function fetchCarousels(category = null) {
  loading.value = true
  try {
    const base = category ? { category } : {}
    const [highProtein, lowCal, bestRatio] = await Promise.all([
      getDishes({ ...base, sort: 'protein_desc', limit: 10 }),
      getDishes({ ...base, calories_max: 500, sort: 'protein_ratio_desc', limit: 10 }),
      getDishes({ ...base, sort: 'protein_ratio_desc', limit: 10 }),
    ])
    highProteinDishes.value = highProtein.data
    lowCalDishes.value = lowCal.data
    bestRatioDishes.value = bestRatio.data
  } catch (e) {
    console.error('Failed to load carousel data:', e)
  } finally {
    loading.value = false
  }
}

function handleSearch(value) {
  dishesStore.setSearch(value)
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
      <SearchBar :model-value="dishesStore.search" @update:model-value="handleSearch" placeholder="Search dishes or restaurants..." />
    </div>

    <!-- Category pills -->
    <CategoryPills :active="activeCategory" @change="handleCategoryChange" />

    <!-- Scrollable content -->
    <div class="home-content">
      <!-- Restaurants carousel -->
      <CarouselSection title="Restaurants" see-all-to="/map">
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

      <!-- All Restaurants grid -->
      <section class="all-restaurants">
        <h2 class="section-title">All Restaurants</h2>
        <div class="restaurants-grid">
          <RestaurantCard
            v-for="restaurant in restaurants"
            :key="restaurant.slug"
            :restaurant="restaurant"
            full-width
          />
        </div>
      </section>
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

.all-restaurants {
  padding: 0 16px;
  margin-top: 8px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.restaurants-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 769px) {
  .restaurants-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (min-width: 1024px) {
  .restaurants-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
