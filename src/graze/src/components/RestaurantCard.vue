<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useConfigStore } from '../stores/config'

const props = defineProps({
  restaurant: {
    type: Object,
    required: true,
  },
  fullWidth: {
    type: Boolean,
    default: false,
  },
})

const configStore = useConfigStore()

const brandColor = computed(() => {
  return configStore.getRestaurantColor(props.restaurant.slug) || '#06C167'
})

const gradientStyle = computed(() => ({
  background: `linear-gradient(135deg, ${brandColor.value} 0%, ${brandColor.value}cc 100%)`,
}))

const iconUrl = computed(() => {
  return configStore.getRestaurantIcon(props.restaurant.slug)
})

const bodyLogoUrl = computed(() => {
  return iconUrl.value || props.restaurant.logo_url
})

const hasIcon = computed(() => !!iconUrl.value)

</script>

<template>
  <RouterLink
    :to="{ name: 'restaurant-detail', params: { slug: restaurant.slug } }"
    class="restaurant-card"
    :class="{ 'full-width': fullWidth }"
  >
    <!-- Gradient header with logo -->
    <div class="card-header" :style="gradientStyle">
      <img
        v-if="restaurant.logo_url"
        :src="restaurant.logo_url"
        :alt="restaurant.name"
        class="header-logo"
      />
      <div v-else class="logo-placeholder">
        <span>{{ restaurant.name.charAt(0) }}</span>
      </div>
    </div>

    <!-- Card body -->
    <div class="card-body">
      <div class="body-top">
        <div v-if="bodyLogoUrl" class="body-logo" :class="{ 'has-icon': hasIcon }">
          <img :src="bodyLogoUrl" :alt="restaurant.name" />
        </div>
        <div class="body-text">
          <h3 class="restaurant-name">{{ restaurant.name }}</h3>
          <div class="restaurant-meta">
            <span class="meta-item">{{ restaurant.item_count }} items</span>
            <span v-if="restaurant.location_count" class="meta-dot">&middot;</span>
            <span v-if="restaurant.location_count" class="meta-item">{{ restaurant.location_count.toLocaleString() }} locations</span>
          </div>
        </div>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.restaurant-card {
  display: block;
  width: 260px;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  text-decoration: none;
  transition: all 200ms ease;
}

.restaurant-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
}

.restaurant-card.full-width {
  width: 100%;
}

.card-header {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 16px 24px;
}

.header-logo {
  max-height: 60px;
  max-width: 80%;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.9;
  position: relative;
  z-index: 1;
}

.logo-placeholder {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.9);
}

.card-body {
  padding: 12px;
}

.body-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.body-logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.body-logo.has-icon {
  padding: 0;
  border: none;
}

.body-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.body-logo.has-icon img {
  object-fit: cover;
}

.body-text {
  flex: 1;
  min-width: 0;
}

.restaurant-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.restaurant-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.meta-dot {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.full-width .card-header {
  height: 80px;
}

.full-width .header-logo {
  max-height: 48px;
}
</style>
