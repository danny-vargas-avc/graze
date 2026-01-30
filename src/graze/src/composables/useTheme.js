import { ref, watchEffect } from 'vue'

const isDark = ref(false)
const THEME_KEY = 'graze-theme'

// Initialize theme from localStorage or system preference
function initTheme() {
  const stored = localStorage.getItem(THEME_KEY)

  if (stored) {
    isDark.value = stored === 'dark'
  } else {
    // Check system preference
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  applyTheme()
}

// Apply theme to document
function applyTheme() {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// Toggle theme
function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
  applyTheme()
}

// Set specific theme
function setTheme(theme) {
  isDark.value = theme === 'dark'
  localStorage.setItem(THEME_KEY, theme)
  applyTheme()
}

// Initialize on first import
if (typeof window !== 'undefined') {
  initTheme()

  // Watch for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(THEME_KEY)) {
      isDark.value = e.matches
      applyTheme()
    }
  })
}

export function useTheme() {
  return {
    isDark,
    toggleTheme,
    setTheme
  }
}
