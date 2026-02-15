import { defineStore } from 'pinia'
import apiClient from '../api/client'

const CACHE_KEY = 'graze_config'
const CACHE_TTL = 24 * 60 * 60 * 1000 // 24 hours

// Hardcoded fallback configuration matching current app
const FALLBACK_CONFIG = {
  filters: [
    {
      name: 'calories',
      display_name: 'Calories',
      filter_type: 'range',
      unit: '',
      options: [
        { label: 'Any', min: null, max: null },
        { label: '0-300', min: 0, max: 300 },
        { label: '300-500', min: 300, max: 500 },
        { label: '500-700', min: 500, max: 700 },
        { label: '700+', min: 700, max: null },
      ],
      order: 1
    },
    {
      name: 'protein',
      display_name: 'Protein',
      filter_type: 'range',
      unit: 'g',
      options: [
        { label: 'Any', min: null, max: null },
        { label: '0-20g', min: 0, max: 20 },
        { label: '20-40g', min: 20, max: 40 },
        { label: '40-60g', min: 40, max: 60 },
        { label: '60g+', min: 60, max: null },
      ],
      order: 2
    },
    {
      name: 'carbs',
      display_name: 'Carbs',
      filter_type: 'max_only',
      unit: 'g',
      options: [
        { label: 'Any', min: null, max: null },
        { label: '0-30g', min: null, max: 30 },
        { label: '30-60g', min: null, max: 60 },
        { label: '60-100g', min: null, max: 100 },
        { label: '100g+', min: null, max: null },
      ],
      order: 3
    },
    {
      name: 'fat',
      display_name: 'Fat',
      filter_type: 'range',
      unit: 'g',
      options: [
        { label: 'Any', min: null, max: null },
        { label: '0-15g', min: 0, max: 15 },
        { label: '15-30g', min: 15, max: 30 },
        { label: '30-50g', min: 30, max: 50 },
        { label: '50g+', min: 50, max: null },
      ],
      order: 4
    }
  ],
  quick_filters: [
    { id_key: 'nearby-5mi', label: 'Nearby 5 mi', filter_params: { radius: 5, sort: 'distance_asc' }, requires_location: true, order: 0 },
    { id_key: 'high-protein', label: 'High Protein 40g+', filter_params: { protein_min: 40 }, requires_location: false, order: 1 },
    { id_key: 'under-500', label: 'Under 500 cal', filter_params: { calories_max: 500 }, requires_location: false, order: 2 },
    { id_key: 'best-ratio', label: 'Best Ratio', filter_params: { sort: 'protein_ratio_desc' }, requires_location: false, order: 3 },
    { id_key: 'low-carb', label: 'Low Carb', filter_params: { carbs_max: 30 }, requires_location: false, order: 4 },
  ],
  sort_options: [
    { value: 'distance_asc', label: 'Nearest', requires_location: true, order: 0 },
    { value: 'protein_ratio_desc', label: 'Best Protein/Cal', requires_location: false, order: 1 },
    { value: 'protein_desc', label: 'Highest Protein', requires_location: false, order: 2 },
    { value: 'protein_asc', label: 'Lowest Protein', requires_location: false, order: 3 },
    { value: 'calories_asc', label: 'Lowest Calories', requires_location: false, order: 4 },
    { value: 'calories_desc', label: 'Highest Calories', requires_location: false, order: 5 },
    { value: 'carbs_asc', label: 'Lowest Carbs', requires_location: false, order: 6 },
    { value: 'fat_desc', label: 'Highest Fat', requires_location: false, order: 7 },
    { value: 'fat_asc', label: 'Lowest Fat', requires_location: false, order: 8 },
    { value: 'alpha_asc', label: 'A-Z', requires_location: false, order: 9 },
  ],
  app_settings: {
    default_map_center: [-74.0060, 40.7128], // NYC
    default_map_zoom: 12,
    items_per_page: 20,
    radius_options: [5, 10, 25, 50],
    default_sort: 'protein_ratio_desc',
    enable_geolocation: true,
    enable_distance_sort: true,
  },
  restaurant_colors: {
    'chipotle': '#A81612',
    'cava': '#F4A261',
    'sweetgreen': '#6DBF4B',
    'panera': '#5C8B3E',
    'chick-fil-a': '#E51937',
    'in-n-out': '#DA291C',
    'shake-shack': '#1F8143',
    'wingstop': '#024731',
    'raising-canes': '#CE1126',
    'mod-pizza': '#F05023',
    'sweetfin': '#00B4D8',
    'default': '#3B82F6'
  },
  restaurant_icons: {},
  version: 1
}

export const useConfigStore = defineStore('config', {
  state: () => ({
    filters: [],
    quickFilters: [],
    sortOptions: [],
    appSettings: null,
    restaurantColors: {},
    restaurantIcons: {},
    version: null,
    loading: false,
    error: null,
    lastFetched: null,
    usingFallback: false,
  }),

  getters: {
    /**
     * Get filter options by filter name (e.g., 'calories', 'protein')
     */
    getFilterOptions: (state) => (filterName) => {
      const filter = state.filters.find(f => f.name === filterName)
      return filter?.options || []
    },

    /**
     * Get restaurant brand color by slug with fallback
     */
    getRestaurantColor: (state) => (slug) => {
      return state.restaurantColors[slug] || state.restaurantColors.default || '#3B82F6'
    },

    /**
     * Get square icon URL for a restaurant (for small thumbnail contexts).
     * Returns null if no dedicated icon — caller should fall back to logo_url.
     */
    getRestaurantIcon: (state) => (slug) => {
      return state.restaurantIcons[slug] || null
    },

    /**
     * Check if config is loaded
     */
    isConfigLoaded: (state) => {
      return state.appSettings !== null
    },

    /**
     * Check if config needs refresh based on TTL
     */
    needsRefresh: (state) => {
      if (!state.lastFetched) return true
      const elapsed = Date.now() - state.lastFetched
      return elapsed > CACHE_TTL
    },

    /**
     * Get all active quick filters, optionally filtered by location requirement
     */
    getQuickFilters: (state) => (hasLocation = false) => {
      return state.quickFilters.filter(filter => {
        // Include non-location filters always
        // Include location filters only if hasLocation is true
        return !filter.requires_location || hasLocation
      })
    },

    /**
     * Get all active sort options, optionally filtered by location requirement
     */
    getSortOptions: (state) => (hasLocation = false) => {
      return state.sortOptions.filter(option => {
        return !option.requires_location || hasLocation
      })
    },
  },

  actions: {
    /**
     * Fetch configuration from backend API
     */
    async fetchConfig(force = false) {
      // Check if already loaded and not expired
      if (!force && this.isConfigLoaded && !this.needsRefresh) {
        return
      }

      // Try loading from cache first
      if (!force) {
        const cached = this.loadFromCache()
        if (cached) {
          console.log('Loaded config from cache')
          return
        }
      }

      this.loading = true
      this.error = null
      this.usingFallback = false

      try {
        const response = await apiClient.get('/config/all/')
        const data = response.data

        this.filters = data.filters || []
        this.quickFilters = data.quick_filters || []
        this.sortOptions = data.sort_options || []
        this.appSettings = data.app_settings || {}
        this.restaurantColors = data.restaurant_colors || {}
        this.restaurantIcons = data.restaurant_icons || FALLBACK_CONFIG.restaurant_icons
        this.version = data.version || 1
        this.lastFetched = Date.now()

        // Save to cache
        this.saveToCache()
        console.log('Config loaded from API')
      } catch (error) {
        this.error = error
        console.warn('Failed to fetch config from API, using fallback:', error)

        // Try to use cached data as fallback
        const cached = this.loadFromCache()
        if (!cached) {
          // Use hardcoded fallbacks as last resort
          this.useFallbacks()
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * Save current config to localStorage cache
     */
    saveToCache() {
      try {
        const cache = {
          filters: this.filters,
          quickFilters: this.quickFilters,
          sortOptions: this.sortOptions,
          appSettings: this.appSettings,
          restaurantColors: this.restaurantColors,
          restaurantIcons: this.restaurantIcons,
          version: this.version,
          lastFetched: this.lastFetched,
        }
        localStorage.setItem(CACHE_KEY, JSON.stringify(cache))
      } catch (error) {
        console.error('Failed to save config to cache:', error)
      }
    },

    /**
     * Load config from localStorage cache
     * Returns true if successful, false otherwise
     */
    loadFromCache() {
      try {
        const cached = localStorage.getItem(CACHE_KEY)
        if (!cached) return false

        const data = JSON.parse(cached)

        // Check if cache is still valid (TTL)
        const elapsed = Date.now() - data.lastFetched
        if (elapsed > CACHE_TTL) {
          console.log('Cache expired')
          return false
        }

        // Check version mismatch
        if (this.version && data.version !== this.version) {
          console.log('Cache version mismatch')
          return false
        }

        this.filters = data.filters
        this.quickFilters = data.quickFilters
        this.sortOptions = data.sortOptions
        this.appSettings = data.appSettings
        this.restaurantColors = data.restaurantColors
        this.restaurantIcons = data.restaurantIcons || FALLBACK_CONFIG.restaurant_icons
        this.version = data.version
        this.lastFetched = data.lastFetched

        return true
      } catch (error) {
        console.error('Failed to load cache:', error)
        return false
      }
    },

    /**
     * Clear localStorage cache
     */
    clearCache() {
      localStorage.removeItem(CACHE_KEY)
      this.lastFetched = null
    },

    /**
     * Use hardcoded fallback configuration
     */
    useFallbacks() {
      this.filters = FALLBACK_CONFIG.filters
      this.quickFilters = FALLBACK_CONFIG.quick_filters
      this.sortOptions = FALLBACK_CONFIG.sort_options
      this.appSettings = FALLBACK_CONFIG.app_settings
      this.restaurantColors = FALLBACK_CONFIG.restaurant_colors
      this.restaurantIcons = FALLBACK_CONFIG.restaurant_icons
      this.version = FALLBACK_CONFIG.version
      this.usingFallback = true
      console.log('Using fallback configuration')
    },

    /**
     * Force refresh configuration from API
     */
    async refreshConfig() {
      this.clearCache()
      await this.fetchConfig(true)
    },

    /**
     * Get quick filter by ID
     */
    getQuickFilterById(id) {
      return this.quickFilters.find(f => f.id_key === id)
    },

    /**
     * Get sort option by value
     */
    getSortOptionByValue(value) {
      return this.sortOptions.find(o => o.value === value)
    },

    /**
     * Check for config version updates
     * Returns true if a new version is available
     */
    async checkForUpdates() {
      try {
        const response = await apiClient.get('/config/all/')
        const newVersion = response.data.version

        // If version changed, we need to refresh
        if (this.version && newVersion !== this.version) {
          console.log(`Config version updated: ${this.version} → ${newVersion}`)
          return true
        }

        return false
      } catch (error) {
        console.error('Failed to check for config updates:', error)
        return false
      }
    },

    /**
     * Invalidate cache and force refresh
     * Useful for admin-triggered updates
     */
    async invalidateCache() {
      console.log('Invalidating config cache...')
      this.clearCache()
      await this.fetchConfig(true)
    },
  },
})
