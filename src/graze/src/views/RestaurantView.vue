<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRestaurant } from '../api/restaurants'
import DishCard from '../components/DishCard.vue'

const route = useRoute()
const router = useRouter()

const restaurant = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    restaurant.value = await getRestaurant(route.params.slug)
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
  <div class="max-w-6xl mx-auto px-4 py-6">
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
    <div v-else-if="restaurant">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-8">
        <img
          v-if="restaurant.logo_url"
          :src="restaurant.logo_url"
          :alt="restaurant.name"
          class="w-20 h-20 rounded-full object-cover"
        />
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ restaurant.name }}</h1>
          <p class="text-gray-500">{{ restaurant.item_count }} items</p>
          <a
            v-if="restaurant.website_url"
            :href="restaurant.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-green-600 hover:text-green-700 text-sm"
          >
            Visit website →
          </a>
        </div>
      </div>

      <!-- Dishes -->
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Menu Items</h2>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <DishCard
          v-for="dish in restaurant.dishes"
          :key="dish.id"
          :dish="{ ...dish, restaurant }"
        />
      </div>
    </div>
  </div>
</template>
