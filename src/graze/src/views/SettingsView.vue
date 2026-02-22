<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRestaurantsStore } from '../stores/restaurants'
import ThemeToggle from '../components/ThemeToggle.vue'
import GeolocationButton from '../components/GeolocationButton.vue'

const emit = defineEmits(['close'])

const restaurantsStore = useRestaurantsStore()
const { restaurants, stats } = storeToRefs(restaurantsStore)

onMounted(() => {
  restaurantsStore.fetchRestaurants()
  restaurantsStore.fetchStats()
})
</script>

<template>
  <div class="settings-overlay" @click.self="emit('close')">
    <div class="settings-modal">
      <!-- Header -->
      <div class="modal-header">
        <h2 class="modal-title">Settings</h2>
        <button class="close-btn" @click="emit('close')" aria-label="Close settings">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="modal-content">
        <!-- Stats -->
        <section class="stats-grid" v-if="restaurants.length || stats">
          <div class="stat-card">
            <span class="stat-value">{{ restaurants.length }}</span>
            <span class="stat-label">Restaurants</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ stats?.total_dishes ?? '...' }}</span>
            <span class="stat-label">Menu Items</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ stats?.total_locations?.toLocaleString() ?? '...' }}</span>
            <span class="stat-label">Locations</span>
          </div>
        </section>

        <!-- What is Graze -->
        <section class="info-section">
          <h3 class="section-title">What is Graze?</h3>
          <div class="info-card">
            <p class="info-text">Graze aggregates nutrition data from fast-casual restaurants so you can compare protein, calories, and macros across menus — all in one place.</p>
            <p class="info-text">Search by dish, filter by macros, or explore the map to find high-protein options near you.</p>
          </div>
        </section>

        <!-- Settings -->
        <section class="info-section">
          <h3 class="section-title">Preferences</h3>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Dark Mode</span>
              <span class="setting-desc">Toggle between light and dark theme</span>
            </div>
            <ThemeToggle />
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Your Location</span>
              <span class="setting-desc">Enable location for nearby restaurants</span>
            </div>
            <GeolocationButton />
          </div>
        </section>

        <!-- Footer -->
        <div class="modal-footer">
          <p class="footer-text">Built for protein lovers.</p>
          <p class="footer-version">v1.0.0</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.settings-modal {
  width: 100%;
  max-width: 480px;
  max-height: 85dvh;
  background-color: var(--color-surface-elevated);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 12px;
  flex-shrink: 0;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background-color: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.close-btn:hover {
  background-color: var(--color-border);
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px calc(16px + env(safe-area-inset-bottom));
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 8px;
  background-color: var(--color-surface);
  border-radius: 12px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
}

/* Info sections */
.info-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.info-card {
  padding: 14px 16px;
  background-color: var(--color-surface);
  border-radius: 12px;
}

.info-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 8px;
}

.info-text:last-child {
  margin-bottom: 0;
}

/* Settings */
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background-color: var(--color-surface);
  border-radius: 12px;
  margin-bottom: 8px;
}

.setting-row:last-child {
  margin-bottom: 0;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.setting-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
}

/* Footer */
.modal-footer {
  text-align: center;
  padding: 24px 0 8px;
}

.footer-text {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.footer-version {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 4px;
  opacity: 0.6;
}

</style>
