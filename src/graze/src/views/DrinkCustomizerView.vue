<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRestaurant } from '../api/restaurants'
import { useConfigStore } from '../stores/config'
import { useSheetDrag } from '../composables/useSheetDrag'
import { groupDrinkVariants, lookupVariant } from '../utils/drinkParser'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorState from '../components/ErrorState.vue'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()

const restaurant = ref(null)
const loading = ref(true)
const error = ref(null)

// Drink data
const baseDrinks = ref([])
const selectedDrink = ref(null)
const selectedSize = ref(null)
const selectedMilk = ref(null)

// Desktop detection
const isDesktop = ref(false)
let desktopQuery = null
function onDesktopChange(e) { isDesktop.value = e.matches }

const brandColor = computed(() => {
  if (!restaurant.value) return '#06C167'
  return configStore.getRestaurantColor(restaurant.value.slug) || '#06C167'
})

const restaurantLogoUrl = computed(() => {
  if (!restaurant.value) return null
  return configStore.getRestaurantIcon(restaurant.value.slug) || restaurant.value.logo_url
})

// Group base drinks by category
const drinksByCategory = computed(() => {
  const groups = {}
  for (const drink of baseDrinks.value) {
    const cat = drink.category || 'Other'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(drink)
  }
  return Object.entries(groups)
    .map(([name, drinks]) => ({ name, drinks }))
    .sort((a, b) => a.name.localeCompare(b.name))
})

// Currently looked-up variant
const currentVariant = computed(() => {
  if (!selectedDrink.value || !selectedSize.value || !selectedMilk.value) return null
  return lookupVariant(selectedDrink.value, selectedSize.value, selectedMilk.value)
})

const hasSelection = computed(() => currentVariant.value !== null)

const proteinPer100Cal = computed(() => {
  if (!currentVariant.value || currentVariant.value.calories === 0) return 0
  return Math.round((Number(currentVariant.value.protein) * 100 / currentVariant.value.calories) * 10) / 10
})

const densityLabel = computed(() => {
  const ratio = proteinPer100Cal.value
  if (ratio > 12) return 'excellent'
  if (ratio >= 8) return 'good'
  if (ratio >= 5) return 'average'
  return 'low'
})

const hasExtendedNutrition = computed(() => {
  if (!currentVariant.value) return false
  const v = currentVariant.value
  return v.fiber !== null || v.sodium !== null || v.sugar !== null || v.saturated_fat !== null
})

// Draggable nutrition sheet
const barHeight = 55
const expandedHeight = window.innerHeight - 80

const { handleRef: sheetHandleRef, currentHeight: sheetHeight, isDragging: sheetDragging, snapTo: sheetSnapTo } = useSheetDrag({
  snapPoints: [barHeight, expandedHeight],
  initialSnap: 0,
})

const showNutrition = computed(() => sheetHeight.value > barHeight + 20)

const sheetBarStyle = computed(() => ({
  maxHeight: `${sheetHeight.value}px`,
  transition: sheetDragging.value ? 'none' : `max-height 450ms cubic-bezier(0.32, 0.72, 0, 1)`,
  overflow: 'hidden',
}))

onMounted(async () => {
  desktopQuery = window.matchMedia('(min-width: 1024px)')
  isDesktop.value = desktopQuery.matches
  desktopQuery.addEventListener('change', onDesktopChange)

  try {
    const data = await getRestaurant(route.params.slug)
    restaurant.value = data
    const { baseDrinks: drinks } = groupDrinkVariants(data.dishes || [])
    baseDrinks.value = drinks
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  desktopQuery?.removeEventListener('change', onDesktopChange)
})

function goBack() {
  router.back()
}

function selectDrink(drink) {
  if (selectedDrink.value?.baseName === drink.baseName) {
    // Deselect
    selectedDrink.value = null
    selectedSize.value = null
    selectedMilk.value = null
    return
  }

  selectedDrink.value = drink
  // Default to middle size and first milk
  selectedSize.value = drink.sizes.includes('Grande') ? 'Grande' : drink.sizes[0]
  selectedMilk.value = drink.milks[0]
}

function selectSize(size) {
  selectedSize.value = size
}

function selectMilk(milk) {
  selectedMilk.value = milk
}

function clearSelection() {
  selectedDrink.value = null
  selectedSize.value = null
  selectedMilk.value = null
  sheetSnapTo(0)
}

function retry() {
  loading.value = true
  error.value = null
  getRestaurant(route.params.slug)
    .then(data => {
      restaurant.value = data
      const { baseDrinks: drinks } = groupDrinkVariants(data.dishes || [])
      baseDrinks.value = drinks
    })
    .catch(err => { error.value = err })
    .finally(() => { loading.value = false })
}

function formatMilkLabel(milk) {
  return milk.charAt(0).toUpperCase() + milk.slice(1)
}
</script>

<template>
  <div class="drink-view">
    <!-- Loading -->
    <LoadingSpinner v-if="loading" center size="lg" text="Loading drinks..." />

    <!-- Error -->
    <ErrorState v-else-if="error" :error="error" @retry="retry" />

    <!-- Content -->
    <template v-else-if="restaurant">
      <!-- Desktop back bar -->
      <button class="desktop-back" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>

      <!-- Header -->
      <div class="drink-header" :style="{ background: `linear-gradient(135deg, ${brandColor}18, ${brandColor}08)` }">
        <div class="header-nav">
          <button class="nav-btn" @click="goBack" aria-label="Go back">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button v-if="selectedDrink" class="clear-btn" @click="clearSelection">Clear</button>
        </div>

        <div class="header-info">
          <div v-if="restaurantLogoUrl" class="header-logo" :class="{ 'has-icon': configStore.getRestaurantIcon(restaurant.slug) }">
            <img :src="restaurantLogoUrl" :alt="restaurant.name" />
          </div>
          <div v-else class="header-dot" :style="{ backgroundColor: brandColor }"></div>
          <h1 class="header-title">Customize Your Drink</h1>
          <p class="header-sub">{{ restaurant.name }} · {{ baseDrinks.length }} drinks</p>
        </div>
      </div>

      <!-- Drink selection area -->
      <div class="drink-sections">
        <!-- Selected drink customizer -->
        <div v-if="selectedDrink" class="customizer-panel">
          <h2 class="selected-drink-name">{{ selectedDrink.baseName }}</h2>

          <!-- Size picker -->
          <div class="picker-section">
            <h3 class="picker-label">Size</h3>
            <div class="picker-chips">
              <button
                v-for="size in selectedDrink.sizes"
                :key="size"
                class="picker-chip"
                :class="{ active: selectedSize === size }"
                :style="selectedSize === size ? { borderColor: brandColor, backgroundColor: brandColor + '12', color: brandColor } : {}"
                @click="selectSize(size)"
              >
                {{ size }}
              </button>
            </div>
          </div>

          <!-- Milk picker -->
          <div class="picker-section">
            <h3 class="picker-label">Milk</h3>
            <div class="picker-chips">
              <button
                v-for="milk in selectedDrink.milks"
                :key="milk"
                class="picker-chip"
                :class="{ active: selectedMilk === milk }"
                :style="selectedMilk === milk ? { borderColor: brandColor, backgroundColor: brandColor + '12', color: brandColor } : {}"
                @click="selectMilk(milk)"
              >
                {{ formatMilkLabel(milk) }}
              </button>
            </div>
          </div>

          <!-- Variant not found warning -->
          <div v-if="selectedSize && selectedMilk && !currentVariant" class="variant-missing">
            <p>This combination isn't available.</p>
          </div>
        </div>

        <!-- Category sections -->
        <div v-for="group in drinksByCategory" :key="group.name" class="category-section">
          <h2 class="category-heading">{{ group.name }}</h2>
          <div class="drink-grid">
            <button
              v-for="drink in group.drinks"
              :key="drink.baseName"
              class="drink-chip"
              :class="{ active: selectedDrink?.baseName === drink.baseName }"
              :style="selectedDrink?.baseName === drink.baseName ? { borderColor: brandColor, backgroundColor: brandColor + '12' } : {}"
              @click="selectDrink(drink)"
            >
              <span class="drink-name">{{ drink.baseName }}</span>
              <span class="drink-meta">{{ drink.sizes.length }} sizes · {{ drink.milks.length }} milks</span>
            </button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="drinksByCategory.length === 0" class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="empty-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p class="empty-text">No drink variants found.</p>
          <p class="empty-sub">This restaurant doesn't have customizable drinks.</p>
        </div>
      </div>

      <!-- Sticky bottom bar with nutrition -->
      <Transition name="slide-up">
        <div v-if="hasSelection" class="sticky-bar" :style="isDesktop ? {} : sheetBarStyle">
          <div ref="sheetHandleRef" class="bar-summary" @click="sheetSnapTo(showNutrition ? 0 : 1)">
            <div class="bar-left">
              <span class="bar-drink-name">{{ selectedDrink.baseName }}</span>
              <span class="bar-variant">{{ selectedSize }} · {{ formatMilkLabel(selectedMilk) }}</span>
            </div>
            <div class="bar-macros">
              <span class="bar-macro calories">{{ currentVariant.calories }} cal</span>
              <span class="bar-macro protein">{{ Number(currentVariant.protein).toFixed(0) }}g P</span>
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
              <span class="cal-number">{{ currentVariant.calories }}</span>
              <span class="cal-unit">cal</span>
            </div>

            <!-- Macro rings -->
            <div class="macro-row">
              <div class="macro-item">
                <div class="macro-ring" style="--ring-color: var(--color-primary)">
                  <span class="macro-val">{{ Number(currentVariant.protein).toFixed(0) }}g</span>
                </div>
                <span class="macro-label">Protein</span>
              </div>
              <div class="macro-item">
                <div class="macro-ring" style="--ring-color: var(--color-warning)">
                  <span class="macro-val">{{ Number(currentVariant.carbs).toFixed(0) }}g</span>
                </div>
                <span class="macro-label">Carbs</span>
              </div>
              <div class="macro-item">
                <div class="macro-ring" style="--ring-color: var(--color-text-tertiary)">
                  <span class="macro-val">{{ Number(currentVariant.fat).toFixed(0) }}g</span>
                </div>
                <span class="macro-label">Fat</span>
              </div>
            </div>

            <!-- Protein density -->
            <div v-if="currentVariant.calories > 0" class="density-section">
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
                  <span>{{ currentVariant.calories }}</span>
                </div>
                <div class="nut-row thick">
                  <span>Protein</span>
                  <span>{{ Number(currentVariant.protein).toFixed(1) }}g</span>
                </div>
                <div class="nut-row thick">
                  <span>Total Carbs</span>
                  <span>{{ Number(currentVariant.carbs).toFixed(1) }}g</span>
                </div>
                <div v-if="currentVariant.fiber" class="nut-row indent">
                  <span>Fiber</span>
                  <span>{{ Number(currentVariant.fiber).toFixed(1) }}g</span>
                </div>
                <div v-if="currentVariant.sugar" class="nut-row indent">
                  <span>Sugar</span>
                  <span>{{ Number(currentVariant.sugar).toFixed(1) }}g</span>
                </div>
                <div class="nut-row thick">
                  <span>Total Fat</span>
                  <span>{{ Number(currentVariant.fat).toFixed(1) }}g</span>
                </div>
                <div v-if="currentVariant.saturated_fat" class="nut-row indent">
                  <span>Saturated Fat</span>
                  <span>{{ Number(currentVariant.saturated_fat).toFixed(1) }}g</span>
                </div>
                <div v-if="currentVariant.sodium" class="nut-row thick">
                  <span>Sodium</span>
                  <span>{{ currentVariant.sodium }}mg</span>
                </div>
              </div>
            </div>

            <!-- Drink info -->
            <div class="breakdown-section">
              <h2 class="section-heading">Your Drink</h2>
              <div class="breakdown-item">
                <span class="breakdown-name">{{ currentVariant.name }}</span>
              </div>
              <div v-if="currentVariant.serving_size" class="breakdown-item">
                <span class="breakdown-label">Serving</span>
                <span class="breakdown-val">{{ currentVariant.serving_size }}</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </template>
  </div>
</template>

<style scoped>
.drink-view {
  max-width: 640px;
  margin: 0 auto;
  padding-bottom: 120px;
}

/* ---- Header ---- */
.drink-header {
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

/* ---- Customizer panel ---- */
.drink-sections {
  padding: 0 20px;
}

.customizer-panel {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.selected-drink-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 16px;
}

.picker-section {
  margin-bottom: 16px;
}

.picker-section:last-child {
  margin-bottom: 0;
}

.picker-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.picker-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.picker-chip {
  padding: 8px 16px;
  border-radius: 20px;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 150ms ease;
}

.picker-chip:hover {
  border-color: var(--color-text-tertiary);
}

.picker-chip.active {
  font-weight: 600;
}

.variant-missing {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--color-surface);
  color: var(--color-text-tertiary);
  font-size: 13px;
}

/* ---- Category sections ---- */
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

.category-section:first-child .category-heading,
.customizer-panel + .category-section .category-heading {
  border-top: none;
  padding-top: 0;
}

.drink-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ---- Drink chips ---- */
.drink-chip {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
  text-align: left;
  transition: border-color 150ms ease, background-color 150ms ease, transform 100ms ease;
}

.drink-chip:active {
  transform: scale(0.98);
}

.drink-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.drink-meta {
  font-size: 12px;
  color: var(--color-text-tertiary);
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
  bottom: env(safe-area-inset-bottom);
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
  min-width: 0;
}

.bar-drink-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-variant {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.bar-macros {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
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
  flex-shrink: 0;
}

.bar-expand.rotated {
  transform: rotate(180deg);
}

.bar-expand svg {
  width: 18px;
  height: 18px;
}

/* ---- Nutrition sheet ---- */
.nutrition-sheet {
  padding: 0 20px 32px;
  max-height: calc(100dvh - 200px);
  overflow-y: auto;
}

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

.breakdown-label {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.breakdown-val {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
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

/* ---- Dark mode ---- */
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

/* ---- Desktop back button ---- */
.desktop-back {
  display: none;
}

/* ---- Desktop layout ---- */
@media (min-width: 1024px) {
  .drink-view {
    max-width: 1440px;
    margin: 0 auto;
    padding: 0 40px 40px;
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 0 32px;
  }

  .desktop-back {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    grid-column: 1 / -1;
    padding: 20px 0 8px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary);
    font-family: inherit;
    transition: color 150ms ease;
  }

  .desktop-back:hover {
    color: var(--color-text-primary);
  }

  .desktop-back svg {
    width: 16px;
    height: 16px;
  }

  .drink-header {
    grid-column: 1;
    border-radius: 16px;
  }

  .nav-btn {
    display: none;
  }

  .header-nav {
    justify-content: flex-end;
  }

  .drink-sections {
    grid-column: 1;
  }

  .drink-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  /* Nutrition sidebar */
  .sticky-bar {
    position: sticky;
    top: 80px;
    grid-column: 2;
    grid-row: 2 / span 2;
    align-self: flex-start;
    bottom: auto;
    left: auto;
    right: auto;
    max-width: none;
    border-radius: 16px;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-md);
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }

  .bar-summary {
    cursor: default;
    border-bottom: 1px solid var(--color-border);
  }

  .bar-summary:active {
    cursor: default;
  }

  .bar-expand {
    display: none;
  }

  .nutrition-sheet {
    max-height: none;
  }
}
</style>
