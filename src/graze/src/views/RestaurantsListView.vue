<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useRestaurantsStore } from '../stores/restaurants'
import RestaurantCard from '../components/RestaurantCard.vue'
import SearchBar from '../components/SearchBar.vue'

const router = useRouter()
const restaurantsStore = useRestaurantsStore()
const { restaurants, loading } = storeToRefs(restaurantsStore)

const searchQuery = ref('')

const filteredRestaurants = computed(() => {
  if (!searchQuery.value.trim()) return restaurants.value
  const q = searchQuery.value.trim().toLowerCase()
  return restaurants.value.filter(r => r.name.toLowerCase().includes(q))
})

onMounted(() => {
  restaurantsStore.fetchRestaurants()
})

function goBack() {
  router.back()
}
</script>

<template>
  <div class="restaurants-list-view">
    <div class="list-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div>
        <h1 class="page-title">Restaurants</h1>
        <p v-if="restaurants.length" class="page-subtitle">{{ filteredRestaurants.length }} of {{ restaurants.length }} restaurants</p>
      </div>
    </div>

    <div class="search-section">
      <SearchBar v-model="searchQuery" placeholder="Filter restaurants..." />
    </div>

    <div class="list-content">
      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div v-for="i in 4" :key="i" class="skeleton-card"></div>
      </div>

      <!-- Restaurant list -->
      <div v-else-if="filteredRestaurants.length" class="restaurants-list">
        <RestaurantCard
          v-for="restaurant in filteredRestaurants"
          :key="restaurant.slug"
          :restaurant="restaurant"
          full-width
        />
      </div>

      <!-- No results -->
      <div v-else class="empty-state">
        <p>No restaurants match "{{ searchQuery }}"</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.restaurants-list-view {
  height: 100%;
  overflow-y: auto;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 16px 12px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-surface-elevated);
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
  transition: background 150ms ease;
}

.back-btn:hover {
  background: var(--color-surface);
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.search-section {
  padding: 0 16px 12px;
}

.list-content {
  padding: 0 16px 24px;
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--color-text-tertiary);
  font-size: 14px;
}

.restaurants-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-card {
  height: 140px;
  border-radius: 12px;
  background: var(--color-surface);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (min-width: 1024px) {
  .restaurants-list-view {
    max-width: 1440px;
    margin: 0 auto;
    padding: 0 40px;
  }

  .back-btn {
    display: none;
  }

  .list-header {
    padding: 20px 0 12px;
  }

  .search-section {
    padding: 0 0 16px;
  }

  .list-content {
    padding: 0 0 40px;
  }

  .restaurants-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  /* Show gradient card headers on desktop */
  .restaurants-list :deep(.restaurant-card.full-width) {
    border-left-width: 1px;
    border-left-color: var(--color-border);
  }

  .restaurants-list :deep(.full-width .card-header) {
    display: flex;
  }

  .restaurants-list :deep(.full-width .card-body) {
    padding: 12px;
  }
}

@media (min-width: 1280px) {
  .restaurants-list {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1440px) {
  .restaurants-list {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
