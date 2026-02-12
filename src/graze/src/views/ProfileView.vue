<script setup>
import ThemeToggle from '../components/ThemeToggle.vue'
import GeolocationButton from '../components/GeolocationButton.vue'
</script>

<template>
  <div class="profile-view">
    <div class="profile-header">
      <h1 class="page-title">Profile</h1>
    </div>

    <div class="profile-content">
      <!-- Appearance -->
      <section class="settings-section">
        <h2 class="section-title">Appearance</h2>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Dark Mode</span>
            <span class="setting-desc">Toggle between light and dark theme</span>
          </div>
          <ThemeToggle />
        </div>
      </section>

      <!-- Location -->
      <section class="settings-section">
        <h2 class="section-title">Location</h2>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Your Location</span>
            <span class="setting-desc">Enable location for nearby restaurants</span>
          </div>
          <GeolocationButton />
        </div>
      </section>

      <!-- About -->
      <section class="settings-section">
        <h2 class="section-title">About</h2>
        <div class="about-info">
          <p class="about-text">Graze helps you find the highest-protein meals at your favorite restaurants.</p>
          <p class="about-text">7 restaurants &middot; 204 menu items &middot; 4,155 locations</p>
          <p class="about-text version">v1.0.0</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  height: 100%;
  overflow-y: auto;
}

.profile-header {
  padding: 20px 16px 12px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.profile-content {
  padding: 0 16px 24px;
}

.settings-section {
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

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 12px;
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

.about-info {
  padding: 14px 16px;
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.about-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.about-text.version {
  margin-top: 8px;
  color: var(--color-text-tertiary);
  font-size: 12px;
}
</style>
