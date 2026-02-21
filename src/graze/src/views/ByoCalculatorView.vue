<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getByoComponents } from '../api/restaurants'
import { useConfigStore } from '../stores/config'
import { useSheetDrag } from '../composables/useSheetDrag'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorState from '../components/ErrorState.vue'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()

const restaurant = ref(null)
const categories = ref({})
const loading = ref(true)
const error = ref(null)
const quantities = reactive({}) // { [itemId]: quantity }

const brandColor = computed(() => {
  if (!restaurant.value) return '#06C167'
  return configStore.getRestaurantColor(restaurant.value.slug) || '#06C167'
})

const restaurantLogoUrl = computed(() => {
  if (!restaurant.value) return null
  return configStore.getRestaurantIcon(restaurant.value.slug) || restaurant.value.logo_url
})

// Category display order and labels
const categoryOrder = ['base', 'protein', 'topping', 'dressing', 'extra']
const categoryLabels = {
  base: 'Base',
  protein: 'Protein',
  topping: 'Toppings',
  dressing: 'Dressing & Sauce',
  extra: 'Extras',
}

const orderedCategories = computed(() => {
  return categoryOrder.filter(cat => categories.value[cat]?.length > 0)
})

// Build a lookup map of all items by ID
const allItems = computed(() => {
  const map = {}
  for (const cat of Object.values(categories.value)) {
    for (const item of cat) {
      map[item.id] = item
    }
  }
  return map
})

// Selected items with quantities
const selectedItems = computed(() => {
  return Object.entries(quantities)
    .filter(([, qty]) => qty > 0)
    .map(([id, qty]) => ({ ...allItems.value[id], qty }))
    .filter(item => item.id) // guard against stale IDs
})

// Totals (multiply each nutrient by its quantity)
const totals = computed(() => {
  const t = { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0, sodium: 0, sugar: 0, saturated_fat: 0 }
  for (const item of selectedItems.value) {
    const q = item.qty
    t.calories += Math.round((Number(item.calories) || 0) * q)
    t.protein += (Number(item.protein) || 0) * q
    t.carbs += (Number(item.carbs) || 0) * q
    t.fat += (Number(item.fat) || 0) * q
    t.fiber += (Number(item.fiber) || 0) * q
    t.sodium += Math.round((Number(item.sodium) || 0) * q)
    t.sugar += (Number(item.sugar) || 0) * q
    t.saturated_fat += (Number(item.saturated_fat) || 0) * q
  }
  return t
})

const hasSelection = computed(() => selectedItems.value.length > 0)

const itemCount = computed(() => {
  return selectedItems.value.reduce((sum, item) => sum + item.qty, 0)
})

const proteinPer100Cal = computed(() => {
  if (totals.value.calories === 0) return 0
  return Math.round((totals.value.protein * 100 / totals.value.calories) * 10) / 10
})

const densityLabel = computed(() => {
  const ratio = proteinPer100Cal.value
  if (ratio > 12) return 'excellent'
  if (ratio >= 8) return 'good'
  if (ratio >= 5) return 'average'
  return 'low'
})

const hasExtendedNutrition = computed(() => {
  return selectedItems.value.some(item =>
    item.fiber !== null || item.sodium !== null || item.sugar !== null || item.saturated_fat !== null
  )
})

// Draggable nutrition sheet
const barHeight = 55
const expandedHeight = Math.min(window.innerHeight * 0.7, 600)

const { handleRef: byoHandleRef, sheetStyle: byoSheetStyle, currentHeight: byoHeight, isDragging: byoDragging, snapTo: byoSnapTo } = useSheetDrag({
  snapPoints: [barHeight, expandedHeight],
  initialSnap: 0,
})

const showNutrition = computed(() => byoHeight.value > barHeight + 20)

const byoBarStyle = computed(() => ({
  maxHeight: `${byoHeight.value}px`,
  transition: byoDragging.value ? 'none' : `max-height 350ms cubic-bezier(0.32, 0.72, 0, 1)`,
  overflow: 'hidden',
}))

onMounted(async () => {
  try {
    const data = await getByoComponents(route.params.slug)
    restaurant.value = data.restaurant
    categories.value = data.categories
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.back()
}

function getQty(item) {
  return quantities[item.id] || 0
}

function isSelected(item) {
  return getQty(item) > 0
}

function toggleItem(item) {
  if (isSelected(item)) {
    delete quantities[item.id]
  } else {
    quantities[item.id] = 1
  }
}

function incrementQty(item, e) {
  e.stopPropagation()
  const current = getQty(item)
  if (current < 2) {
    quantities[item.id] = current + 0.5
  }
}

function decrementQty(item, e) {
  e.stopPropagation()
  const current = getQty(item)
  if (current <= 0.5) {
    delete quantities[item.id]
  } else {
    quantities[item.id] = current - 0.5
  }
}

function formatQty(qty) {
  if (qty === 0.5) return '½'
  if (qty === 1.5) return '1½'
  return qty.toString()
}

function clearAll() {
  Object.keys(quantities).forEach(key => delete quantities[key])
  byoSnapTo(0)
}

function retry() {
  loading.value = true
  error.value = null
  getByoComponents(route.params.slug)
    .then(data => {
      restaurant.value = data.restaurant
      categories.value = data.categories
    })
    .catch(err => { error.value = err })
    .finally(() => { loading.value = false })
}
</script>

<template>
  <div class="byo-view">
    <!-- Loading -->
    <LoadingSpinner v-if="loading" center size="lg" text="Loading ingredients..." />

    <!-- Error -->
    <ErrorState v-else-if="error" :error="error" @retry="retry" />

    <!-- Content -->
    <template v-else-if="restaurant">
      <!-- Header -->
      <div class="byo-header" :style="{ background: `linear-gradient(135deg, ${brandColor}18, ${brandColor}08)` }">
        <div class="header-nav">
          <button class="nav-btn" @click="goBack" aria-label="Go back">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button v-if="hasSelection" class="clear-btn" @click="clearAll">Clear</button>
        </div>

        <div class="header-info">
          <div v-if="restaurantLogoUrl" class="header-logo" :class="{ 'has-icon': configStore.getRestaurantIcon(restaurant.slug) }">
            <img :src="restaurantLogoUrl" :alt="restaurant.name" />
          </div>
          <div v-else class="header-dot" :style="{ backgroundColor: brandColor }"></div>
          <h1 class="header-title">Build Your Bowl</h1>
          <p class="header-sub">{{ restaurant.name }}</p>
        </div>
      </div>

      <!-- Ingredient selection -->
      <div class="ingredient-sections">
        <div v-for="cat in orderedCategories" :key="cat" class="category-section">
          <h2 class="category-heading">{{ categoryLabels[cat] || cat }}</h2>
          <div class="ingredient-grid">
            <button
              v-for="item in categories[cat]"
              :key="item.id"
              class="ingredient-chip"
              :class="{ active: isSelected(item) }"
              :style="isSelected(item) ? { borderColor: brandColor, backgroundColor: brandColor + '12' } : {}"
              @click="toggleItem(item)"
            >
              <div class="chip-main">
                <span class="chip-name">{{ item.name }}</span>
                <span v-if="!isSelected(item)" class="chip-cal">{{ item.calories }} cal</span>
                <!-- Quantity controls when selected -->
                <div v-else class="qty-controls" @click.stop>
                  <button class="qty-btn" @click="decrementQty(item, $event)" :style="{ color: brandColor }">
                    <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" clip-rule="evenodd" /></svg>
                  </button>
                  <span class="qty-label" :style="{ color: brandColor }">{{ formatQty(getQty(item)) }}×</span>
                  <button class="qty-btn" @click="incrementQty(item, $event)" :style="{ color: brandColor }" :disabled="getQty(item) >= 2">
                    <svg viewBox="0 0 20 20" fill="currentColor"><path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" /></svg>
                  </button>
                </div>
              </div>
              <div class="chip-macros">
                <span class="chip-macro"><strong>{{ item.protein }}g</strong> P</span>
                <span class="chip-sep"></span>
                <span class="chip-macro"><strong>{{ item.carbs }}g</strong> C</span>
                <span class="chip-sep"></span>
                <span class="chip-macro"><strong>{{ item.fat }}g</strong> F</span>
              </div>
            </button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="orderedCategories.length === 0" class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="empty-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p class="empty-text">No ingredients available yet.</p>
          <p class="empty-sub">Check back soon — we're adding BYO data for {{ restaurant.name }}.</p>
        </div>
      </div>

      <!-- Sticky bottom bar with running total -->
      <Transition name="slide-up">
        <div v-if="hasSelection" class="sticky-bar" :style="byoBarStyle">
          <div ref="byoHandleRef" class="bar-summary" @click="byoSnapTo(showNutrition ? 0 : 1)">
            <div class="bar-left">
              <span class="bar-count">{{ selectedItems.length }} item{{ selectedItems.length > 1 ? 's' : '' }}</span>
              <span class="bar-cals">{{ totals.calories }} cal</span>
            </div>
            <div class="bar-macros">
              <span class="bar-macro protein">{{ totals.protein.toFixed(0) }}g P</span>
              <span class="bar-macro carbs">{{ totals.carbs.toFixed(0) }}g C</span>
              <span class="bar-macro fat">{{ totals.fat.toFixed(0) }}g F</span>
            </div>
            <button class="bar-expand" :class="{ rotated: showNutrition }">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M14.77 12.79a.75.75 0 01-1.06-.02L10 8.832 6.29 12.77a.75.75 0 11-1.08-1.04l4.25-4.5a.75.75 0 011.08 0l4.25 4.5a.75.75 0 01-.02 1.06z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <!-- Expanded nutrition sheet -->
            <div class="nutrition-sheet">
              <!-- Calorie hero -->
              <div class="calorie-hero">
                <span class="cal-number">{{ totals.calories }}</span>
                <span class="cal-unit">cal</span>
              </div>

              <!-- Macro rings -->
              <div class="macro-row">
                <div class="macro-item">
                  <div class="macro-ring" style="--ring-color: var(--color-primary)">
                    <span class="macro-val">{{ totals.protein.toFixed(0) }}g</span>
                  </div>
                  <span class="macro-label">Protein</span>
                </div>
                <div class="macro-item">
                  <div class="macro-ring" style="--ring-color: var(--color-warning)">
                    <span class="macro-val">{{ totals.carbs.toFixed(0) }}g</span>
                  </div>
                  <span class="macro-label">Carbs</span>
                </div>
                <div class="macro-item">
                  <div class="macro-ring" style="--ring-color: var(--color-text-tertiary)">
                    <span class="macro-val">{{ totals.fat.toFixed(0) }}g</span>
                  </div>
                  <span class="macro-label">Fat</span>
                </div>
              </div>

              <!-- Protein density -->
              <div v-if="totals.calories > 0" class="density-section">
                <div class="density-row">
                  <div class="density-left">
                    <span class="density-title">Protein Density</span>
                    <span class="density-stat">{{ proteinPer100Cal }}g per 100 cal</span>
                  </div>
                  <span class="density-badge" :class="densityLabel">{{ densityLabel }}</span>
                </div>
              </div>

              <!-- Nutrition facts table -->
              <div v-if="hasExtendedNutrition" class="nutrition-section">
                <h2 class="section-heading">Nutrition Facts</h2>
                <div class="nutrition-table">
                  <div class="nut-row thick">
                    <span>Calories</span>
                    <span>{{ totals.calories }}</span>
                  </div>
                  <div class="nut-row thick">
                    <span>Protein</span>
                    <span>{{ totals.protein.toFixed(1) }}g</span>
                  </div>
                  <div class="nut-row thick">
                    <span>Total Carbs</span>
                    <span>{{ totals.carbs.toFixed(1) }}g</span>
                  </div>
                  <div v-if="totals.fiber" class="nut-row indent">
                    <span>Fiber</span>
                    <span>{{ totals.fiber.toFixed(1) }}g</span>
                  </div>
                  <div v-if="totals.sugar" class="nut-row indent">
                    <span>Sugar</span>
                    <span>{{ totals.sugar.toFixed(1) }}g</span>
                  </div>
                  <div class="nut-row thick">
                    <span>Total Fat</span>
                    <span>{{ totals.fat.toFixed(1) }}g</span>
                  </div>
                  <div v-if="totals.saturated_fat" class="nut-row indent">
                    <span>Saturated Fat</span>
                    <span>{{ totals.saturated_fat.toFixed(1) }}g</span>
                  </div>
                  <div v-if="totals.sodium" class="nut-row thick">
                    <span>Sodium</span>
                    <span>{{ totals.sodium }}mg</span>
                  </div>
                </div>
              </div>

              <!-- Selected items breakdown -->
              <div class="breakdown-section">
                <h2 class="section-heading">Your Bowl</h2>
                <div v-for="item in selectedItems" :key="item.id" class="breakdown-item">
                  <span class="breakdown-name">
                    <span v-if="item.qty !== 1" class="breakdown-qty">{{ formatQty(item.qty) }}×</span>
                    {{ item.name }}
                  </span>
                  <span class="breakdown-cal">{{ Math.round(item.calories * item.qty) }} cal</span>
                </div>
              </div>
            </div>
        </div>
      </Transition>
    </template>
  </div>
</template>

<style scoped>
.byo-view {
  max-width: 640px;
  margin: 0 auto;
  padding-bottom: 200px;
}

/* ---- Header ---- */
.byo-header {
  padding: 16px 20px 24px;
}

.header-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
  background: var(--color-surface-elevated);
  color: var(--color-text-primary);
  transition: transform 150ms ease;
}

.nav-btn:active {
  transform: scale(0.9);
}

.nav-btn svg {
  width: 18px;
  height: 18px;
}

.clear-btn {
  padding: 6px 16px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-surface-elevated);
  transition: color 150ms ease;
}

.clear-btn:hover {
  color: var(--color-error);
}

.header-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 4px;
}

.header-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--color-surface);
  padding: 4px;
  margin-bottom: 8px;
}

.header-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.header-logo.has-icon {
  padding: 0;
  background: none;
}

.header-logo.has-icon img {
  object-fit: cover;
}

.header-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-bottom: 8px;
}

.header-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.header-sub {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* ---- Category sections ---- */
.ingredient-sections {
  padding: 0 20px;
}

.category-section {
  margin-bottom: 24px;
}

.category-heading {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}

.category-section:first-child .category-heading {
  border-top: none;
  padding-top: 0;
}

.ingredient-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ---- Ingredient chips ---- */
.ingredient-chip {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
  text-align: left;
  transition: border-color 150ms ease, background-color 150ms ease, transform 100ms ease;
}

.ingredient-chip:active {
  transform: scale(0.98);
}

.chip-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chip-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.chip-cal {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-tertiary);
}

.chip-macros {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chip-macro {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.chip-macro strong {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.chip-sep {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-border);
}

/* ---- Quantity controls ---- */
.qty-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.qty-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--color-surface-elevated);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: background 150ms ease, transform 100ms ease;
}

.qty-btn:active {
  transform: scale(0.9);
}

.qty-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.qty-btn:disabled:active {
  transform: none;
}

.qty-btn svg {
  width: 16px;
  height: 16px;
}

.qty-label {
  font-size: 14px;
  font-weight: 700;
  min-width: 28px;
  text-align: center;
}

/* ---- Empty state ---- */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px;
  text-align: center;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--color-text-tertiary);
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.empty-sub {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

/* ---- Sticky bottom bar ---- */
.sticky-bar {
  position: fixed;
  bottom: calc(60px + env(safe-area-inset-bottom));
  left: 0;
  right: 0;
  max-width: 640px;
  margin: 0 auto;
  z-index: 50;
  background: var(--color-surface-elevated);
  border-top: 1px solid var(--color-border);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.12);
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.bar-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  cursor: grab;
  position: sticky;
  top: 0;
  background: var(--color-surface-elevated);
  z-index: 1;
  touch-action: none;
}

.bar-summary:active {
  cursor: grabbing;
}

.bar-left {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.bar-count {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.bar-cals {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.bar-macros {
  display: flex;
  gap: 10px;
}

.bar-macro {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.bar-macro.protein {
  color: var(--color-primary);
}

.bar-expand {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  transition: transform 200ms ease;
}

.bar-expand.rotated {
  transform: rotate(180deg);
}

.bar-expand svg {
  width: 18px;
  height: 18px;
}

/* ---- Nutrition sheet (inside sticky bar) ---- */
.nutrition-sheet {
  padding: 0 20px 20px;
  overflow-y: auto;
}

/* Reuse DishDetailView nutrition styles */
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

/* ---- Breakdown ---- */
.breakdown-section {
  padding: 20px 0 0;
  border-top: 1px solid var(--color-border);
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.breakdown-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.breakdown-cal {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.breakdown-qty {
  font-weight: 600;
  color: var(--color-primary);
  margin-right: 2px;
}

/* ---- Transitions ---- */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 250ms ease, opacity 250ms ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
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

:root[data-theme='dark'] .sticky-bar {
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4);
}
</style>
