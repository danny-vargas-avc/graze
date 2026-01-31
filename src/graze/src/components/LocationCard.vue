<template>
  <div class="location-card" @click="handleClick" :class="{ 'highlighted': highlighted }">
    <div class="card-header">
      <div class="restaurant-info">
        <img
          v-if="location.restaurant.logo_url"
          :src="location.restaurant.logo_url"
          :alt="location.restaurant.name"
          class="restaurant-logo"
        />
        <div class="text-info">
          <h3 class="location-name">{{ location.name }}</h3>
          <p class="restaurant-name">{{ location.restaurant.name }}</p>
        </div>
      </div>
      <div v-if="distance" class="distance">
        {{ distance }} mi
      </div>
    </div>

    <div class="card-body">
      <div class="address">
        <p v-if="location.address" class="address-line">{{ location.address }}</p>
        <p class="city-state">
          <span v-if="location.city">{{ location.city }}</span><span v-if="location.city && location.state">, </span><span v-if="location.state">{{ location.state }}</span>
          <span v-if="location.postcode"> {{ location.postcode }}</span>
        </p>
      </div>

      <div v-if="location.phone" class="phone">
        📞 {{ location.phone }}
      </div>
    </div>

    <div class="card-actions">
      <button class="action-button primary" @click.stop="viewMenu">
        View Menu
      </button>
      <button class="action-button secondary" @click.stop="reportIssue">
        Report Issue
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  location: {
    type: Object,
    required: true
  },
  highlighted: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'view-menu', 'report-issue'])

const distance = computed(() => {
  if (!props.location.distance_miles) return null
  const dist = parseFloat(props.location.distance_miles)
  return dist.toFixed(1)
})

const handleClick = () => {
  emit('click', props.location)
}

const viewMenu = () => {
  emit('view-menu', props.location)
}

const reportIssue = () => {
  emit('report-issue', props.location)
}
</script>

<style scoped>
.location-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.location-card.highlighted {
  border-color: var(--color-primary);
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.restaurant-info {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.restaurant-logo {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.text-info {
  flex: 1;
}

.location-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.restaurant-name {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.distance {
  background: var(--color-surface);
  color: var(--color-clickable);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  border: 1px solid var(--color-border);
}

.card-body {
  margin-bottom: 12px;
}

.address {
  margin-bottom: 8px;
}

.address-line {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-primary);
}

.city-state {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.phone {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-button {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button.primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: white;
  box-shadow: var(--shadow-sm);
}

.action-button.primary:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.action-button.secondary {
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.action-button.secondary:hover {
  background: var(--color-surface-elevated);
  color: var(--color-text-primary);
  border-color: var(--color-border-hover);
}
</style>
