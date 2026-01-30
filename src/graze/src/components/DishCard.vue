<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

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
      <div class="flex-shrink-0">
        <img
          v-if="dish.restaurant.logo_url"
          :src="dish.restaurant.logo_url"
          :alt="dish.restaurant.name"
          class="w-10 h-10 rounded-full object-cover"
        />
        <div
          v-else
          class="w-10 h-10 rounded-full bg-surface flex items-center justify-center text-tertiary text-lg border border-border"
        >
          🍽️
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
