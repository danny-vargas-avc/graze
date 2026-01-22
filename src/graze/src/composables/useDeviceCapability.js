/**
 * Device capability detection for mobile/GPU fallbacks
 */
import { ref, computed, onMounted } from 'vue'

export function useDeviceCapability() {
  const isMobile = ref(false)
  const hasWebGL = ref(true)
  const isLowPerfDevice = ref(false)
  const pixelRatio = ref(1)

  onMounted(() => {
    // Check mobile
    isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ) || window.innerWidth < 768

    // Check WebGL support
    try {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
      hasWebGL.value = !!gl

      if (gl) {
        // Check for integrated GPU (typically lower performance)
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
        if (debugInfo) {
          const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
          isLowPerfDevice.value = /Intel|Mali|Adreno 3|Adreno 4/i.test(renderer)
        }
      }
    } catch (e) {
      hasWebGL.value = false
    }

    // Get pixel ratio (capped for performance)
    pixelRatio.value = Math.min(window.devicePixelRatio || 1, 2)

    // Additional check: prefer reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      isLowPerfDevice.value = true
    }
  })

  // Should use CSS-only fallback
  const shouldUseFallback = computed(() => {
    return isMobile.value || !hasWebGL.value || isLowPerfDevice.value
  })

  // Recommended quality settings
  const qualitySettings = computed(() => {
    if (shouldUseFallback.value) {
      return {
        particleCount: 0,
        shadowsEnabled: false,
        antialiasEnabled: false,
        pixelRatio: 1,
      }
    }

    if (isLowPerfDevice.value) {
      return {
        particleCount: 10,
        shadowsEnabled: false,
        antialiasEnabled: false,
        pixelRatio: 1,
      }
    }

    return {
      particleCount: 25,
      shadowsEnabled: true,
      antialiasEnabled: true,
      pixelRatio: pixelRatio.value,
    }
  })

  return {
    isMobile,
    hasWebGL,
    isLowPerfDevice,
    pixelRatio,
    shouldUseFallback,
    qualitySettings,
  }
}
