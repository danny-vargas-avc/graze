<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  dish: {
    type: Object,
    required: true,
  },
})

const densityColors = {
  excellent: 'bg-green-100 text-green-800',
  good: 'bg-yellow-100 text-yellow-800',
  average: 'bg-orange-100 text-orange-800',
  low: 'bg-gray-100 text-gray-600',
}

const densityDots = {
  excellent: '🟢',
  good: '🟡',
  average: '🟠',
  low: '⚪',
}

const densityClass = computed(() => densityColors[props.dish.density_label] || densityColors.low)
const densityDot = computed(() => densityDots[props.dish.density_label] || densityDots.low)
</script>

<template>
  <RouterLink
    :to="{ name: 'dish-detail', params: { id: dish.id } }"
    class="block bg-white rounded-lg border border-gray-200 p-4 hover:border-green-300 hover:shadow-sm transition-all"
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
          class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-lg"
        >
          🍽️
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <!-- Restaurant name -->
        <p class="text-sm text-gray-500">{{ dish.restaurant.name }}</p>

        <!-- Dish name -->
        <h3 class="font-semibold text-gray-900 truncate">{{ dish.name }}</h3>

        <!-- Macros -->
        <p class="text-sm text-gray-600 mt-1">
          {{ dish.calories }} cal · {{ dish.protein }}g protein · {{ dish.carbs }}g carbs · {{ dish.fat }}g fat
        </p>

        <!-- Density label -->
        <div class="mt-2">
          <span :class="['inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium', densityClass]">
            {{ densityDot }} {{ dish.density_label.charAt(0).toUpperCase() + dish.density_label.slice(1) }} protein density
          </span>
        </div>
      </div>
    </div>
  </RouterLink>
</template>
