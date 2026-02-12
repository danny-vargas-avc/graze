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
const bowlDishes = ref([])
const saladDishes = ref([])
const burgerDishes = ref([])
const loading = ref(true)

async function fetchCarousels(category = null) {
  loading.value = true
  try {
    const base = category ? { category } : {}

    // Core macro-based carousels (always fetched)
    const corePromises = [
      getDishes({ ...base, sort: 'protein_desc', limit: 10 }),
      getDishes({ ...base, calories_max: 500, sort: 'protein_ratio_desc', limit: 10 }),
      getDishes({ ...base, sort: 'protein_ratio_desc', limit: 10 }),
    ]

    // Category carousels only when no filter is active
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

</style>
