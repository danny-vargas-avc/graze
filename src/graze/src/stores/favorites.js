import { defineStore } from 'pinia'
import { getDish } from '../api/dishes'

const STORAGE_KEY = 'graze_favorites'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    favoriteIds: JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'),
    favoriteDishes: [],
    loading: false,
  }),

  actions: {
    toggle(dishId) {
      const index = this.favoriteIds.indexOf(dishId)
      if (index > -1) {
        this.favoriteIds.splice(index, 1)
        this.favoriteDishes = this.favoriteDishes.filter(d => d.id !== dishId)
      } else {
        this.favoriteIds.push(dishId)
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.favoriteIds))
    },

    isFavorite(dishId) {
      return this.favoriteIds.includes(dishId)
    },

    async loadFavorites() {
      if (this.favoriteIds.length === 0) {
        this.favoriteDishes = []
        return
      }

      this.loading = true
      try {
        const dishes = await Promise.all(
          this.favoriteIds.map(id => getDish(id).catch(() => null))
        )
        this.favoriteDishes = dishes.filter(Boolean)
      } catch (e) {
        console.error('Failed to load favorites:', e)
      } finally {
        this.loading = false
      }
    },
  },
})
