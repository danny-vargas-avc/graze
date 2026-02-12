<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useFavoritesStore } from '../stores/favorites'
import DishCard from '../components/DishCard.vue'

const favoritesStore = useFavoritesStore()
const { favoriteDishes, loading } = storeToRefs(favoritesStore)

onMounted(() => {
  favoritesStore.loadFavorites()
})
</script>

<template>
  <div class="favorites-view">
    <div class="favorites-header">
      <h1 class="page-title">Favorites</h1>
      <p class="page-subtitle" v-if="favoriteDishes.length > 0">{{ favoriteDishes.length }} saved dishes</p>
    </div>

    <div class="favorites-content">
      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div v-for="i in 3" :key="i" class="skeleton-card"></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="favoriteDishes.length === 0" class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
        <h2 class="empty-title">No favorites yet</h2>
        <p class="empty-text">Tap the heart icon on any dish to save it here.</p>
      </div>

      <!-- Favorites list -->
      <div v-else class="favorites-list">
        <DishCard
          v-for="dish in favoriteDishes"
          :key="dish.id"
          :dish="dish"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorites-view {
  height: 100%;
  overflow-y: auto;
}

.favorites-header {
  padding: 20px 16px 12px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.favorites-content {
  padding: 0 16px 24px;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 32px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: var(--color-text-tertiary);
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.empty-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  max-width: 260px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-card {
  height: 80px;
  border-radius: 12px;
  background: var(--color-surface);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
