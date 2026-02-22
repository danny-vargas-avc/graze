<script setup>
import { computed, inject } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const showSettings = inject('showSettings')

const isHome = computed(() => route.meta.headerMode === 'home')
const pageTitle = computed(() => route.meta.title || '')

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/home')
  }
}
</script>

<template>
  <header class="app-header">
    <div class="header-content">
      <!-- HOME MODE -->
      <template v-if="isHome">
        <RouterLink to="/home" class="logo">
          <span class="logo-text">Graze</span>
        </RouterLink>

        <!-- Desktop nav -->
        <nav class="desktop-nav" aria-label="Navigation">
          <RouterLink to="/home" class="nav-link" active-class="nav-link-active">Home</RouterLink>
          <button class="nav-link" @click="showSettings = true">Settings</button>
        </nav>

        <!-- Mobile nav icons -->
        <div class="mobile-nav">
          <button class="nav-icon-btn" aria-label="Settings" @click="showSettings = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </template>

      <!-- BACK MODE -->
      <template v-else>
        <div class="back-left">
          <button class="back-btn" @click="goBack" aria-label="Go back">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span v-if="pageTitle" class="page-title">{{ pageTitle }}</span>
        </div>

        <!-- Desktop nav (still visible on wide screens) -->
        <nav class="desktop-nav" aria-label="Navigation">
          <RouterLink to="/home" class="nav-link" active-class="nav-link-active">Home</RouterLink>
          <button class="nav-link" @click="showSettings = true">Settings</button>
        </nav>

        <div class="back-right"></div>
      </template>
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

/* Logo */
.logo {
  text-decoration: none;
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
}

/* Desktop nav */
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
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background-color: var(--color-surface);
}

.nav-link-active {
  color: var(--color-primary);
  font-weight: 600;
}

/* Mobile nav icons */
.mobile-nav {
  display: flex;
  align-items: center;
  gap: 2px;
}

.nav-icon-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 150ms ease;
}

.nav-icon-btn:hover {
  color: var(--color-text-primary);
  background-color: var(--color-surface);
}

.nav-icon-btn svg {
  width: 22px;
  height: 22px;
}

/* Back mode */
.back-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--color-surface);
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: background 150ms ease;
}

.back-btn:hover {
  background: var(--color-border);
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.page-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.back-right {
  width: 36px;
}

/* Responsive */
@media (min-width: 1024px) {
  .desktop-nav {
    display: flex;
  }

  .mobile-nav {
    display: none;
  }

  .back-btn {
    display: none;
  }

  .back-right {
    display: none;
  }
}
</style>
