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
    <div v-if="loading" class="loading-text">Loading...</div>

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
        <img
          v-if="restaurant.logo_url"
          :src="restaurant.logo_url"
          :alt="restaurant.name"
          class="restaurant-logo"
        />
        <span>{{ restaurant.name }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.loading-text {
  font-size: 14px;
  color: rgb(var(--color-text-secondary));
}

.restaurant-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background-color: rgb(var(--color-surface-elevated));
  border: 1px solid rgb(var(--color-border));
  border-radius: 8px;
  color: rgb(var(--color-text-secondary));
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms ease;
}

.restaurant-chip:hover {
  background-color: rgb(var(--color-surface));
  border-color: rgb(var(--color-primary));
  color: rgb(var(--color-text-primary));
}

.restaurant-chip.active {
  background: linear-gradient(135deg, rgb(var(--color-primary)) 0%, rgb(var(--color-accent)) 100%);
  border-color: transparent;
  color: white;
}

.restaurant-logo {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  object-fit: cover;
}
</style>
