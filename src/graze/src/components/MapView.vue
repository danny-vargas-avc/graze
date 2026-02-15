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
import { useConfigStore } from '../stores/config'

const configStore = useConfigStore()

const MARKER_SIZE = 64
const MARKER_BORDER = 4

const props = defineProps({
  center: {
    type: Array,
    default: () => [-74.0060, 40.7128]
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
    default: null
  },
  highlightedRestaurantSlug: {
    type: String,
    default: null
  },
})

const emit = defineEmits(['move', 'load', 'marker-click', 'bounds-change'])

const mapContainer = ref(null)
const isLoading = ref(true)
const isDarkMode = ref(false)
let map = null
let clusterIndex = null
let boundsChangeTimeout = null

// Layer and source IDs
const CLUSTER_LAYER = 'clusters'
const CLUSTER_COUNT_LAYER = 'cluster-count'
const MARKERS_LAYER = 'unclustered-points'
const SOURCE_ID = 'locations'

const updateDarkMode = () => {
  isDarkMode.value = document.documentElement.classList.contains('dark')
}

const getMapStyle = () => {
  return isDarkMode.value
    ? 'mapbox://styles/mapbox/dark-v11'
    : 'mapbox://styles/mapbox/streets-v12'
}

// --- Marker Image Rendering ---

// Create a canvas with a colored circle and white initial letter
const createInitialMarker = (color, initial) => {
  const canvas = document.createElement('canvas')
  canvas.width = MARKER_SIZE
  canvas.height = MARKER_SIZE
  const ctx = canvas.getContext('2d')
  const r = MARKER_SIZE / 2

  // White border ring
  ctx.beginPath()
  ctx.arc(r, r, r, 0, Math.PI * 2)
  ctx.fillStyle = '#ffffff'
  ctx.fill()

  // Colored inner circle
  ctx.beginPath()
  ctx.arc(r, r, r - MARKER_BORDER, 0, Math.PI * 2)
  ctx.fillStyle = color
  ctx.fill()

  // Initial letter
  ctx.fillStyle = '#ffffff'
  ctx.font = `bold ${MARKER_SIZE * 0.4}px -apple-system, BlinkMacSystemFont, sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(initial, r, r + 1)

  const imageData = ctx.getImageData(0, 0, MARKER_SIZE, MARKER_SIZE)
  return { data: new Uint8Array(imageData.data.buffer), width: MARKER_SIZE, height: MARKER_SIZE }
}

// Load an image URL and render it clipped to a circle with white border
const createIconMarker = (url) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = MARKER_SIZE
      canvas.height = MARKER_SIZE
      const ctx = canvas.getContext('2d')
      const r = MARKER_SIZE / 2
      const inner = r - MARKER_BORDER

      // White border ring
      ctx.beginPath()
      ctx.arc(r, r, r, 0, Math.PI * 2)
      ctx.fillStyle = '#ffffff'
      ctx.fill()

      // Clip to inner circle and draw image
      ctx.save()
      ctx.beginPath()
      ctx.arc(r, r, inner, 0, Math.PI * 2)
      ctx.clip()
      ctx.drawImage(img, MARKER_BORDER, MARKER_BORDER, inner * 2, inner * 2)
      ctx.restore()

      const imageData = ctx.getImageData(0, 0, MARKER_SIZE, MARKER_SIZE)
      resolve({ data: new Uint8Array(imageData.data.buffer), width: MARKER_SIZE, height: MARKER_SIZE })
    }
    img.onerror = () => resolve(null)
    img.src = url
  })
}

// Load all restaurant marker images into the map style
const loadMarkerImages = async () => {
  if (!map) return

  const icons = configStore.restaurantIcons || {}
  const colors = configStore.restaurantColors || {}

  // Collect all slugs we need markers for
  const slugs = new Set([...Object.keys(icons), ...Object.keys(colors)])
  slugs.delete('default')

  for (const slug of slugs) {
    const imageName = `marker-${slug}`
    if (map.hasImage(imageName)) map.removeImage(imageName)

    const iconUrl = icons[slug]
    const color = colors[slug] || colors['default'] || '#3B82F6'
    // Use first letter of first word for initial
    const initial = slug.replace(/-.*/, '').charAt(0).toUpperCase()

    let imageObj = null
    if (iconUrl) {
      imageObj = await createIconMarker(iconUrl)
    }
    if (!imageObj) {
      imageObj = createInitialMarker(color, initial)
    }

    map.addImage(imageName, imageObj)
  }

  // Default fallback marker
  const defaultName = 'marker-default'
  if (map.hasImage(defaultName)) map.removeImage(defaultName)
  map.addImage(defaultName, createInitialMarker(colors['default'] || '#3B82F6', '?'))
}

// --- Supercluster ---

const initCluster = () => {
  clusterIndex = new Supercluster({
    radius: 60,
    maxZoom: 14,
    minZoom: 0,
    minPoints: 2
  })
}

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
        restaurantName: location.restaurant?.name || '',
        color: configStore.getRestaurantColor(location.restaurant?.slug)
      }
    }))
  }
}

const loadClusters = () => {
  if (!clusterIndex || !props.locations || props.locations.length === 0) return
  const geojson = createGeoJSON(props.locations)
  clusterIndex.load(geojson.features)
}

const getClusters = () => {
  if (!map || !clusterIndex) return []
  const bounds = map.getBounds()
  const zoom = map.getZoom()
  return clusterIndex.getClusters(
    [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()],
    Math.floor(zoom)
  )
}

// --- User Location Marker ---

const updateUserLocation = () => {
  if (!map || !map.isStyleLoaded()) return

  const sourceId = 'user-location'
  const layerId = 'user-location-marker'
  const pulseLayerId = 'user-location-pulse'

  if (map.getLayer(pulseLayerId)) map.removeLayer(pulseLayerId)
  if (map.getLayer(layerId)) map.removeLayer(layerId)
  if (map.getSource(sourceId)) map.removeSource(sourceId)

  if (props.userLocation && props.userLocation.lat && props.userLocation.lng) {
    map.addSource(sourceId, {
      type: 'geojson',
      data: {
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
    })

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

    map.easeTo({
      center: [props.userLocation.lng, props.userLocation.lat],
      duration: 1000
    })
  }
}

// --- Map Layers ---

const updateMarkers = () => {
  if (!map || !map.isStyleLoaded()) return

  // Remove existing layers and source
  if (map.getLayer(CLUSTER_COUNT_LAYER)) map.removeLayer(CLUSTER_COUNT_LAYER)
  if (map.getLayer(CLUSTER_LAYER)) map.removeLayer(CLUSTER_LAYER)
  if (map.getLayer(MARKERS_LAYER)) map.removeLayer(MARKERS_LAYER)
  if (map.getSource(SOURCE_ID)) map.removeSource(SOURCE_ID)

  if (!props.locations || props.locations.length === 0) return

  loadClusters()
  const clusters = getClusters()

  map.addSource(SOURCE_ID, {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: clusters }
  })

  // Cluster circles — brand green
  map.addLayer({
    id: CLUSTER_LAYER,
    type: 'circle',
    source: SOURCE_ID,
    filter: ['has', 'point_count'],
    paint: {
      'circle-color': [
        'step', ['get', 'point_count'],
        '#06C167', 10,
        '#05a85a', 50,
        '#048a49'
      ],
      'circle-radius': [
        'step', ['get', 'point_count'],
        18, 10,
        24, 50,
        30
      ],
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 2
    }
  })

  // Cluster count text
  map.addLayer({
    id: CLUSTER_COUNT_LAYER,
    type: 'symbol',
    source: SOURCE_ID,
    filter: ['has', 'point_count'],
    layout: {
      'text-field': '{point_count_abbreviated}',
      'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
      'text-size': 13
    },
    paint: {
      'text-color': '#ffffff'
    }
  })

  // Individual markers — restaurant icon symbols
  map.addLayer({
    id: MARKERS_LAYER,
    type: 'symbol',
    source: SOURCE_ID,
    filter: ['!', ['has', 'point_count']],
    layout: {
      'icon-image': ['concat', 'marker-', ['get', 'restaurantSlug']],
      'icon-size': 0.5,
      'icon-allow-overlap': true,
      'icon-ignore-placement': true,
      // Restaurant name labels at high zoom
      'text-field': ['step', ['zoom'], '', 14, ['get', 'restaurantName']],
      'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Regular'],
      'text-size': 11,
      'text-offset': [0, 1.8],
      'text-anchor': 'top',
      'text-optional': true,
      'text-allow-overlap': false,
    },
    paint: {
      'icon-opacity': 0.95,
      'text-color': isDarkMode.value ? '#e5e5e5' : '#333333',
      'text-halo-color': isDarkMode.value ? '#1a1a1a' : '#ffffff',
      'text-halo-width': 1.5,
    }
  })
}

// --- Event Handlers (registered once) ---

const setupMapEvents = () => {
  // Cluster click — zoom to expand
  map.on('click', CLUSTER_LAYER, (e) => {
    const features = map.queryRenderedFeatures(e.point, { layers: [CLUSTER_LAYER] })
    if (features.length > 0) {
      const clusterId = features[0].properties.cluster_id
      const expansionZoom = clusterIndex.getClusterExpansionZoom(clusterId)
      map.easeTo({
        center: features[0].geometry.coordinates,
        zoom: expansionZoom
      })
    }
  })

  // Marker click — emit for bottom sheet
  map.on('click', MARKERS_LAYER, (e) => {
    if (e.features && e.features.length > 0) {
      const feature = e.features[0]
      emit('marker-click', {
        id: feature.properties.id,
        name: feature.properties.name,
        restaurant: JSON.parse(feature.properties.restaurant),
        coordinates: feature.geometry.coordinates
      })
    }
  })

  // Hover cursors
  map.on('mouseenter', CLUSTER_LAYER, () => {
    map.getCanvas().style.cursor = 'pointer'
  })
  map.on('mouseleave', CLUSTER_LAYER, () => {
    map.getCanvas().style.cursor = ''
  })
  map.on('mouseenter', MARKERS_LAYER, () => {
    map.getCanvas().style.cursor = 'pointer'
  })
  map.on('mouseleave', MARKERS_LAYER, () => {
    map.getCanvas().style.cursor = ''
  })
}

// --- Lifecycle ---

onMounted(async () => {
  initCluster()
  updateDarkMode()

  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: getMapStyle(),
    center: props.center,
    zoom: props.zoom
  })

  // Theme observer
  const observer = new MutationObserver(() => {
    const newIsDark = document.documentElement.classList.contains('dark')
    if (newIsDark !== isDarkMode.value) {
      isDarkMode.value = newIsDark
      if (map) map.setStyle(getMapStyle())
    }
  })
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  })
  map._themeObserver = observer

  // Map controls
  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  map.addControl(
    new mapboxgl.GeolocateControl({
      positionOptions: { enableHighAccuracy: true },
      trackUserLocation: true,
      showUserHeading: true
    }),
    'top-right'
  )

  // Map load
  map.on('load', async () => {
    await loadMarkerImages()
    setupMapEvents()
    updateMarkers()
    updateUserLocation()
    isLoading.value = false
    emit('load', map)
  })

  // Style reload (theme change) — re-load images and layers
  map.on('style.load', async () => {
    await loadMarkerImages()
    updateMarkers()
    updateUserLocation()
  })

  // Map movement — update clusters
  map.on('moveend', () => {
    const bounds = map.getBounds()
    const center = map.getCenter()
    const zoom = map.getZoom()

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

    emit('move', boundsData)

    if (boundsChangeTimeout) clearTimeout(boundsChangeTimeout)
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

  // Resize observer
  const resizeObserver = new ResizeObserver(() => {
    if (map) map.resize()
  })
  resizeObserver.observe(mapContainer.value)
  map._resizeObserver = resizeObserver
})

onUnmounted(() => {
  if (boundsChangeTimeout) {
    clearTimeout(boundsChangeTimeout)
    boundsChangeTimeout = null
  }

  if (map) {
    if (map._themeObserver) map._themeObserver.disconnect()
    if (map._resizeObserver) map._resizeObserver.disconnect()
    map.remove()
    map = null
  }
  clusterIndex = null
})

// --- Watchers ---

watch(() => props.center, (newCenter) => {
  if (map && newCenter) map.setCenter(newCenter)
})

watch(() => props.zoom, (newZoom) => {
  if (map && newZoom !== undefined) map.setZoom(newZoom)
})

watch(() => props.locations, () => {
  if (map && map.isStyleLoaded()) {
    if (!clusterIndex) initCluster()
    updateMarkers()
  }
}, { deep: true })

watch(() => props.highlightedRestaurantSlug, (newSlug) => {
  if (!map || !map.isStyleLoaded() || !map.getLayer(MARKERS_LAYER)) return

  if (newSlug) {
    map.setLayoutProperty(MARKERS_LAYER, 'icon-size', [
      'case',
      ['==', ['get', 'restaurantSlug'], newSlug],
      0.65,
      0.5
    ])
    map.setPaintProperty(MARKERS_LAYER, 'icon-opacity', [
      'case',
      ['==', ['get', 'restaurantSlug'], newSlug],
      1,
      0.35
    ])
    map.setPaintProperty(MARKERS_LAYER, 'text-opacity', [
      'case',
      ['==', ['get', 'restaurantSlug'], newSlug],
      1,
      0.3
    ])
  } else {
    map.setLayoutProperty(MARKERS_LAYER, 'icon-size', 0.5)
    map.setPaintProperty(MARKERS_LAYER, 'icon-opacity', 0.95)
    map.setPaintProperty(MARKERS_LAYER, 'text-opacity', 1)
  }
})

watch(() => props.userLocation, (newLocation) => {
  if (map && map.isStyleLoaded() && newLocation) {
    updateUserLocation()
  }
}, { deep: true })

defineExpose({
  getMap: () => map,
  setLoading: (loading) => { isLoading.value = loading }
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
