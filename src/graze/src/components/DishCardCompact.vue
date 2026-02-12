<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useConfigStore } from '../stores/config'

const props = defineProps({
  dish: {
    type: Object,
    required: true,
  },
})

const configStore = useConfigStore()

const brandColor = computed(() => {
  return configStore.getRestaurantColor(props.dish.restaurant?.slug) || '#06C167'
})
</script>

<template>
  <RouterLink
    :to="{ name: 'dish-detail', params: { id: dish.id } }"
    class="dish-compact"
  >
    <!-- Thumbnail area -->
    <div class="dish-thumbnail" :style="{ backgroundColor: dish.image_url ? undefined : brandColor + '20' }">
      <img
        v-if="dish.image_url"
        :src="dish.image_url"
        :alt="dish.name"
        class="thumb-img"
        loading="lazy"
      />
      <template v-else>
        <svg class="thumb-icon" viewBox="0 0 24 24" fill="none" :stroke="brandColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M3 12h18" />
          <path stroke-linecap="round" d="M5 12c0 3.866 3.134 7 7 7s7-3.134 7-7" />
          <path stroke-linecap="round" d="M9 12V8" />
          <path stroke-linecap="round" d="M12 12V6" />
          <path stroke-linecap="round" d="M15 12V8" />
        </svg>
        <div class="brand-dot" :style="{ backgroundColor: brandColor }"></div>
      </template>
    </div>

    <!-- Info -->
    <div class="dish-info">
      <p class="dish-restaurant">{{ dish.restaurant?.name }}</p>
      <h4 class="dish-name">{{ dish.name }}</h4>
      <div class="dish-macros">
        <span class="macro">
          <svg class="macro-icon" viewBox="0 0 16 16" fill="currentColor">
            <path d="M9.58 1.077a.75.75 0 01.405.82L8.77 6.5h4.48a.75.75 0 01.592 1.21l-5.5 7a.75.75 0 01-1.327-.74L8.23 9.5H3.75a.75.75 0 01-.592-1.21l5.5-7a.75.75 0 01.922-.213z" />
          </svg>
          {{ dish.calories }}
        </span>
        <span class="macro protein">
          <svg class="macro-icon" viewBox="0 0 16 16" fill="currentColor">
            <path fill-rule="evenodd" d="M8 15A7 7 0 108 1a7 7 0 000 14zm.75-10.25a.75.75 0 00-1.5 0v1.5h-1.5a.75.75 0 000 1.5h1.5v1.5a.75.75 0 001.5 0v-1.5h1.5a.75.75 0 000-1.5h-1.5v-1.5z" clip-rule="evenodd" />
          </svg>
          {{ dish.protein }}g
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.dish-compact {
  display: flex;
  flex-direction: column;
  width: 180px;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  text-decoration: none;
  transition: all 200ms ease;
}

.dish-compact:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.dish-thumbnail {
  height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-icon {
  width: 36px;
  height: 36px;
  opacity: 0.6;
}

.brand-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dish-info {
  padding: 10px 12px 12px;
}

.dish-restaurant {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.dish-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
}

.dish-macros {
  display: flex;
  gap: 10px;
}

.macro {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.macro.protein {
  color: var(--color-primary);
  font-weight: 600;
}

.macro-icon {
  width: 12px;
  height: 12px;
}
</style>
