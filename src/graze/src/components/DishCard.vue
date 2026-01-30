<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import LazyImage from './LazyImage.vue'

const props = defineProps({
  dish: {
    type: Object,
    required: true,
  },
})

const distance = computed(() => {
  if (!props.dish.distance_miles) return null
  const dist = parseFloat(props.dish.distance_miles)
  return dist < 10 ? dist.toFixed(1) : Math.round(dist)
})
</script>

<template>
  <RouterLink
    :to="{ name: 'dish-detail', params: { id: dish.id } }"
    class="block bg-surface-elevated rounded-xl border border-border p-4 hover:border-primary hover:shadow-custom-md transition-all duration-200 group"
  >
    <div class="flex items-start gap-3">
      <!-- Restaurant logo -->
      <div class="logo-container">
        <LazyImage
          v-if="dish.restaurant.logo_url"
          :src="dish.restaurant.logo_url"
          :alt="`${dish.restaurant.name} logo`"
        />
        <div v-else class="logo-fallback">
          <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <!-- Restaurant name with distance -->
        <div class="flex items-center gap-2">
          <p class="text-sm text-secondary">{{ dish.restaurant.name }}</p>
          <p v-if="distance" class="text-xs text-tertiary">· {{ distance }} mi</p>
        </div>

        <!-- Dish name -->
        <h3 class="font-semibold text-primary truncate group-hover:text-gradient-primary transition-all">{{ dish.name }}</h3>

        <!-- Macros -->
        <p class="text-sm text-secondary mt-1">
          {{ dish.calories }} cal · {{ dish.protein }}g protein · {{ dish.carbs }}g carbs · {{ dish.fat }}g fat
        </p>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.logo-container {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
}

.logo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface);
  color: var(--color-text-tertiary);
}

.logo-fallback .icon {
  width: 24px;
  height: 24px;
}
</style>
