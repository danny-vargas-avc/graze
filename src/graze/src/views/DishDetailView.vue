<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDish } from '../api/dishes'
import { useConfigStore } from '../stores/config'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorState from '../components/ErrorState.vue'
import LazyImage from '../components/LazyImage.vue'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()

const dish = ref(null)
const loading = ref(true)
const error = ref(null)

const brandColor = computed(() => {
  if (!dish.value) return '#06C167'
  return configStore.getRestaurantColor(dish.value.restaurant?.slug) || '#06C167'
})

const restaurantLogoUrl = computed(() => {
  if (!dish.value) return null
  return configStore.getRestaurantIcon(dish.value.restaurant?.slug) || dish.value.restaurant?.logo_url
})

const hasExtendedNutrition = computed(() => {
  if (!dish.value) return false
  return dish.value.fiber !== null || dish.value.sodium !== null || dish.value.sugar !== null || dish.value.saturated_fat !== null
})

const hasDietaryInfo = computed(() => {
  if (!dish.value) return false
  return dish.value.is_vegetarian || dish.value.is_vegan || dish.value.is_gluten_free
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
    <template v-else-if="dish">
      <!-- Hero area -->
      <div class="hero" :class="{ 'hero-no-image': !dish.image_url }">
        <!-- Floating nav buttons -->
        <div class="floating-nav">
          <button class="nav-btn back-btn" @click="goBack" aria-label="Go back">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        <!-- Photo -->
        <img v-if="dish.image_url" :src="dish.image_url" :alt="dish.name" class="hero-img" />
        <div v-else class="hero-placeholder" :style="{ background: `linear-gradient(135deg, ${brandColor}18, ${brandColor}08)` }">
          <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" :stroke="brandColor" stroke-width="1.2" opacity="0.4">
            <path stroke-linecap="round" d="M3 12h18" />
            <path stroke-linecap="round" d="M5 12c0 3.866 3.134 7 7 7s7-3.134 7-7" />
            <path stroke-linecap="round" d="M9 12V8" />
            <path stroke-linecap="round" d="M12 12V6" />
            <path stroke-linecap="round" d="M15 12V8" />
          </svg>
        </div>
      </div>

      <!-- Main content -->
      <div class="content">
        <!-- Header -->
        <div class="dish-header">
          <RouterLink
            :to="{ name: 'restaurant-detail', params: { slug: dish.restaurant.slug } }"
            class="restaurant-link"
          >
            <div v-if="restaurantLogoUrl" class="restaurant-logo" :class="{ 'has-icon': configStore.getRestaurantIcon(dish.restaurant.slug) }">
              <img :src="restaurantLogoUrl" :alt="dish.restaurant.name" />
            </div>
            <div v-else class="restaurant-dot" :style="{ backgroundColor: brandColor }"></div>
            <span class="restaurant-name">{{ dish.restaurant.name }}</span>
            <svg class="chevron" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
            </svg>
          </RouterLink>
          <h1 class="dish-name">{{ dish.name }}</h1>
          <p v-if="dish.serving_size" class="serving-size">{{ dish.serving_size }} serving</p>
        </div>

        <!-- Calorie hero -->
        <div class="calorie-hero">
          <span class="cal-number">{{ dish.calories }}</span>
          <span class="cal-unit">cal</span>
        </div>

        <!-- Macro rings -->
        <div class="macro-row">
          <div class="macro-item">
            <div class="macro-ring" :style="{ '--ring-color': 'var(--color-primary)' }">
              <span class="macro-val">{{ dish.protein }}g</span>
            </div>
            <span class="macro-label">Protein</span>
          </div>
          <div class="macro-item">
            <div class="macro-ring" :style="{ '--ring-color': 'var(--color-warning)' }">
              <span class="macro-val">{{ dish.carbs }}g</span>
            </div>
            <span class="macro-label">Carbs</span>
          </div>
          <div class="macro-item">
            <div class="macro-ring" :style="{ '--ring-color': 'var(--color-text-tertiary)' }">
              <span class="macro-val">{{ dish.fat }}g</span>
            </div>
            <span class="macro-label">Fat</span>
          </div>
        </div>

        <!-- Protein density -->
        <div v-if="dish.protein_per_100cal" class="density-section">
          <div class="density-row">
            <div class="density-left">
              <span class="density-title">Protein Density</span>
              <span class="density-stat">{{ dish.protein_per_100cal }}g per 100 cal</span>
            </div>
            <span class="density-badge" :class="dish.density_label">{{ dish.density_label }}</span>
          </div>
        </div>

        <!-- Dietary tags -->
        <div v-if="hasDietaryInfo" class="dietary-section">
          <span v-if="dish.is_vegetarian" class="diet-pill">
            <svg viewBox="0 0 16 16" fill="currentColor" class="pill-icon"><path d="M8 15A7 7 0 108 1a7 7 0 000 14zm3.844-8.791a.75.75 0 00-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 10-1.114 1.004l2.25 2.5a.75.75 0 001.15-.043l4.25-5.5z" /></svg>
            Vegetarian
          </span>
          <span v-if="dish.is_vegan" class="diet-pill">
            <svg viewBox="0 0 16 16" fill="currentColor" class="pill-icon"><path d="M8 15A7 7 0 108 1a7 7 0 000 14zm3.844-8.791a.75.75 0 00-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 10-1.114 1.004l2.25 2.5a.75.75 0 001.15-.043l4.25-5.5z" /></svg>
            Vegan
          </span>
          <span v-if="dish.is_gluten_free" class="diet-pill">
            <svg viewBox="0 0 16 16" fill="currentColor" class="pill-icon"><path d="M8 15A7 7 0 108 1a7 7 0 000 14zm3.844-8.791a.75.75 0 00-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 10-1.114 1.004l2.25 2.5a.75.75 0 001.15-.043l4.25-5.5z" /></svg>
            Gluten-Free
          </span>
        </div>

        <!-- Nutrition details table -->
        <div v-if="hasExtendedNutrition" class="nutrition-section">
          <h2 class="section-heading">Nutrition Facts</h2>
          <div class="nutrition-table">
            <div class="nut-row thick">
              <span>Calories</span>
              <span>{{ dish.calories }}</span>
            </div>
            <div class="nut-row thick">
              <span>Protein</span>
              <span>{{ dish.protein }}g</span>
            </div>
            <div class="nut-row thick">
              <span>Total Carbs</span>
              <span>{{ dish.carbs }}g</span>
            </div>
            <div v-if="dish.fiber !== null" class="nut-row indent">
              <span>Fiber</span>
              <span>{{ dish.fiber }}g</span>
            </div>
            <div v-if="dish.sugar !== null" class="nut-row indent">
              <span>Sugar</span>
              <span>{{ dish.sugar }}g</span>
            </div>
            <div class="nut-row thick">
              <span>Total Fat</span>
              <span>{{ dish.fat }}g</span>
            </div>
            <div v-if="dish.saturated_fat !== null" class="nut-row indent">
              <span>Saturated Fat</span>
              <span>{{ dish.saturated_fat }}g</span>
            </div>
            <div v-if="dish.sodium !== null" class="nut-row thick">
              <span>Sodium</span>
              <span>{{ dish.sodium }}mg</span>
            </div>
          </div>
        </div>

        <!-- Source footer -->
        <div class="source-footer">
          <span v-if="dish.last_verified" class="source-date">
            Verified {{ new Date(dish.last_verified).toLocaleDateString() }}
          </span>
          <a
            v-if="dish.source_url"
            :href="dish.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="source-link"
          >
            View source
            <svg viewBox="0 0 16 16" fill="currentColor" class="source-arrow">
              <path fill-rule="evenodd" d="M4.22 11.78a.75.75 0 010-1.06L9.44 5.5H5.75a.75.75 0 010-1.5h5.5a.75.75 0 01.75.75v5.5a.75.75 0 01-1.5 0V6.56l-5.22 5.22a.75.75 0 01-1.06 0z" clip-rule="evenodd" />
            </svg>
          </a>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-view {
  max-width: 640px;
  margin: 0 auto;
  padding-bottom: 80px;
}

/* ---- Hero ---- */
.hero {
  position: relative;
  width: 100%;
  height: 280px;
  overflow: hidden;
  background-color: var(--color-surface);
}

.hero-no-image {
  height: 160px;
}

.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  width: 48px;
  height: 48px;
}

.floating-nav {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  z-index: 10;
}

.nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.nav-btn:active {
  transform: scale(0.9);
}

.nav-btn svg {
  width: 18px;
  height: 18px;
}

/* Back button — dark pill, white icon */
.back-btn {
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

/* ---- Content ---- */
.content {
  padding: 0 20px;
}

/* ---- Header ---- */
.dish-header {
  padding: 20px 0 16px;
}

.restaurant-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  transition: color 150ms ease;
}

.restaurant-link:hover {
  color: var(--color-text-primary);
}

.restaurant-logo {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background-color: var(--color-surface);
  padding: 3px;
}

.restaurant-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.restaurant-logo.has-icon {
  padding: 0;
  border: none;
  background: none;
}

.restaurant-logo.has-icon img {
  object-fit: cover;
}

.restaurant-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.restaurant-name {
  line-height: 1;
}

.chevron {
  width: 16px;
  height: 16px;
  opacity: 0.5;
}

.dish-name {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.serving-size {
  font-size: 14px;
  color: var(--color-text-tertiary);
  margin-top: 6px;
}

/* ---- Calorie hero ---- */
.calorie-hero {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding: 16px 0;
  border-top: 1px solid var(--color-border);
}

.cal-number {
  font-size: 48px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.03em;
}

.cal-unit {
  font-size: 18px;
  font-weight: 500;
  color: var(--color-text-tertiary);
}

/* ---- Macro rings ---- */
.macro-row {
  display: flex;
  gap: 16px;
  padding: 8px 0 24px;
}

.macro-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.macro-ring {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 3px solid var(--ring-color);
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

.macro-val {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.macro-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* ---- Density ---- */
.density-section {
  padding: 16px 0;
  border-top: 1px solid var(--color-border);
}

.density-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.density-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.density-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.density-stat {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-primary);
}

.density-badge {
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 13px;
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

/* ---- Dietary pills ---- */
.dietary-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 0;
  border-top: 1px solid var(--color-border);
}

.diet-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 20px;
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
}

.pill-icon {
  width: 14px;
  height: 14px;
}

/* ---- Nutrition table ---- */
.nutrition-section {
  padding: 20px 0;
  border-top: 1px solid var(--color-border);
}

.section-heading {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.nutrition-table {
  border-top: 8px solid var(--color-text-primary);
}

.nut-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 14px;
  color: var(--color-text-secondary);
}

.nut-row span:last-child {
  font-weight: 500;
  color: var(--color-text-primary);
}

.nut-row.thick {
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom-width: 2px;
}

.nut-row.thick span:last-child {
  font-weight: 700;
}

.nut-row.indent span:first-child {
  padding-left: 20px;
  font-weight: 400;
  color: var(--color-text-secondary);
}

/* ---- Source footer ---- */
.source-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-top: 1px solid var(--color-border);
}

.source-date {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.source-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
}

.source-link:hover {
  text-decoration: underline;
}

.source-arrow {
  width: 14px;
  height: 14px;
}

/* ---- Dark mode adjustments ---- */
:root[data-theme='dark'] .density-badge.excellent {
  background-color: #052e16;
  color: #4ade80;
}

:root[data-theme='dark'] .density-badge.good {
  background-color: #422006;
  color: #fbbf24;
}

:root[data-theme='dark'] .density-badge.average {
  background-color: #431407;
  color: #fb923c;
}
</style>
