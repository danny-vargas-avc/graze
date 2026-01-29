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
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-card:hover {
  border-color: #3B82F6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.location-card.highlighted {
  border-color: #3B82F6;
  background: #EFF6FF;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
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
  color: #1E293B;
  line-height: 1.4;
}

.restaurant-name {
  margin: 4px 0 0;
  font-size: 14px;
  color: #64748B;
}

.distance {
  background: #EFF6FF;
  color: #3B82F6;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
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
  color: #475569;
}

.city-state {
  margin: 4px 0 0;
  font-size: 14px;
  color: #64748B;
}

.phone {
  font-size: 14px;
  color: #64748B;
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
  background: #3B82F6;
  color: white;
}

.action-button.primary:hover {
  background: #2563EB;
}

.action-button.secondary {
  background: #F1F5F9;
  color: #64748B;
}

.action-button.secondary:hover {
  background: #E2E8F0;
  color: #475569;
}
</style>
