<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useConfigStore } from '../stores/config'
import { useFavoritesStore } from '../stores/favorites'
import LazyImage from './LazyImage.vue'

const props = defineProps({
  dish: {
    type: Object,
    required: true,
  },
})

const configStore = useConfigStore()
const favoritesStore = useFavoritesStore()

const distance = computed(() => {
  if (!props.dish.distance_miles) return null
  const dist = parseFloat(props.dish.distance_miles)
  return dist < 10 ? dist.toFixed(1) : Math.round(dist)
})

const brandColor = computed(() => {
  return configStore.getRestaurantColor(props.dish.restaurant?.slug) || '#06C167'
})

const iconUrl = computed(() => {
  return configStore.getRestaurantIcon(props.dish.restaurant?.slug)
})

const isFavorite = computed(() => favoritesStore.isFavorite(props.dish.id))

function toggleFavorite(e) {
  e.preventDefault()
  e.stopPropagation()
  favoritesStore.toggle(props.dish.id)
}
</script>

<template>
  <RouterLink
    :to="{ name: 'dish-detail', params: { id: dish.id } }"
    class="dish-card"
  >
    <!-- Brand color accent -->
    <div class="brand-accent" :style="{ backgroundColor: brandColor }"></div>

    <div class="card-content">
      <!-- Food photo or restaurant logo -->
      <div class="logo-container" :class="{ 'has-photo': dish.image_url, 'has-icon': !dish.image_url && iconUrl }">
        <img
          v-if="dish.image_url"
          :src="dish.image_url"
          :alt="dish.name"
          class="food-photo"
          loading="lazy"
        />
        <img
          v-else-if="iconUrl"
          :src="iconUrl"
          :alt="`${dish.restaurant.name} logo`"
          class="icon-photo"
        />
        <LazyImage
          v-else-if="dish.restaurant.logo_url"
          :src="dish.restaurant.logo_url"
          :alt="`${dish.restaurant.name} logo`"
        />
        <div v-else class="logo-fallback" :style="{ backgroundColor: brandColor + '15' }">
          <svg class="icon" viewBox="0 0 24 24" fill="none" :stroke="brandColor" stroke-width="1.5">
            <path stroke-linecap="round" d="M3 12h18" />
            <path stroke-linecap="round" d="M5 12c0 3.866 3.134 7 7 7s7-3.134 7-7" />
            <path stroke-linecap="round" d="M12 12V6" />
          </svg>
        </div>
      </div>

      <!-- Content -->
      <div class="card-text">
        <!-- Restaurant name with distance -->
        <div class="restaurant-row">
          <p class="restaurant-name">{{ dish.restaurant.name }}</p>
          <p v-if="distance" class="distance">{{ distance }} mi</p>
        </div>

        <!-- Dish name -->
        <h3 class="dish-name">{{ dish.name }}</h3>

        <!-- Macros -->
        <div class="macros">
          <span class="macro">
            <svg class="macro-icon" viewBox="0 0 16 16" fill="currentColor">
              <path d="M9.58 1.077a.75.75 0 01.405.82L8.77 6.5h4.48a.75.75 0 01.592 1.21l-5.5 7a.75.75 0 01-1.327-.74L8.23 9.5H3.75a.75.75 0 01-.592-1.21l5.5-7a.75.75 0 01.922-.213z" />
            </svg>
            {{ dish.calories }}
          </span>
          <span class="macro protein">
            <svg class="macro-icon" viewBox="0 0 16 16" fill="currentColor">
              <path fill-rule="evenodd" d="M8 15A7 7 0 108 1a7 7 0 000 14zm.75-10.25a.75.75 0 00-1.5 0v1.5h-1.5a.75.75 0 000 1.5h1.5v1.5a.75.75 0 001.5 0v-1.5h1.5a.75.75 0 000-1.5h-1.5v-1.5z" clip-rule="evenodd" />
            </svg>
            {{ dish.protein }}g
          </span>
          <span class="macro">{{ dish.carbs }}g carbs</span>
          <span class="macro">{{ dish.fat }}g fat</span>
        </div>
      </div>

      <!-- Favorite button -->
      <button class="favorite-btn" @click="toggleFavorite" :class="{ active: isFavorite }">
        <!-- Outline heart -->
        <svg v-if="!isFavorite" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
        <!-- Filled heart -->
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
        </svg>
      </button>
    </div>
  </RouterLink>
</template>

<style scoped>
.dish-card {
  display: flex;
  background-color: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  overflow: hidden;
  text-decoration: none;
  transition: all 200ms ease;
}

.dish-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.brand-accent {
  width: 4px;
  flex-shrink: 0;
}

.card-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  flex: 1;
  min-width: 0;
}

.logo-container {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
}

.logo-container.has-photo {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  padding: 0;
  background: none;
}

.logo-container.has-icon {
  padding: 0;
  border: none;
}

.food-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.icon-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-fallback .icon {
  width: 22px;
  height: 22px;
}

.card-text {
  flex: 1;
  min-width: 0;
}

.restaurant-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.restaurant-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.distance {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.distance::before {
  content: '\00b7  ';
}

.dish-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.macros {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.macro {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.macro.protein {
  color: var(--color-primary);
  font-weight: 600;
}

.macro-icon {
  width: 12px;
  height: 12px;
}

.favorite-btn {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 50%;
  color: var(--color-text-tertiary);
  transition: all 150ms ease;
  padding: 0;
}

.favorite-btn:hover {
  background-color: var(--color-surface);
  color: var(--color-error);
}

.favorite-btn.active {
  color: var(--color-error);
}

.favorite-btn svg {
  width: 20px;
  height: 20px;
}
</style>
