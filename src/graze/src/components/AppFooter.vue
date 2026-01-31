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
  <footer class="bg-surface border-t border-border mt-8">
    <div class="max-w-6xl mx-auto px-4 py-6">
      <!-- Disclaimer -->
      <div class="bg-surface-elevated border border-border rounded-lg p-3 mb-4">
        <p class="text-sm text-warning">
          ⚠️ Nutritional information is estimated and may vary. Always verify with the restaurant. Not medical advice.
        </p>
      </div>

      <!-- Stats and links -->
      <div class="flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-secondary">
        <div v-if="stats">
          {{ stats.total_dishes }} dishes · {{ stats.total_restaurants }} restaurants
        </div>
        <div class="flex gap-4">
          <a href="#" class="hover:text-primary transition-colors">Terms</a>
          <a href="#" class="hover:text-primary transition-colors">Privacy</a>
          <a href="#" class="hover:text-primary transition-colors">Report Issue</a>
        </div>
      </div>
    </div>
  </footer>
</template>
