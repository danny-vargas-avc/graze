import { defineStore } from 'pinia'
import { getDishes } from '../api/dishes'
import { useLocationsStore } from './locations'
import { useConfigStore } from './config'

export const useDishesStore = defineStore('dishes', {
  state: () => {
    const configStore = useConfigStore()
    return {
      dishes: [],
      total: 0,
      loading: false,
      error: null,

      // Request cancellation
      abortController: null,

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

      // Sorting - use config default
      sort: configStore.appSettings?.default_sort || 'protein_ratio_desc',

      // Pagination - use config default
      limit: configStore.appSettings?.items_per_page || 20,
      offset: 0,
      hasMore: false,
    }
  },

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
      // Cancel any pending request
      if (this.abortController) {
        this.abortController.abort()
      }

      // Create new abort controller for this request
      this.abortController = new AbortController()

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
        const response = await getDishes(params, this.abortController.signal)

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
        // Don't set error state if request was aborted
        if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
          this.error = error
        }
      } finally {
        this.loading = false
        this.abortController = null
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
      const configStore = useConfigStore()
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
      this.sort = configStore.appSettings?.default_sort || 'protein_ratio_desc'
      this.fetchDishes()
    },

    // Apply quick filter presets from config
    applyQuickFilter(presetId) {
      const configStore = useConfigStore()
      this.clearFilters()

      // Get filter configuration from config store
      const filterConfig = configStore.getQuickFilterById(presetId)
      if (!filterConfig) {
        console.warn(`Quick filter '${presetId}' not found in config`)
        this.fetchDishes()
        return
      }

      // Apply filter parameters from config
      const params = filterConfig.filter_params
      if (params.protein_min !== undefined) this.proteinMin = params.protein_min
      if (params.protein_max !== undefined) this.proteinMax = params.protein_max
      if (params.calories_min !== undefined) this.caloriesMin = params.calories_min
      if (params.calories_max !== undefined) this.caloriesMax = params.calories_max
      if (params.carbs_min !== undefined) this.carbsMin = params.carbs_min
      if (params.carbs_max !== undefined) this.carbsMax = params.carbs_max
      if (params.fat_min !== undefined) this.fatMin = params.fat_min
      if (params.fat_max !== undefined) this.fatMax = params.fat_max
      if (params.sort !== undefined) this.sort = params.sort

      // Handle radius/location filters
      if (params.radius !== undefined && this.userLocation) {
        this.radiusMiles = params.radius
        if (params.sort) this.sort = params.sort
      }

      this.fetchDishes()
    },
  },
})
