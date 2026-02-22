<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { getDishes } from '../api/dishes'
import { useConfigStore } from '../stores/config'
import { useSheetDrag } from '../composables/useSheetDrag'

const props = defineProps({
  location: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'view-all'])

const configStore = useConfigStore()
const dishes = ref([])
const loading = ref(false)

const brandColor = computed(() => {
  return configStore.getRestaurantColor(props.location.restaurant?.slug) || '#06C167'
})

const iconUrl = computed(() => {
  return configStore.getRestaurantIcon(props.location.restaurant?.slug)
})

const sheetLogoUrl = computed(() => {
  return iconUrl.value || props.location.restaurant?.logo_url
})

const addressLine = computed(() => {
  const parts = []
  if (props.location.address) parts.push(props.location.address)
  if (props.location.city) parts.push(props.location.city)
  if (props.location.state) parts.push(props.location.state)
  return parts.join(', ')
})

const distanceText = computed(() => {
  if (props.location.distance_miles) {
    return `${props.location.distance_miles} mi`
  }
  return null
})

// Sheet drag setup — start closed, open after measuring content
const { sheetRef, handleRef, sheetStyle, currentHeight, snapTo, updateSnapPoints } = useSheetDrag({
  snapPoints: [0, 400],
  initialSnap: 0,
  onClose: () => emit('close'),
})

function measureAndOpen() {
  if (!sheetRef.value) return
  const height = sheetRef.value.scrollHeight + 16
  updateSnapPoints([0, height])
  snapTo(1)
}

// Overlay fade based on sheet height
const overlayOpacity = computed(() => {
  if (currentHeight.value <= 0) return 0
  return Math.min(currentHeight.value / 300, 1) * 0.3
})

async function loadDishes() {
  if (!props.location.restaurant?.slug) return
  loading.value = true
  try {
    const response = await getDishes({
      restaurants: props.location.restaurant.slug,
      sort: 'protein_ratio_desc',
      limit: 3,
    })
    dishes.value = response.data || []
  } catch (error) {
    console.warn('Failed to load dishes for location:', error)
  } finally {
    loading.value = false
    // Re-measure and re-snap after content changes
    await nextTick()
    if (sheetRef.value) {
      const height = sheetRef.value.scrollHeight + 16
      updateSnapPoints([0, height])
      snapTo(1)
    }
  }
}

onMounted(async () => {
  loadDishes()
  // Measure with skeleton content and open
  await nextTick()
  measureAndOpen()
})
</script>

<template>
  <div class="sheet-overlay" :style="{ backgroundColor: `rgba(0,0,0,${overlayOpacity})` }" @click.self="snapTo(0)">
    <div ref="sheetRef" class="sheet" :style="{ ...sheetStyle, '--brand-color': brandColor }">
      <!-- Drag handle -->
      <div ref="handleRef" class="sheet-drag-area">
        <div class="sheet-handle">
          <div class="handle-bar"></div>
        </div>

        <!-- Header -->
        <div class="sheet-header">
          <div class="header-left">
            <div class="sheet-logo" :class="{ 'has-icon': iconUrl }" :style="{ borderColor: brandColor + '30' }">
              <img v-if="sheetLogoUrl" :src="sheetLogoUrl" :alt="location.restaurant?.name" />
              <div v-else class="logo-fallback" :style="{ backgroundColor: brandColor }">
                {{ location.restaurant?.name?.charAt(0) }}
              </div>
            </div>
            <div>
              <h3 class="restaurant-name">{{ location.restaurant?.name }}</h3>
              <p class="location-address">{{ addressLine }}</p>
            </div>
          </div>
          <button class="close-btn" @click="snapTo(0)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Distance badge -->
      <div class="sheet-body">
        <div v-if="distanceText" class="distance-badge">
          <svg class="distance-icon" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 1a5 5 0 00-5 5c0 3.5 5 9 5 9s5-5.5 5-9a5 5 0 00-5-5zm0 7a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
          {{ distanceText }}
        </div>

        <!-- Dishes preview -->
        <div class="dishes-section">
          <p class="dishes-label">Top Dishes</p>
          <div v-if="loading" class="dishes-loading">
            <div class="skeleton-dish" v-for="n in 3" :key="n"></div>
          </div>
          <div v-else-if="dishes.length" class="dishes-list">
            <div v-for="dish in dishes" :key="dish.id" class="dish-row">
              <div class="dish-info">
                <span class="dish-name">{{ dish.name }}</span>
                <span class="dish-category">{{ dish.category }}</span>
              </div>
              <div class="dish-macros">
                <span class="macro-cal">{{ dish.calories }} cal</span>
                <span class="macro-protein">{{ dish.protein }}g protein</span>
              </div>
            </div>
          </div>
          <div v-else class="dishes-empty">
            <p>No dishes available</p>
          </div>
        </div>

        <!-- View All button -->
        <button
          class="view-all-btn"
          :style="{ backgroundColor: brandColor }"
          @click="emit('view-all', location.restaurant?.slug)"
        >
          View Full Menu
          <svg class="btn-arrow" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sheet-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: flex-end;
  transition: background-color 350ms ease;
}

.sheet {
  width: 100%;
  background-color: var(--color-surface-elevated);
  border-radius: 16px 16px 0 0;
  /* Top shadow for depth + bottom shadow to cover rubber band gap */
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15), 0 200px 0 0 var(--color-surface-elevated);
  overflow: hidden;
}

.sheet-drag-area {
  cursor: grab;
  touch-action: none;
  padding: 0 16px;
}

.sheet-drag-area:active {
  cursor: grabbing;
}

.sheet-handle {
  display: flex;
  justify-content: center;
  padding: 10px 0 6px;
}

.handle-bar {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background-color: var(--color-border);
}

.sheet-body {
  padding: 0 16px calc(16px + env(safe-area-inset-bottom));
}

.sheet-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.sheet-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
}

.sheet-logo.has-icon {
  padding: 0;
  border: none;
}

.sheet-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.sheet-logo.has-icon img {
  object-fit: cover;
}

.logo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

.restaurant-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.location-address {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.3;
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background-color: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 0;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.close-btn:hover {
  background-color: var(--color-border);
}

.distance-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background-color: var(--color-surface);
  padding: 4px 10px;
  border-radius: 12px;
  margin-bottom: 12px;
}

.distance-icon {
  width: 12px;
  height: 12px;
}

.dishes-section {
  margin-bottom: 12px;
}

.dishes-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 8px;
}

.dishes-loading {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-dish {
  height: 40px;
  border-radius: 8px;
  background: var(--color-surface);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.dishes-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background-color: var(--color-border);
  border-radius: 10px;
  overflow: hidden;
}

.dish-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  background-color: var(--color-surface-elevated);
}

.dish-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.dish-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dish-category {
  font-size: 11px;
  color: var(--color-text-tertiary);
  text-transform: capitalize;
}

.dish-macros {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}

.macro-cal {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.macro-protein {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
}

.dishes-empty {
  text-align: center;
  padding: 16px;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.view-all-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px;
  border: none;
  border-radius: 10px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 150ms ease;
}

.view-all-btn:hover {
  opacity: 0.9;
}

.btn-arrow {
  width: 18px;
  height: 18px;
}
</style>
