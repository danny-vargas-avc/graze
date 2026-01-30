<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDish } from '../api/dishes'

const route = useRoute()
const router = useRouter()

const dish = ref(null)
const loading = ref(true)
const error = ref(null)

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
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-6">
    <!-- Back button -->
    <button
      @click="goBack"
      class="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-6"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to search
    </button>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-600">{{ error.message }}</p>
    </div>

    <!-- Content -->
    <div v-else-if="dish" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-start gap-4">
          <img
            v-if="dish.restaurant.logo_url"
            :src="dish.restaurant.logo_url"
            :alt="dish.restaurant.name"
            class="w-16 h-16 rounded-full object-cover"
          />
          <div>
            <p class="text-gray-500">{{ dish.restaurant.name }}</p>
            <h1 class="text-2xl font-bold text-gray-900">{{ dish.name }}</h1>
            <p v-if="dish.serving_size" class="text-sm text-gray-500 mt-1">
              Serving: {{ dish.serving_size }}
            </p>
          </div>
        </div>
      </div>

      <!-- Core macros -->
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Macros</h2>
        <div class="grid grid-cols-4 gap-4 text-center">
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-2xl font-bold text-gray-900">{{ dish.calories }}</p>
            <p class="text-sm text-gray-500">Calories</p>
          </div>
          <div class="bg-green-50 rounded-lg p-4">
            <p class="text-2xl font-bold text-green-700">{{ dish.protein }}g</p>
            <p class="text-sm text-gray-500">Protein</p>
          </div>
          <div class="bg-blue-50 rounded-lg p-4">
            <p class="text-2xl font-bold text-blue-700">{{ dish.carbs }}g</p>
            <p class="text-sm text-gray-500">Carbs</p>
          </div>
          <div class="bg-yellow-50 rounded-lg p-4">
            <p class="text-2xl font-bold text-yellow-700">{{ dish.fat }}g</p>
            <p class="text-sm text-gray-500">Fat</p>
          </div>
        </div>
      </div>

      <!-- Extended nutrition -->
      <div v-if="dish.fiber || dish.sodium || dish.sugar" class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Additional Nutrition</h2>
        <div class="grid grid-cols-3 gap-4">
          <div v-if="dish.fiber !== null">
            <p class="text-sm text-gray-500">Fiber</p>
            <p class="font-medium">{{ dish.fiber }}g</p>
          </div>
          <div v-if="dish.sodium !== null">
            <p class="text-sm text-gray-500">Sodium</p>
            <p class="font-medium">{{ dish.sodium }}mg</p>
          </div>
          <div v-if="dish.sugar !== null">
            <p class="text-sm text-gray-500">Sugar</p>
            <p class="font-medium">{{ dish.sugar }}g</p>
          </div>
          <div v-if="dish.saturated_fat !== null">
            <p class="text-sm text-gray-500">Saturated Fat</p>
            <p class="font-medium">{{ dish.saturated_fat }}g</p>
          </div>
        </div>
      </div>

      <!-- Dietary info -->
      <div v-if="dish.is_vegetarian || dish.is_vegan || dish.is_gluten_free || dish.allergens?.length" class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Dietary Information</h2>
        <div class="flex flex-wrap gap-2">
          <span v-if="dish.is_vegetarian" class="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">Vegetarian</span>
          <span v-if="dish.is_vegan" class="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">Vegan</span>
          <span v-if="dish.is_gluten_free" class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">Gluten-Free</span>
        </div>
        <div v-if="dish.allergens?.length" class="mt-3">
          <p class="text-sm text-gray-500">Allergens:</p>
          <p class="font-medium">{{ dish.allergens.join(', ') }}</p>
        </div>
      </div>

      <!-- Source -->
      <div class="p-6">
        <div class="flex items-center justify-between text-sm text-gray-500">
          <span v-if="dish.last_verified">
            Last verified: {{ new Date(dish.last_verified).toLocaleDateString() }}
          </span>
          <a
            v-if="dish.source_url"
            :href="dish.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-green-600 hover:text-green-700"
          >
            View source →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
