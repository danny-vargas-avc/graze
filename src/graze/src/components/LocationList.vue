<template>
  <div class="location-list">
    <div class="list-header">
      <h2 v-if="locations.length > 0">
        {{ total || locations.length }} location{{ (total || locations.length) !== 1 ? 's' : '' }}
        <span v-if="radius" class="radius-text">within {{ radius }} miles</span>
      </h2>
      <h2 v-else>Locations</h2>
    </div>

    <div v-if="loading" class="loading-state">
      <p>⏳ Loading locations...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>❌ {{ error.message || 'Failed to load locations' }}</p>
    </div>

    <div v-else-if="locations.length === 0" class="empty-state">
      <p>📍 No locations found nearby</p>
      <p class="empty-hint">Try adjusting your filters or search radius</p>
    </div>

    <div v-else class="list-content">
      <LocationCard
        v-for="location in locations"
        :key="location.id"
        :location="location"
        :highlighted="highlightedId === location.id"
        @click="handleLocationClick"
        @view-menu="handleViewMenu"
        @report-issue="handleReportIssue"
      />
    </div>

    <div v-if="hasMore && !loading" class="load-more">
      <LoadMoreButton @click="handleLoadMore" />
    </div>
  </div>
</template>

<script setup>
import LocationCard from './LocationCard.vue'
import LoadMoreButton from './LoadMoreButton.vue'

const props = defineProps({
  locations: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: null
  },
  radius: {
    type: Number,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: Object,
    default: null
  },
  hasMore: {
    type: Boolean,
    default: false
  },
  highlightedId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['location-click', 'view-menu', 'report-issue', 'load-more'])

const handleLocationClick = (location) => {
  emit('location-click', location)
}

const handleViewMenu = (location) => {
  emit('view-menu', location)
}

const handleReportIssue = (location) => {
  emit('report-issue', location)
}

const handleLoadMore = () => {
  emit('load-more')
}
</script>

<style scoped>
.location-list {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.list-header {
  padding: 16px;
  border-bottom: 1px solid #E2E8F0;
  background: white;
  position: sticky;
  top: 0;
  z-index: 10;
}

.list-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.radius-text {
  font-size: 14px;
  font-weight: 400;
  color: #64748B;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.loading-state,
.error-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
}

.loading-state p,
.error-state p,
.empty-state p {
  margin: 0;
  font-size: 16px;
  color: #64748B;
}

.empty-hint {
  margin-top: 8px !important;
  font-size: 14px !important;
  color: #94A3B8 !important;
}

.load-more {
  padding: 16px;
  border-top: 1px solid #E2E8F0;
  background: white;
}
</style>
