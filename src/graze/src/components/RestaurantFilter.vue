<script setup>
import { onMounted } from 'vue'
import { useRestaurantsStore } from '../stores/restaurants'
import { storeToRefs } from 'pinia'

const props = defineProps({
  selected: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['toggle'])

const restaurantsStore = useRestaurantsStore()
const { restaurants, loading } = storeToRefs(restaurantsStore)

onMounted(() => {
  restaurantsStore.fetchRestaurants()
})

function isSelected(slug) {
  return props.selected.includes(slug)
}
</script>

<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">Restaurants</label>

    <div v-if="loading" class="text-sm text-gray-500">Loading...</div>

    <div v-else class="flex flex-wrap gap-2">
      <button
        v-for="restaurant in restaurants"
        :key="restaurant.slug"
        @click="emit('toggle', restaurant.slug)"
        :class="[
          'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
          isSelected(restaurant.slug)
            ? 'bg-green-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        <img
          v-if="restaurant.logo_url"
          :src="restaurant.logo_url"
          :alt="restaurant.name"
          class="w-4 h-4 rounded-full object-cover"
        />
        <span>{{ restaurant.name }}</span>
      </button>
    </div>
  </div>
</template>
