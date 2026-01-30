<script setup>
import { onMounted } from 'vue'
import { useRestaurantsStore } from '../stores/restaurants'
import { storeToRefs } from 'pinia'
import LoadingSpinner from './LoadingSpinner.vue'
import LazyImage from './LazyImage.vue'

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
    <LoadingSpinner v-if="loading" size="sm" text="Loading restaurants..." />

    <div v-else class="flex flex-wrap gap-2">
      <button
        v-for="restaurant in restaurants"
        :key="restaurant.slug"
        @click="emit('toggle', restaurant.slug)"
        :class="[
          'restaurant-chip',
          isSelected(restaurant.slug) ? 'active' : ''
        ]"
      >
        <div v-if="restaurant.logo_url" class="restaurant-logo">
          <LazyImage
            :src="restaurant.logo_url"
            :alt="restaurant.name"
          />
        </div>
        <span>{{ restaurant.name }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.restaurant-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms ease;
}

.restaurant-chip:hover {
  background-color: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

.restaurant-chip.active {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border-color: transparent;
  color: white;
}

.restaurant-logo {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}
</style>
