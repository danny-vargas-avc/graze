import { defineStore } from 'pinia'
import { getDishes } from '../api/dishes'
import { useLocationsStore } from './locations'

export const useDishesStore = defineStore('dishes', {
  state: () => ({
    dishes: [],
    total: 0,
    loading: false,
    error: null,

    // Filters
    search: '',
    caloriesMin: null,
    caloriesMax: null,
    proteinMin: null,
    proteinMax: null,
    carbsMax: null,
    fatMin: null,
    fatMax: null,
    selectedRestaurants: [],
    category: null,

    // Location
    userLocation: null, // { lat, lng }
    radiusMiles: null, // for "nearby" filter

    // Sorting
    sort: 'protein_ratio_desc',

    // Pagination
    limit: 20,
    offset: 0,
    hasMore: false,
  }),

  getters: {
    activeFilterCount: (state) => {
      let count = 0
      if (state.caloriesMin || state.caloriesMax) count++
      if (state.proteinMin || state.proteinMax) count++
      if (state.carbsMax) count++
      if (state.fatMin || state.fatMax) count++
      if (state.selectedRestaurants.length > 0) count++
      if (state.radiusMiles) count++
      return count
    },
  },

  actions: {
    async fetchDishes(append = false) {
      this.loading = true
      this.error = null

      const params = {
        limit: this.limit,
        offset: append ? this.offset : 0,
        sort: this.sort,
      }

      if (this.search) params.search = this.search
      if (this.caloriesMin) params.calories_min = this.caloriesMin
      if (this.caloriesMax) params.calories_max = this.caloriesMax
      if (this.proteinMin) params.protein_min = this.proteinMin
      if (this.proteinMax) params.protein_max = this.proteinMax
      if (this.carbsMax) params.carbs_max = this.carbsMax
      if (this.fatMin) params.fat_min = this.fatMin
      if (this.fatMax) params.fat_max = this.fatMax
      if (this.selectedRestaurants.length > 0) {
        params.restaurants = this.selectedRestaurants.join(',')
      }
      if (this.category) params.category = this.category

      // Include user location if available (for future distance-based features)
      if (this.userLocation) {
        params.lat = this.userLocation.lat
        params.lng = this.userLocation.lng
      }
      // Include radius filter if set
      if (this.radiusMiles) {
        params.radius = this.radiusMiles
      }

      try {
        const response = await getDishes(params)

        if (append) {
          this.dishes = [...this.dishes, ...response.data]
        } else {
          this.dishes = response.data
          this.offset = 0
        }

        this.total = response.meta.total
        this.hasMore = response.meta.has_more
        this.offset = response.meta.offset + response.meta.limit
      } catch (error) {
        this.error = error
      } finally {
        this.loading = false
      }
    },

    async loadMore() {
      if (this.hasMore && !this.loading) {
        await this.fetchDishes(true)
      }
    },

    setSearch(value) {
      this.search = value
      this.fetchDishes()
    },

    setCaloriesFilter(min, max) {
      this.caloriesMin = min
      this.caloriesMax = max
      this.fetchDishes()
    },

    setProteinFilter(min, max) {
      this.proteinMin = min
      this.proteinMax = max
      this.fetchDishes()
    },

    setCarbsFilter(max) {
      this.carbsMax = max
      this.fetchDishes()
    },

    setFatFilter(min, max) {
      this.fatMin = min
      this.fatMax = max
      this.fetchDishes()
    },

    setRestaurants(slugs) {
      this.selectedRestaurants = slugs
      this.fetchDishes()
    },

    toggleRestaurant(slug) {
      const index = this.selectedRestaurants.indexOf(slug)
      if (index > -1) {
        this.selectedRestaurants.splice(index, 1)
      } else {
        this.selectedRestaurants.push(slug)
      }
      this.fetchDishes()
    },

    setSort(sort) {
      this.sort = sort
      this.fetchDishes()
    },

    // Set user location from locations store
    setUserLocation(lat, lng) {
      if (lat && lng) {
        this.userLocation = { lat, lng }
      } else {
        this.userLocation = null
      }
      this.fetchDishes()
    },

    // Set radius filter for "nearby" searches
    setRadius(miles) {
      this.radiusMiles = miles
      this.fetchDishes()
    },

    clearFilters() {
      this.search = ''
      this.caloriesMin = null
      this.caloriesMax = null
      this.proteinMin = null
      this.proteinMax = null
      this.carbsMax = null
      this.fatMin = null
      this.fatMax = null
      this.selectedRestaurants = []
      this.category = null
      this.radiusMiles = null
      this.sort = 'protein_ratio_desc'
      this.fetchDishes()
    },

    // Apply quick filter presets
    applyQuickFilter(preset) {
      this.clearFilters()

      switch (preset) {
        case 'high-protein':
          this.proteinMin = 40
          break
        case 'under-500':
          this.caloriesMax = 500
          break
        case 'best-ratio':
          this.sort = 'protein_ratio_desc'
          break
        case 'low-carb':
          this.carbsMax = 30
          break
        case 'nearby-5mi':
          // Only apply if user location is set
          if (this.userLocation) {
            this.radiusMiles = 5
            this.sort = 'distance_asc'
          }
          break
      }

      this.fetchDishes()
    },
  },
})
