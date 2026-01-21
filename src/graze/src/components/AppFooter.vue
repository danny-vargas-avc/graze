<script setup>
import { useRestaurantsStore } from '../stores/restaurants'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'

const restaurantsStore = useRestaurantsStore()
const { stats } = storeToRefs(restaurantsStore)

onMounted(() => {
  restaurantsStore.fetchStats()
})
</script>

<template>
  <footer class="bg-white border-t border-gray-200 mt-8">
    <div class="max-w-6xl mx-auto px-4 py-6">
      <!-- Disclaimer -->
      <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
        <p class="text-sm text-amber-800">
          ⚠️ Nutritional information is estimated and may vary. Always verify with the restaurant. Not medical advice.
        </p>
      </div>

      <!-- Stats and links -->
      <div class="flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-gray-500">
        <div v-if="stats">
          {{ stats.total_dishes }} dishes · {{ stats.total_restaurants }} restaurants
        </div>
        <div class="flex gap-4">
          <a href="#" class="hover:text-gray-700">Terms</a>
          <a href="#" class="hover:text-gray-700">Privacy</a>
          <a href="#" class="hover:text-gray-700">Report Issue</a>
        </div>
      </div>
    </div>
  </footer>
</template>
