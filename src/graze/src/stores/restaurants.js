import { defineStore } from 'pinia'
import { getRestaurants, getStats } from '../api/restaurants'

export const useRestaurantsStore = defineStore('restaurants', {
  state: () => ({
    restaurants: [],
    stats: null,
    loading: false,
    error: null,
  }),

  getters: {
    getBySlug: (state) => (slug) => {
      return state.restaurants.find(r => r.slug === slug)
    },
  },

  actions: {
    async fetchRestaurants() {
      if (this.restaurants.length > 0) return // Already loaded

      this.loading = true
      this.error = null

      try {
        this.restaurants = await getRestaurants()
      } catch (error) {
        this.error = error
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        this.stats = await getStats()
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    },
  },
})
