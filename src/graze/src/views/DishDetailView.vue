<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDish } from '../api/dishes'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorState from '../components/ErrorState.vue'
import LazyImage from '../components/LazyImage.vue'

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
  <div class="max-w-2xl mx-auto px-4 py-6">
    <!-- Back button -->
    <button
      @click="goBack"
      class="flex items-center gap-2 text-secondary hover:text-primary mb-6 transition-colors"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to search
    </button>

    <!-- Loading -->
    <LoadingSpinner v-if="loading" center size="lg" text="Loading dish details..." />

    <!-- Error -->
    <ErrorState v-else-if="error" :error="error" @retry="retry" />

    <!-- Content -->
    <div v-else-if="dish" class="bg-surface-elevated rounded-lg border border-border overflow-hidden">
      <!-- Header -->
      <div class="p-6 border-b border-border">
        <div class="flex items-start gap-4">
          <div v-if="dish.restaurant.logo_url" class="restaurant-logo">
            <LazyImage
              :src="dish.restaurant.logo_url"
              :alt="dish.restaurant.name"
            />
          </div>
          <div>
            <p class="text-secondary">{{ dish.restaurant.name }}</p>
            <h1 class="text-2xl font-bold text-primary">{{ dish.name }}</h1>
            <p v-if="dish.serving_size" class="text-sm text-secondary mt-1">
              Serving: {{ dish.serving_size }}
            </p>
          </div>
        </div>
      </div>

      <!-- Core macros -->
      <div class="p-6 border-b border-border">
        <h2 class="text-lg font-semibold text-primary mb-4">Macros</h2>
        <div class="grid grid-cols-4 gap-4 text-center">
          <div class="bg-surface rounded-lg p-4 border border-border">
            <p class="text-2xl font-bold text-primary">{{ dish.calories }}</p>
            <p class="text-sm text-secondary">Calories</p>
          </div>
          <div class="bg-surface rounded-lg p-4 border border-border">
            <p class="text-2xl font-bold text-success">{{ dish.protein }}g</p>
            <p class="text-sm text-secondary">Protein</p>
          </div>
          <div class="bg-surface rounded-lg p-4 border border-border">
            <p class="text-2xl font-bold text-clickable">{{ dish.carbs }}g</p>
            <p class="text-sm text-secondary">Carbs</p>
          </div>
          <div class="bg-surface rounded-lg p-4 border border-border">
            <p class="text-2xl font-bold text-warning">{{ dish.fat }}g</p>
            <p class="text-sm text-secondary">Fat</p>
          </div>
        </div>
      </div>

      <!-- Extended nutrition -->
      <div v-if="dish.fiber || dish.sodium || dish.sugar" class="p-6 border-b border-border">
        <h2 class="text-lg font-semibold text-primary mb-4">Additional Nutrition</h2>
        <div class="grid grid-cols-3 gap-4">
          <div v-if="dish.fiber !== null">
            <p class="text-sm text-secondary">Fiber</p>
            <p class="font-medium text-primary">{{ dish.fiber }}g</p>
          </div>
          <div v-if="dish.sodium !== null">
            <p class="text-sm text-secondary">Sodium</p>
            <p class="font-medium text-primary">{{ dish.sodium }}mg</p>
          </div>
          <div v-if="dish.sugar !== null">
            <p class="text-sm text-secondary">Sugar</p>
            <p class="font-medium text-primary">{{ dish.sugar }}g</p>
          </div>
          <div v-if="dish.saturated_fat !== null">
            <p class="text-sm text-secondary">Saturated Fat</p>
            <p class="font-medium text-primary">{{ dish.saturated_fat }}g</p>
          </div>
        </div>
      </div>

      <!-- Dietary info -->
      <div v-if="dish.is_vegetarian || dish.is_vegan || dish.is_gluten_free || dish.allergens?.length" class="p-6 border-b border-border">
        <h2 class="text-lg font-semibold text-primary mb-4">Dietary Information</h2>
        <div class="flex flex-wrap gap-2">
          <span v-if="dish.is_vegetarian" class="px-2 py-1 bg-surface border border-border rounded text-sm text-success font-medium">Vegetarian</span>
          <span v-if="dish.is_vegan" class="px-2 py-1 bg-surface border border-border rounded text-sm text-success font-medium">Vegan</span>
          <span v-if="dish.is_gluten_free" class="px-2 py-1 bg-surface border border-border rounded text-sm text-clickable font-medium">Gluten-Free</span>
        </div>
        <div v-if="dish.allergens?.length" class="mt-3">
          <p class="text-sm text-secondary">Allergens:</p>
          <p class="font-medium text-primary">{{ dish.allergens.join(', ') }}</p>
        </div>
      </div>

      <!-- Source -->
      <div class="p-6">
        <div class="flex items-center justify-between text-sm text-secondary">
          <span v-if="dish.last_verified">
            Last verified: {{ new Date(dish.last_verified).toLocaleDateString() }}
          </span>
          <a
            v-if="dish.source_url"
            :href="dish.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-clickable hover:text-clickable-hover transition-colors"
          >
            View source →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.restaurant-logo {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
}
</style>
