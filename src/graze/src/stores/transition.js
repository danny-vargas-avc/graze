/**
 * Transition store - passes visual state between landing and loading pages
 */
import { defineStore } from 'pinia'

export const useTransitionStore = defineStore('transition', {
  state: () => ({
    preset: null,
    palette: null,
    screenshotDataUrl: null,
  }),

  actions: {
    capture(preset, palette, screenshotDataUrl) {
      this.preset = preset
      this.palette = palette
      this.screenshotDataUrl = screenshotDataUrl
    },

    clear() {
      this.preset = null
      this.palette = null
      this.screenshotDataUrl = null
    },
  },
})
