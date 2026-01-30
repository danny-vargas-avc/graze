<template>
  <div class="map-wrapper">
    <!-- Loading spinner -->
    <Transition name="fade">
      <div v-if="isLoading" class="map-loading">
        <div class="spinner-container">
          <svg class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="loading-text">Loading map...</p>
        </div>
      </div>
    </Transition>
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'
import Supercluster from 'supercluster'
import 'mapbox-gl/dist/mapbox-gl.css'

const props = defineProps({
  center: {
    type: Array,
    default: () => [-74.0060, 40.7128] // New York City [lng, lat]
  },
  zoom: {
    type: Number,
    default: 10
  },
  locations: {
    type: Array,
    default: () => []
  },
  userLocation: {
    type: Object,
    default: null // { lat, lng }
  },
  highlightedRestaurantSlug: {
    type: String,
    default: null
  },
  dishes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['move', 'load', 'marker-click', 'bounds-change', 'dish-click', 'view-all-dishes'])

const mapContainer = ref(null)
const isLoading = ref(true)
let map = null
let clusterIndex = null
let boundsChangeTimeout = null
let currentPopup = null

// Restaurant color mapping
const restaurantColors = {
  'chipotle': '#A81612',
  'cava': '#F4A261',
  'sweetgreen': '#6DBF4B',
  'panera': '#5C8B3E',
  'chick-fil-a': '#E51937',
  'default': '#3B82F6'
}

// Initialize Supercluster
const initCluster = () => {
  clusterIndex = new Supercluster({
    radius: 60,
    maxZoom: 14,
    minZoom: 0,
    minPoints: 2
  })
}

// Convert locations to GeoJSON
const createGeoJSON = (locations) => {
  return {
    type: 'FeatureCollection',
    features: locations.map(location => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [location.longitude, location.latitude]
      },
      properties: {
        id: location.id,
        name: location.name,
        restaurant: location.restaurant,
        restaurantSlug: location.restaurant?.slug || 'default',
        color: restaurantColors[location.restaurant?.slug] || restaurantColors.default
      }
    }))
  }
}

// Load locations into cluster index
const loadClusters = () => {
  if (!clusterIndex || !props.locations || props.locations.length === 0) return

  const geojson = createGeoJSON(props.locations)
  clusterIndex.load(geojson.features)
}

// Get clusters for current map view
const getClusters = () => {
  if (!map || !clusterIndex) return []

  const bounds = map.getBounds()
  const zoom = map.getZoom()

  return clusterIndex.getClusters(
    [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()],
    Math.floor(zoom)
  )
}

// Create popup HTML content for a location
const createPopupContent = (location) => {
  // Find dishes for this location's restaurant
  const locationDishes = props.dishes.filter(dish =>
    dish.restaurant?.slug === location.restaurant.slug
  )

  // Limit to first 3 dishes
  const displayDishes = locationDishes.slice(0, 3)

  let dishesHTML = ''
  if (displayDishes.length > 0) {
    dishesHTML = displayDishes.map(dish => `
      <div class="popup-dish">
        <div class="dish-info">
          <h4 class="dish-name">${dish.name}</h4>
          <p class="dish-macros">${dish.calories} cal · ${dish.protein}g protein</p>
        </div>
        <button class="see-more-button" data-dish-id="${dish.id}">See more</button>
      </div>
    `).join('')
  } else {
    dishesHTML = '<p class="no-dishes">No dishes available</p>'
  }

  const totalCount = locationDishes.length
  const viewAllButton = totalCount > 3 ? `
    <button class="view-all-button" data-restaurant-slug="${location.restaurant.slug}">
      View all ${totalCount} dishes
    </button>
  ` : ''

  return `
    <div class="map-popup">
      <h3 class="popup-restaurant-name">${location.restaurant.name}</h3>
      <p class="popup-address">${location.name}</p>
      <div class="popup-dishes">
        ${dishesHTML}
      </div>
      ${viewAllButton}
    </div>
  `
}

// Show popup for a location
const showPopup = (location, coordinates) => {
  // Close existing popup
  if (currentPopup) {
    currentPopup.remove()
  }

  // Pan map to center the marker with offset for popup
  map.easeTo({
    center: coordinates,
    offset: [0, -100], // Offset upward to account for popup height
    duration: 500
  })

  // Create new popup after panning starts
  setTimeout(() => {
    currentPopup = new mapboxgl.Popup({
      closeButton: true,
      closeOnClick: true,
      maxWidth: '320px',
      className: 'location-popup'
    })
      .setLngLat(coordinates)
      .setHTML(createPopupContent(location))
      .addTo(map)

    // Attach click handlers after popup is rendered
    setTimeout(() => {
      const popupElement = currentPopup.getElement()
      if (!popupElement) return

      // Handle "See more" button clicks
      const seeMoreButtons = popupElement.querySelectorAll('.see-more-button')
      seeMoreButtons.forEach(button => {
        button.addEventListener('click', (e) => {
          const dishId = e.target.getAttribute('data-dish-id')
          if (dishId) {
            emit('dish-click', dishId)
            currentPopup.remove()
          }
        })
      })

      // Handle "View all dishes" button click
      const viewAllButton = popupElement.querySelector('.view-all-button')
      if (viewAllButton) {
        viewAllButton.addEventListener('click', (e) => {
          const restaurantSlug = e.target.getAttribute('data-restaurant-slug')
          if (restaurantSlug) {
            emit('view-all-dishes', restaurantSlug)
            currentPopup.remove()
          }
        })
      }
    }, 0)

    // Clean up popup reference when closed
    currentPopup.on('close', () => {
      currentPopup = null
    })
  }, 100)
}

// Update user location marker
const updateUserLocation = () => {
  if (!map || !map.isStyleLoaded()) return

  const sourceId = 'user-location'
  const layerId = 'user-location-marker'
  const pulseLayerId = 'user-location-pulse'

  // Remove existing layers and source
  if (map.getLayer(pulseLayerId)) map.removeLayer(pulseLayerId)
  if (map.getLayer(layerId)) map.removeLayer(layerId)
  if (map.getSource(sourceId)) map.removeSource(sourceId)

  // Add user location if provided
  if (props.userLocation && props.userLocation.lat && props.userLocation.lng) {
    const userGeoJSON = {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [props.userLocation.lng, props.userLocation.lat]
        },
        properties: {}
      }]
    }

    map.addSource(sourceId, {
      type: 'geojson',
      data: userGeoJSON
    })

    // Outer pulse circle
    map.addLayer({
      id: pulseLayerId,
      type: 'circle',
      source: sourceId,
      paint: {
        'circle-radius': 20,
        'circle-color': '#3B82F6',
        'circle-opacity': 0.2,
        'circle-stroke-color': '#3B82F6',
        'circle-stroke-width': 1,
        'circle-stroke-opacity': 0.3
      }
    })

    // Inner blue dot
    map.addLayer({
      id: layerId,
      type: 'circle',
      source: sourceId,
      paint: {
        'circle-radius': 10,
        'circle-color': '#3B82F6',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 3,
        'circle-opacity': 1
      }
    })

    // Pan map to user location
    map.easeTo({
      center: [props.userLocation.lng, props.userLocation.lat],
      duration: 1000
    })
  }
}

// Update markers on map
const updateMarkers = () => {
  if (!map || !map.isStyleLoaded()) return

  const clusterLayerId = 'clusters'
  const clusterCountLayerId = 'cluster-count'
  const unclusteredLayerId = 'unclustered-points'
  const sourceId = 'locations'

  // Remove existing layers and source
  if (map.getLayer(clusterCountLayerId)) map.removeLayer(clusterCountLayerId)
  if (map.getLayer(clusterLayerId)) map.removeLayer(clusterLayerId)
  if (map.getLayer(unclusteredLayerId)) map.removeLayer(unclusteredLayerId)
  if (map.getSource(sourceId)) map.removeSource(sourceId)

  // Add new source and layers if we have locations
  if (props.locations && props.locations.length > 0) {
    // Load locations into cluster index
    loadClusters()

    // Get clusters for current view
    const clusters = getClusters()

    // Create GeoJSON from clusters
    const clusterGeoJSON = {
      type: 'FeatureCollection',
      features: clusters
    }

    map.addSource(sourceId, {
      type: 'geojson',
      data: clusterGeoJSON
    })

    // Cluster circles
    map.addLayer({
      id: clusterLayerId,
      type: 'circle',
      source: sourceId,
      filter: ['has', 'point_count'],
      paint: {
        'circle-color': [
          'step',
          ['get', 'point_count'],
          '#51bbd6', 10,
          '#f1f075', 30,
          '#f28cb1'
        ],
        'circle-radius': [
          'step',
          ['get', 'point_count'],
          20, 10,
          30, 30,
          40
        ],
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2
      }
    })

    // Cluster count labels
    map.addLayer({
      id: clusterCountLayerId,
      type: 'symbol',
      source: sourceId,
      filter: ['has', 'point_count'],
      layout: {
        'text-field': '{point_count_abbreviated}',
        'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
        'text-size': 14
      },
      paint: {
        'text-color': '#ffffff'
      }
    })

    // Individual location markers
    map.addLayer({
      id: unclusteredLayerId,
      type: 'circle',
      source: sourceId,
      filter: ['!', ['has', 'point_count']],
      paint: {
        'circle-radius': 8,
        'circle-color': ['get', 'color'],
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2,
        'circle-opacity': 0.9
      }
    })

    // Add hover cursor
    map.on('mouseenter', unclusteredLayerId, () => {
      map.getCanvas().style.cursor = 'pointer'
    })

    map.on('mouseleave', unclusteredLayerId, () => {
      map.getCanvas().style.cursor = ''
    })

    // Handle cluster click - zoom to cluster bounds
    map.on('click', clusterLayerId, (e) => {
      const features = map.queryRenderedFeatures(e.point, {
        layers: [clusterLayerId]
      })

      if (features.length > 0) {
        const clusterId = features[0].properties.cluster_id
        const zoom = map.getZoom()
        const expansionZoom = clusterIndex.getClusterExpansionZoom(clusterId)

        map.easeTo({
          center: features[0].geometry.coordinates,
          zoom: expansionZoom
        })
      }
    })

    // Handle individual marker click
    map.on('click', unclusteredLayerId, (e) => {
      if (e.features && e.features.length > 0) {
        const feature = e.features[0]
        const location = {
          id: feature.properties.id,
          name: feature.properties.name,
          restaurant: JSON.parse(feature.properties.restaurant)
        }

        // Show popup with dishes
        showPopup(location, feature.geometry.coordinates)

        // Still emit event for any parent component that might need it
        emit('marker-click', {
          ...location,
          coordinates: feature.geometry.coordinates
        })
      }
    })

    // Handle hover cursor
    map.on('mouseenter', clusterLayerId, () => {
      map.getCanvas().style.cursor = 'pointer'
    })

    map.on('mouseleave', clusterLayerId, () => {
      map.getCanvas().style.cursor = ''
    })

    map.on('mouseenter', unclusteredLayerId, () => {
      map.getCanvas().style.cursor = 'pointer'
    })

    map.on('mouseleave', unclusteredLayerId, () => {
      map.getCanvas().style.cursor = ''
    })
  }
}

onMounted(() => {
  // Initialize cluster index
  initCluster()

  // Set Mapbox access token
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

  // Initialize map
  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v12',
    center: props.center,
    zoom: props.zoom
  })

  // Add map controls
  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  map.addControl(
    new mapboxgl.GeolocateControl({
      positionOptions: {
        enableHighAccuracy: true
      },
      trackUserLocation: true,
      showUserHeading: true
    }),
    'top-right'
  )

  // Handle map load
  map.on('load', () => {
    updateMarkers()
    updateUserLocation()
    isLoading.value = false
    emit('load', map)
  })

  // Handle map movement (pan/zoom) - update clusters
  map.on('moveend', () => {
    const bounds = map.getBounds()
    const center = map.getCenter()
    const zoom = map.getZoom()

    // Update clusters for new view
    updateMarkers()

    const boundsData = {
      bounds: {
        sw: [bounds.getWest(), bounds.getSouth()],
        ne: [bounds.getEast(), bounds.getNorth()],
        swLat: bounds.getSouth(),
        swLng: bounds.getWest(),
        neLat: bounds.getNorth(),
        neLng: bounds.getEast()
      },
      center: [center.lng, center.lat],
      zoom: zoom
    }

    // Emit immediate move event (for UI updates)
    emit('move', boundsData)

    // Emit debounced bounds-change event (for API calls)
    if (boundsChangeTimeout) {
      clearTimeout(boundsChangeTimeout)
    }
    boundsChangeTimeout = setTimeout(() => {
      emit('bounds-change', {
        bbox: `${bounds.getSouth()},${bounds.getWest()},${bounds.getNorth()},${bounds.getEast()}`,
        swLat: bounds.getSouth(),
        swLng: bounds.getWest(),
        neLat: bounds.getNorth(),
        neLng: bounds.getEast(),
        center: [center.lng, center.lat],
        zoom: zoom
      })
    }, 300)
  })

  // Handle window resize
  const handleResize = () => {
    if (map) {
      map.resize()
    }
  }
  window.addEventListener('resize', handleResize)

  // Store cleanup function
  map._handleResize = handleResize
})

onUnmounted(() => {
  // Clear debounce timeout
  if (boundsChangeTimeout) {
    clearTimeout(boundsChangeTimeout)
    boundsChangeTimeout = null
  }

  if (map) {
    // Remove resize listener
    if (map._handleResize) {
      window.removeEventListener('resize', map._handleResize)
    }
    // Remove map
    map.remove()
    map = null
  }
  // Clean up cluster index
  clusterIndex = null
})

// Watch for center prop changes
watch(() => props.center, (newCenter) => {
  if (map && newCenter) {
    map.setCenter(newCenter)
  }
})

// Watch for zoom prop changes
watch(() => props.zoom, (newZoom) => {
  if (map && newZoom !== undefined) {
    map.setZoom(newZoom)
  }
})

// Watch for locations prop changes
watch(() => props.locations, () => {
  if (map && map.isStyleLoaded()) {
    // Reinitialize cluster with new locations
    if (!clusterIndex) {
      initCluster()
    }
    updateMarkers()
  }
}, { deep: true })

// Watch for highlightedRestaurantSlug changes
watch(() => props.highlightedRestaurantSlug, (newSlug) => {
  if (map && map.isStyleLoaded() && map.getLayer('unclustered-points')) {
    // Update marker styling based on highlighted restaurant
    if (newSlug) {
      // Make matching markers larger and more prominent
      map.setPaintProperty('unclustered-points', 'circle-radius', [
        'case',
        ['==', ['get', 'restaurantSlug'], newSlug],
        12,  // Larger radius for highlighted
        8    // Normal radius
      ])
      map.setPaintProperty('unclustered-points', 'circle-stroke-width', [
        'case',
        ['==', ['get', 'restaurantSlug'], newSlug],
        3,   // Thicker stroke for highlighted
        2    // Normal stroke
      ])
      map.setPaintProperty('unclustered-points', 'circle-opacity', [
        'case',
        ['==', ['get', 'restaurantSlug'], newSlug],
        1,     // Full opacity for highlighted
        0.4    // Dimmed for non-highlighted
      ])
    } else {
      // Reset to normal styling
      map.setPaintProperty('unclustered-points', 'circle-radius', 8)
      map.setPaintProperty('unclustered-points', 'circle-stroke-width', 2)
      map.setPaintProperty('unclustered-points', 'circle-opacity', 0.9)
    }
  }
})

// Watch for userLocation prop changes
watch(() => props.userLocation, (newLocation) => {
  if (map && map.isStyleLoaded() && newLocation) {
    updateUserLocation()
  }
}, { deep: true })

// Expose map instance and loading state for parent components
defineExpose({
  getMap: () => map,
  setLoading: (loading) => {
    isLoading.value = loading
  }
})
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(var(--color-background), 0.9);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 48px;
  height: 48px;
  color: var(--color-primary);
  animation: spin 1s linear infinite;
}

.loading-text {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style>
/* Popup styles (not scoped so they apply to Mapbox popup) */
.mapboxgl-popup-content {
  padding: 0 !important;
  border-radius: 12px !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1) !important;
}

.mapboxgl-popup-close-button {
  font-size: 24px !important;
  padding: 8px 12px !important;
  color: var(--color-text-secondary) !important;
  transition: color 200ms ease !important;
}

.mapboxgl-popup-close-button:hover {
  color: var(--color-text-primary) !important;
  background-color: transparent !important;
}

.map-popup {
  padding: 16px;
  max-width: 320px;
}

.popup-restaurant-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.popup-address {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.popup-dishes {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.popup-dish {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  transition: all 200ms ease;
}

.popup-dish:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.dish-info {
  flex: 1;
  min-width: 0;
}

.dish-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dish-macros {
  margin: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.see-more-button {
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
  transition: opacity 200ms ease;
}

.see-more-button:hover {
  opacity: 0.9;
}

.no-dishes {
  padding: 12px;
  text-align: center;
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.view-all-button {
  width: 100%;
  margin-top: 12px;
  padding: 10px 16px;
  background-color: var(--color-surface-elevated);
  color: var(--color-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.view-all-button:hover {
  background-color: var(--color-surface);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}
</style>
