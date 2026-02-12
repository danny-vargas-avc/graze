<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDish } from '../api/dishes'
import { useConfigStore } from '../stores/config'
import { useFavoritesStore } from '../stores/favorites'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorState from '../components/ErrorState.vue'
import LazyImage from '../components/LazyImage.vue'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()
const favoritesStore = useFavoritesStore()

const dish = ref(null)
const loading = ref(true)
const error = ref(null)

const brandColor = computed(() => {
  if (!dish.value) return '#06C167'
  return configStore.getRestaurantColor(dish.value.restaurant?.slug) || '#06C167'
})

const isFavorite = computed(() => {
  if (!dish.value) return false
  return favoritesStore.isFavorite(dish.value.id)
})

onMounted(async () => {
  try {
    dish.value = await getDish(route.params.id)
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.back()
}

function toggleFavorite() {
  if (dish.value) {
    favoritesStore.toggle(dish.value.id)
  }
}

function retry() {
  loading.value = true
  error.value = null
  getDish(route.params.id)
    .then(data => { dish.value = data })
    .catch(err => { error.value = err })
    .finally(() => { loading.value = false })
}
</script>

<template>
  <div class="detail-view">
    <!-- Loading -->
    <LoadingSpinner v-if="loading" center size="lg" text="Loading dish details..." />

    <!-- Error -->
    <ErrorState v-else-if="error" :error="error" @retry="retry" />

    <!-- Content -->
    <div v-else-if="dish" class="detail-content">
      <!-- Top bar -->
      <div class="top-bar">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button class="fav-btn" :class="{ active: isFavorite }" @click="toggleFavorite">
          <svg v-if="!isFavorite" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
          </svg>
        </button>
      </div>

      <!-- Food photo banner -->
      <div v-if="dish.image_url" class="dish-photo-banner">
        <img :src="dish.image_url" :alt="dish.name" class="dish-photo" />
      </div>

      <!-- Header -->
      <div class="dish-header">
        <div class="header-row">
          <div v-if="dish.restaurant.logo_url" class="restaurant-logo">
            <LazyImage
              :src="dish.restaurant.logo_url"
              :alt="dish.restaurant.name"
            />
          </div>
          <div class="brand-dot" v-else :style="{ backgroundColor: brandColor }"></div>
          <div>
            <p class="restaurant-name">{{ dish.restaurant.name }}</p>
            <h1 class="dish-title">{{ dish.name }}</h1>
            <p v-if="dish.serving_size" class="serving-size">
              Serving: {{ dish.serving_size }}
            </p>
          </div>
        </div>
      </div>

      <!-- Core macros -->
      <div class="section">
        <h2 class="section-title">Macros</h2>
        <div class="macro-grid">
          <div class="macro-card">
            <svg class="macro-card-icon" viewBox="0 0 20 20" fill="var(--color-text-secondary)">
              <path d="M12.186 8.672L18.743.947l-2.048 5.732 3.421 2.068-6.326 7.304 1.898-5.596z" />
            </svg>
            <p class="macro-value">{{ dish.calories }}</p>
            <p class="macro-label">Calories</p>
          </div>
          <div class="macro-card protein-card">
            <svg class="macro-card-icon" viewBox="0 0 20 20" fill="var(--color-primary)">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v2.5h-2.5a.75.75 0 000 1.5h2.5v2.5a.75.75 0 001.5 0v-2.5h2.5a.75.75 0 000-1.5h-2.5v-2.5z" clip-rule="evenodd" />
            </svg>
            <p class="macro-value text-success">{{ dish.protein }}g</p>
            <p class="macro-label">Protein</p>
          </div>
          <div class="macro-card">
            <svg class="macro-card-icon" viewBox="0 0 20 20" fill="var(--color-warning)">
              <path d="M10 2a.75.75 0 01.75.75v.258a33.186 33.186 0 016.668.83.75.75 0 01-.336 1.461 31.28 31.28 0 00-1.103-.232l1.702 7.545a.75.75 0 01-.387.832A4.981 4.981 0 0114 14c-.09 0-.18-.003-.269-.008l-.15-.007A4.98 4.98 0 0110.75 12.6V16.5h2.5a.75.75 0 010 1.5h-6.5a.75.75 0 010-1.5h2.5v-3.9a4.98 4.98 0 01-3.081 1.385l-.15.007A5.001 5.001 0 012.354 12.7a.75.75 0 01-.388-.832l1.703-7.545a31.28 31.28 0 00-1.103.232.75.75 0 11-.336-1.462 33.186 33.186 0 016.668-.829V2.75A.75.75 0 0110 2z" />
            </svg>
            <p class="macro-value">{{ dish.carbs }}g</p>
            <p class="macro-label">Carbs</p>
          </div>
          <div class="macro-card">
            <svg class="macro-card-icon" viewBox="0 0 20 20" fill="var(--color-text-tertiary)">
              <path d="M10 2c.076 0 .152.01.225.03l.002.001 5.253 1.5A.75.75 0 0116 4.28v6.97a4.75 4.75 0 01-2.734 4.306l-2.988 1.422a.75.75 0 01-.647 0l-2.988-1.422A4.75 4.75 0 014 11.25V4.28a.75.75 0 01.52-.749l5.253-1.5.002-.001A.753.753 0 0110 2z" />
            </svg>
            <p class="macro-value">{{ dish.fat }}g</p>
            <p class="macro-label">Fat</p>
          </div>
        </div>
      </div>

      <!-- Protein density -->
      <div v-if="dish.protein_per_100cal" class="section">
        <div class="density-bar">
          <div class="density-info">
            <span class="density-label">Protein Density</span>
            <span class="density-value text-success">{{ dish.protein_per_100cal }}g per 100 cal</span>
          </div>
          <span class="density-badge" :class="dish.density_label">{{ dish.density_label }}</span>
        </div>
      </div>

      <!-- Extended nutrition -->
      <div v-if="dish.fiber || dish.sodium || dish.sugar || dish.saturated_fat" class="section">
        <h2 class="section-title">Additional Nutrition</h2>
        <div class="nutrition-list">
          <div v-if="dish.fiber !== null" class="nutrition-row">
            <span class="nutrition-name">Fiber</span>
            <span class="nutrition-val">{{ dish.fiber }}g</span>
          </div>
          <div v-if="dish.sodium !== null" class="nutrition-row">
            <span class="nutrition-name">Sodium</span>
            <span class="nutrition-val">{{ dish.sodium }}mg</span>
          </div>
          <div v-if="dish.sugar !== null" class="nutrition-row">
            <span class="nutrition-name">Sugar</span>
            <span class="nutrition-val">{{ dish.sugar }}g</span>
          </div>
          <div v-if="dish.saturated_fat !== null" class="nutrition-row">
            <span class="nutrition-name">Saturated Fat</span>
            <span class="nutrition-val">{{ dish.saturated_fat }}g</span>
          </div>
        </div>
      </div>

      <!-- Dietary info -->
      <div v-if="dish.is_vegetarian || dish.is_vegan || dish.is_gluten_free" class="section">
        <h2 class="section-title">Dietary Information</h2>
        <div class="dietary-tags">
          <span v-if="dish.is_vegetarian" class="dietary-tag">
            <svg class="tag-icon" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 15A7 7 0 108 1a7 7 0 000 14zm3.844-8.791a.75.75 0 00-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 10-1.114 1.004l2.25 2.5a.75.75 0 001.15-.043l4.25-5.5z" />
            </svg>
            Vegetarian
          </span>
          <span v-if="dish.is_vegan" class="dietary-tag">
            <svg class="tag-icon" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 15A7 7 0 108 1a7 7 0 000 14zm3.844-8.791a.75.75 0 00-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 10-1.114 1.004l2.25 2.5a.75.75 0 001.15-.043l4.25-5.5z" />
            </svg>
            Vegan
          </span>
          <span v-if="dish.is_gluten_free" class="dietary-tag">
            <svg class="tag-icon" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 15A7 7 0 108 1a7 7 0 000 14zm3.844-8.791a.75.75 0 00-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 10-1.114 1.004l2.25 2.5a.75.75 0 001.15-.043l4.25-5.5z" />
            </svg>
            Gluten-Free
          </span>
        </div>
      </div>

      <!-- Source -->
      <div class="section source-section">
        <span v-if="dish.last_verified" class="source-text">
          Last verified: {{ new Date(dish.last_verified).toLocaleDateString() }}
        </span>
        <a
          v-if="dish.source_url"
          :href="dish.source_url"
          target="_blank"
          rel="noopener noreferrer"
          class="source-link"
        >
          <svg class="source-icon" viewBox="0 0 16 16" fill="currentColor">
            <path d="M6.354 5.5H4a3 3 0 000 6h3a3 3 0 002.83-4H9.874a2 2 0 01-1.874 3H5a2 2 0 110-4h1.354z" />
            <path d="M9.646 10.5H12a3 3 0 000-6H9a3 3 0 00-2.83 4h.996a2 2 0 011.874-3H11a2 2 0 110 4H9.646z" />
          </svg>
          View source
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-view {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 16px 24px;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface-elevated);
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 150ms ease;
}

.back-btn:hover {
  border-color: var(--color-border-hover);
  background-color: var(--color-surface);
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.fav-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface-elevated);
  color: var(--color-text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 150ms ease;
}

.fav-btn:hover {
  color: var(--color-error);
  border-color: var(--color-error);
}

.fav-btn.active {
  color: var(--color-error);
  border-color: var(--color-error);
  background-color: #fef2f2;
}

.fav-btn svg {
  width: 20px;
  height: 20px;
}

.detail-content {
  background-color: var(--color-surface-elevated);
  border-radius: 16px;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.dish-photo-banner {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background-color: var(--color-surface);
}

.dish-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dish-header {
  padding: 20px;
  border-bottom: 1px solid var(--color-border);
}

.header-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.restaurant-logo {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
}

.brand-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}

.restaurant-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 2px;
}

.dish-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.serving-size {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.section {
  padding: 20px;
  border-bottom: 1px solid var(--color-border);
}

.section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.macro-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

@media (max-width: 480px) {
  .macro-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.macro-card {
  background-color: var(--color-surface);
  border-radius: 12px;
  padding: 14px 12px;
  text-align: center;
}

.macro-card-icon {
  width: 18px;
  height: 18px;
  margin: 0 auto 6px;
}

.macro-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.macro-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.density-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.density-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.density-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.density-value {
  font-size: 13px;
  font-weight: 500;
}

.density-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.density-badge.excellent {
  background-color: #dcfce7;
  color: #166534;
}

.density-badge.good {
  background-color: #fef9c3;
  color: #854d0e;
}

.density-badge.average {
  background-color: #ffedd5;
  color: #9a3412;
}

.density-badge.low {
  background-color: var(--color-surface);
  color: var(--color-text-tertiary);
}

.nutrition-list {
  display: flex;
  flex-direction: column;
}

.nutrition-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.nutrition-row:last-child {
  border-bottom: none;
}

.nutrition-name {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.nutrition-val {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.dietary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dietary-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 20px;
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 500;
}

.tag-icon {
  width: 14px;
  height: 14px;
}

.source-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.source-text {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.source-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-primary);
  text-decoration: none;
}

.source-link:hover {
  text-decoration: underline;
}

.source-icon {
  width: 14px;
  height: 14px;
}
</style>
