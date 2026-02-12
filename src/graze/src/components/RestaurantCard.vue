<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useConfigStore } from '../stores/config'

const props = defineProps({
  restaurant: {
    type: Object,
    required: true,
  },
  fullWidth: {
    type: Boolean,
    default: false,
  },
})

const configStore = useConfigStore()

const brandColor = computed(() => {
  return configStore.getRestaurantColor(props.restaurant.slug) || '#06C167'
})

const gradientStyle = computed(() => ({
  background: `linear-gradient(135deg, ${brandColor.value} 0%, ${brandColor.value}cc 100%)`,
}))

// Category icons for the thumbnail grid
const categoryIcons = ['bowl', 'salad', 'sandwich']
</script>

<template>
  <RouterLink
    :to="{ name: 'restaurant-detail', params: { slug: restaurant.slug } }"
    class="restaurant-card"
    :class="{ 'full-width': fullWidth }"
  >
    <!-- Gradient header with thumbnail icons -->
    <div class="card-header" :style="gradientStyle">
      <div class="thumbnail-grid">
        <div v-for="(icon, i) in categoryIcons" :key="i" class="thumbnail">
          <!-- Bowl -->
          <svg v-if="icon === 'bowl'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" d="M3 12h18" />
            <path stroke-linecap="round" d="M5 12c0 3.866 3.134 7 7 7s7-3.134 7-7" />
          </svg>
          <!-- Salad -->
          <svg v-else-if="icon === 'salad'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c-1.5 0-3 .5-4 2-1 1.5-.5 3 0 4H4c0 4.418 3.582 8 8 8s8-3.582 8-8h-4c.5-1 1-2.5 0-4-1-1.5-2.5-2-4-2z" />
          </svg>
          <!-- Sandwich -->
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 17h16l-1-3H5l-1 3z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 14l1-4h12l1 4" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 10c0-3 2.686-5 6-5s6 2 6 5" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Card body -->
    <div class="card-body">
      <h3 class="restaurant-name">{{ restaurant.name }}</h3>
      <div class="restaurant-meta">
        <span class="meta-item">
          <svg class="meta-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" />
          </svg>
          {{ restaurant.item_count }} items
        </span>
        <span v-if="restaurant.location_count" class="meta-item">
          <svg class="meta-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
          </svg>
          {{ restaurant.location_count.toLocaleString() }} locations
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.restaurant-card {
  display: block;
  width: 260px;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  text-decoration: none;
  transition: all 200ms ease;
}

.restaurant-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
}

.restaurant-card.full-width {
  width: 100%;
}

.card-header {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.thumbnail-grid {
  display: flex;
  gap: 12px;
}

.thumbnail {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail svg {
  width: 22px;
  height: 22px;
  color: rgba(255, 255, 255, 0.9);
}

.card-body {
  padding: 12px;
}

.restaurant-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 6px;
}

.restaurant-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.meta-icon {
  width: 14px;
  height: 14px;
  color: var(--color-text-tertiary);
}

.full-width .card-header {
  height: 80px;
}
</style>
