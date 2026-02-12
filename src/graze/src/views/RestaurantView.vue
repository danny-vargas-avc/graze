<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRestaurant } from '../api/restaurants'
import { useConfigStore } from '../stores/config'
import DishCard from '../components/DishCard.vue'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()

const restaurant = ref(null)
const loading = ref(true)
const error = ref(null)
const activeCategory = ref(null)

const brandColor = computed(() => {
  if (!restaurant.value) return '#06C167'
  return configStore.getRestaurantColor(restaurant.value.slug) || '#06C167'
})

const categories = computed(() => {
  if (!restaurant.value?.dishes) return []
  const cats = [...new Set(restaurant.value.dishes.map(d => d.category).filter(Boolean))]
  return cats.sort()
})

const filteredDishes = computed(() => {
  if (!restaurant.value?.dishes) return []
  if (!activeCategory.value) return restaurant.value.dishes
  return restaurant.value.dishes.filter(d => d.category === activeCategory.value)
})

onMounted(async () => {
  try {
    restaurant.value = await getRestaurant(route.params.slug)
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.back()
}

function setCategory(cat) {
  activeCategory.value = activeCategory.value === cat ? null : cat
}
</script>

<template>
  <div class="restaurant-view">
    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <p>{{ error.message }}</p>
      <button @click="goBack" class="back-link">Go back</button>
    </div>

    <!-- Content -->
    <template v-else-if="restaurant">
      <!-- Brand color banner -->
      <div class="banner" :style="{ background: `linear-gradient(135deg, ${brandColor}, ${brandColor}dd)` }">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div class="banner-content">
          <h1 class="restaurant-title">{{ restaurant.name }}</h1>
          <div class="banner-meta">
            <span class="meta-item">
              <svg class="meta-icon" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1.5a.5.5 0 01.5.5v3.793l2.854 2.853a.5.5 0 01-.708.708l-3-3A.5.5 0 017.5 6V2a.5.5 0 01.5-.5z" />
                <path d="M8 15A7 7 0 108 1a7 7 0 000 14zm0-1A6 6 0 108 2a6 6 0 000 12z" />
              </svg>
              {{ restaurant.item_count }} items
            </span>
            <a
              v-if="restaurant.website_url"
              :href="restaurant.website_url"
              target="_blank"
              rel="noopener noreferrer"
              class="meta-link"
            >
              <svg class="meta-icon" viewBox="0 0 16 16" fill="currentColor">
                <path d="M6.354 5.5H4a3 3 0 000 6h3a3 3 0 002.83-4H9.874a2 2 0 01-1.874 3H5a2 2 0 110-4h1.354z" />
                <path d="M9.646 10.5H12a3 3 0 000-6H9a3 3 0 00-2.83 4h.996a2 2 0 011.874-3H11a2 2 0 110 4H9.646z" />
              </svg>
              Website
            </a>
          </div>
        </div>
      </div>

      <!-- Category tabs -->
      <div v-if="categories.length > 1" class="category-tabs hide-scrollbar">
        <button
          class="category-tab"
          :class="{ active: !activeCategory }"
          @click="activeCategory = null"
        >
          All
        </button>
        <button
          v-for="cat in categories"
          :key="cat"
          class="category-tab"
          :class="{ active: activeCategory === cat }"
          @click="setCategory(cat)"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Dishes grid -->
      <div class="dishes-area">
        <p class="results-count">{{ filteredDishes.length }} items</p>
        <div class="dishes-grid">
          <DishCard
            v-for="dish in filteredDishes"
            :key="dish.id"
            :dish="{ ...dish, restaurant }"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.restaurant-view {
  min-height: 100%;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-error);
}

.back-link {
  margin-top: 12px;
  color: var(--color-primary);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.banner {
  padding: 20px;
  padding-top: 16px;
  position: relative;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  padding: 0;
  transition: background-color 150ms ease;
}

.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

.banner-content {
  color: #ffffff;
}

.restaurant-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.banner-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  opacity: 0.9;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 500;
}

.meta-icon {
  width: 14px;
  height: 14px;
}

.meta-link {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  text-decoration: none;
}

.meta-link:hover {
  text-decoration: underline;
}

.category-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-surface-elevated);
}

.category-tab {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 150ms ease;
  text-transform: capitalize;
}

.category-tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.category-tab.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: #ffffff;
}

.dishes-area {
  padding: 16px;
}

.results-count {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: 12px;
}

.dishes-grid {
  display: grid;
  gap: 12px;
}

@media (min-width: 640px) {
  .dishes-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .dishes-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
