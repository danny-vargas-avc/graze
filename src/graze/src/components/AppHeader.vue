<script setup>
import { RouterLink } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
import GeolocationButton from './GeolocationButton.vue'
</script>

<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Logo -->
      <RouterLink to="/home" class="logo">
        <span class="logo-text">Graze</span>
      </RouterLink>

      <!-- Desktop nav links -->
      <nav class="desktop-nav" aria-label="Desktop navigation">
        <RouterLink to="/home" class="nav-link" active-class="nav-link-active">Home</RouterLink>
        <RouterLink to="/map" class="nav-link" active-class="nav-link-active">Map</RouterLink>
        <RouterLink to="/favorites" class="nav-link" active-class="nav-link-active">Favorites</RouterLink>
      </nav>

      <!-- Actions -->
      <div class="header-actions">
        <GeolocationButton />
        <ThemeToggle />
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background-color: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
}

/* Desktop navigation */
.desktop-nav {
  display: none;
  gap: 4px;
}

.nav-link {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 150ms ease;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background-color: var(--color-surface);
}

.nav-link-active {
  color: var(--color-primary);
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (min-width: 769px) {
  .desktop-nav {
    display: flex;
  }
}
</style>
