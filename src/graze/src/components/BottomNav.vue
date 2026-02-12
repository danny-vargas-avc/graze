<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = computed(() => {
  if (route.path.startsWith('/home')) return 'home'
  if (route.path.startsWith('/map')) return 'map'
  if (route.path.startsWith('/favorites')) return 'favorites'
  if (route.path.startsWith('/profile')) return 'profile'
  return 'home'
})
</script>

<template>
  <nav class="bottom-nav" aria-label="Main navigation">
    <RouterLink to="/home" class="nav-tab" :class="{ active: activeTab === 'home' }">
      <!-- Home: outline -->
      <svg v-if="activeTab !== 'home'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
      <!-- Home: filled -->
      <svg v-else class="nav-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 11-1.06 1.06l-.97-.97V19.5a1.5 1.5 0 01-1.5 1.5h-2.25a1.5 1.5 0 01-1.5-1.5v-3.75a.75.75 0 00-.75-.75h-1.5a.75.75 0 00-.75.75v3.75a1.5 1.5 0 01-1.5 1.5H7.5a1.5 1.5 0 01-1.5-1.5v-6.88l-.97.97a.75.75 0 01-1.06-1.06l8.69-8.69z" />
      </svg>
      <span class="nav-label">Home</span>
    </RouterLink>

    <RouterLink to="/map" class="nav-tab" :class="{ active: activeTab === 'map' }">
      <!-- Map: outline -->
      <svg v-if="activeTab !== 'map'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
      </svg>
      <!-- Map: filled -->
      <svg v-else class="nav-icon" viewBox="0 0 24 24" fill="currentColor">
        <path fill-rule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
      </svg>
      <span class="nav-label">Map</span>
    </RouterLink>

    <RouterLink to="/favorites" class="nav-tab" :class="{ active: activeTab === 'favorites' }">
      <!-- Heart: outline -->
      <svg v-if="activeTab !== 'favorites'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
      </svg>
      <!-- Heart: filled -->
      <svg v-else class="nav-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
      </svg>
      <span class="nav-label">Favorites</span>
    </RouterLink>

    <RouterLink to="/profile" class="nav-tab" :class="{ active: activeTab === 'profile' }">
      <!-- Profile: outline -->
      <svg v-if="activeTab !== 'profile'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
      </svg>
      <!-- Profile: filled -->
      <svg v-else class="nav-icon" viewBox="0 0 24 24" fill="currentColor">
        <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clip-rule="evenodd" />
      </svg>
      <span class="nav-label">Profile</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  background-color: var(--color-surface-elevated);
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
  padding: 4px 0;
  padding-bottom: calc(4px + env(safe-area-inset-bottom));
  z-index: 100;
}

.nav-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 6px 0;
  text-decoration: none;
  color: #9ca3af;
  transition: color 150ms ease;
}

.nav-tab.active {
  color: var(--color-primary);
}

.nav-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.nav-label {
  font-size: 11px;
  font-weight: 500;
  line-height: 1;
}

/* Hide on desktop */
@media (min-width: 769px) {
  .bottom-nav {
    display: none;
  }
}
</style>
