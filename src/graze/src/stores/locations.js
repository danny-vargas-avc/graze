import { defineStore } from 'pinia'
import { getLocations } from '../api/locations'

export const useLocationsStore = defineStore('locations', {
  state: () => ({
    locations: [],
    total: 0,
    loading: false,
    error: null,

    // User location
    userLocation: null, // { lat, lng }

    // Map bounds
    mapBounds: null, // { swLat, swLng, neLat, neLng }

    // Filters
    selectedRestaurants: [],
    radius: 25, // miles

    // Limits
    limit: 100,
  }),

  getters: {
    hasUserLocation: (state) => state.userLocation !== null,

    boundingBox: (state) => {
      if (!state.mapBounds) return null
      return `${state.mapBounds.swLat},${state.mapBounds.swLng},${state.mapBounds.neLat},${state.mapBounds.neLng}`
    },
  },

  actions: {
    async fetchLocations(options = {}) {
      this.loading = true
      this.error = null

      const params = {
        limit: options.limit || this.limit,
      }

      // Use bbox if provided, otherwise use user location + radius
      if (options.bbox) {
        params.bbox = options.bbox
      } else if (this.mapBounds) {
        params.bbox = this.boundingBox
      } else if (this.userLocation) {
        params.lat = this.userLocation.lat
        params.lng = this.userLocation.lng
        params.radius = this.radius
      }

      // Filter by restaurants
      const restaurants = options.restaurants || this.selectedRestaurants
      if (restaurants.length > 0) {
        params.restaurants = restaurants.join(',')
      }

      try {
        const response = await getLocations(params)
        this.locations = response.data
        this.total = response.meta.total
      } catch (error) {
        this.error = error
        this.locations = []
      } finally {
        this.loading = false
      }
    },

    setUserLocation(lat, lng) {
      this.userLocation = { lat, lng }
    },

    clearUserLocation() {
      this.userLocation = null
    },

    setMapBounds(bounds) {
      this.mapBounds = {
        swLat: bounds.swLat,
        swLng: bounds.swLng,
        neLat: bounds.neLat,
        neLng: bounds.neLng,
      }
    },

    clearMapBounds() {
      this.mapBounds = null
    },

    setRestaurants(slugs) {
      this.selectedRestaurants = slugs
      this.fetchLocations()
    },

    toggleRestaurant(slug) {
      const index = this.selectedRestaurants.indexOf(slug)
      if (index > -1) {
        this.selectedRestaurants.splice(index, 1)
      } else {
        this.selectedRestaurants.push(slug)
      }
      this.fetchLocations()
    },

    setRadius(miles) {
      this.radius = miles
      if (this.userLocation) {
        this.fetchLocations()
      }
    },

    async requestUserLocation() {
      this.loading = true
      this.error = null

      return new Promise((resolve, reject) => {
        if (!('geolocation' in navigator)) {
          this.error = { message: 'Geolocation is not supported by your browser' }
          this.loading = false
          reject(this.error)
          return
        }

        navigator.geolocation.getCurrentPosition(
          (position) => {
            this.setUserLocation(
              position.coords.latitude,
              position.coords.longitude
            )
            this.loading = false
            resolve(this.userLocation)
          },
          (error) => {
            let errorMessage = 'Unable to get your location'

            switch (error.code) {
              case error.PERMISSION_DENIED:
                errorMessage = 'Location permission denied'
                break
              case error.POSITION_UNAVAILABLE:
                errorMessage = 'Location information unavailable'
                break
              case error.TIMEOUT:
                errorMessage = 'Location request timed out'
                break
            }

            this.error = { message: errorMessage }
            this.loading = false
            reject(this.error)
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
          }
        )
      })
    },
  },
})
