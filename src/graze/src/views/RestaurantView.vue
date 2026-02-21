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
      <!-- Banner with logo -->
      <div class="banner" :style="{ background: `linear-gradient(135deg, ${brandColor}, ${brandColor}cc)` }">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <!-- Logo displayed white on gradient -->
        <div class="banner-content">
          <img
            v-if="restaurant.logo_url"
            :src="restaurant.logo_url"
            :alt="restaurant.name"
            class="banner-logo"
          />
          <h1 class="restaurant-title">{{ restaurant.name }}</h1>
          <div class="banner-meta">
            <span class="meta-item">{{ restaurant.item_count }} items</span>
            <a
              v-if="restaurant.website_url"
              :href="restaurant.website_url"
              target="_blank"
              rel="noopener noreferrer"
              class="meta-link"
            >
              Website
              <svg class="meta-icon" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M4.22 11.78a.75.75 0 010-1.06L9.44 5.5H5.75a.75.75 0 010-1.5h5.5a.75.75 0 01.75.75v5.5a.75.75 0 01-1.5 0V6.56l-5.22 5.22a.75.75 0 01-1.06 0z" clip-rule="evenodd" />
              </svg>
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
          <!-- BYO Calculator card -->
          <RouterLink
            v-if="restaurant.has_byo && !activeCategory"
            :to="{ name: 'byo-calculator', params: { slug: restaurant.slug } }"
            class="dish-card byo-card"
          >
            <div class="brand-accent" :style="{ backgroundColor: brandColor }"></div>
            <div class="card-content">
              <div class="byo-icon-box" :style="{ backgroundColor: brandColor }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25v-.008zm2.498-6.75h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007v-.008zm2.504-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008v-.008zm2.498-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008v-.008zM8.25 6h7.5v2.25h-7.5V6zM12 2.25c-1.892 0-3.758.11-5.593.322C5.307 2.7 4.5 3.65 4.5 4.757V19.5a2.25 2.25 0 002.25 2.25h10.5a2.25 2.25 0 002.25-2.25V4.757c0-1.108-.806-2.057-1.907-2.185A48.507 48.507 0 0012 2.25z" />
                </svg>
              </div>
              <div class="card-text">
                <div class="restaurant-row">
                  <p class="restaurant-name">{{ restaurant.name }}</p>
                </div>
                <h3 class="dish-name">Build Your Own Bowl</h3>
                <p class="byo-sub">Calculate nutrition for a custom meal</p>
              </div>
              <svg class="byo-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
              </svg>
            </div>
          </RouterLink>
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
  overflow: hidden;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  padding: 0;
  transition: background 150ms ease, transform 150ms ease;
  position: relative;
  z-index: 2;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.45);
}

.back-btn:active {
  transform: scale(0.9);
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.banner-content {
  color: #ffffff;
  position: relative;
  z-index: 2;
}

.banner-logo {
  max-height: 48px;
  max-width: 200px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  padding: 6px 12px;
  margin-bottom: 14px;
}

.restaurant-title {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.banner-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  opacity: 0.9;
}

.meta-item {
  font-size: 14px;
  font-weight: 500;
}

.meta-icon {
  width: 13px;
  height: 13px;
}

.meta-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  text-decoration: none;
}

.meta-link:hover {
  text-decoration: underline;
}

/* ---- BYO Card (in grid) ---- */
.byo-card {
  display: flex;
  background-color: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  overflow: hidden;
  text-decoration: none;
  transition: all 200ms ease;
}

.byo-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.byo-card .brand-accent {
  width: 4px;
  flex-shrink: 0;
}

.byo-card .card-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  flex: 1;
  min-width: 0;
}

.byo-icon-box {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.byo-icon-box svg {
  width: 22px;
  height: 22px;
}

.byo-card .card-text {
  flex: 1;
  min-width: 0;
}

.byo-card .restaurant-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.byo-card .restaurant-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.byo-card .dish-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.byo-sub {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.byo-arrow {
  width: 20px;
  height: 20px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  align-self: center;
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
