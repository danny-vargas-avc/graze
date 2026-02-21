// iOS-style draggable bottom sheet composable
// Handles touch drag, rubber band overscroll, velocity flick, and spring snap animation.

import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

const IOS_SPRING = 'cubic-bezier(0.32, 0.72, 0, 1)'
const SPRING_DURATION = 450
const FLICK_THRESHOLD = 0.5 // px/ms
const RUBBER_BAND_DEFAULT = 0.3

export function useSheetDrag(options = {}) {
  const {
    snapPoints: initialSnapPoints = [0, 300],
    initialSnap = 0,
    onClose = null,
    rubberBandFactor = RUBBER_BAND_DEFAULT,
  } = options

  const snapPoints = ref([...initialSnapPoints])
  const sheetRef = ref(null)
  const handleRef = ref(null)
  const currentHeight = ref(snapPoints.value[initialSnap] ?? 0)
  const isDragging = ref(false)

  let startY = 0
  let startHeight = 0
  let lastTouches = [] // { y, time } for velocity calc

  const minSnap = computed(() => Math.min(...snapPoints.value))
  const maxSnap = computed(() => Math.max(...snapPoints.value))

  const sheetStyle = computed(() => {
    const translate = `translateY(calc(100% - ${currentHeight.value}px))`
    return {
      transform: translate,
      transition: isDragging.value ? 'none' : `transform ${SPRING_DURATION}ms ${IOS_SPRING}`,
      willChange: isDragging.value ? 'transform' : 'auto',
    }
  })

  function rubberBand(offset, limit) {
    // iOS rubber band: diminishing returns past the edge
    const d = Math.abs(offset)
    return Math.sign(offset) * d * rubberBandFactor * (1 - d / (d + limit * 0.55))
  }

  function clampWithRubberBand(height) {
    const min = minSnap.value
    const max = maxSnap.value
    if (height > max) {
      return max + rubberBand(height - max, max)
    }
    if (height < min) {
      return min + rubberBand(height - min, max)
    }
    return height
  }

  function getVelocity() {
    if (lastTouches.length < 2) return 0
    const last = lastTouches[lastTouches.length - 1]
    const prev = lastTouches[Math.max(0, lastTouches.length - 3)]
    const dt = last.time - prev.time
    if (dt === 0) return 0
    return (prev.y - last.y) / dt // positive = dragging up (increasing height)
  }

  function findNearestSnap(height) {
    let nearest = snapPoints.value[0]
    let minDist = Math.abs(height - nearest)
    for (const sp of snapPoints.value) {
      const dist = Math.abs(height - sp)
      if (dist < minDist) {
        minDist = dist
        nearest = sp
      }
    }
    return nearest
  }

  function findNextSnap(height, direction) {
    // direction: 1 = up (higher snap), -1 = down (lower snap)
    const sorted = [...snapPoints.value].sort((a, b) => a - b)
    if (direction > 0) {
      for (const sp of sorted) {
        if (sp > height + 10) return sp
      }
      return sorted[sorted.length - 1]
    } else {
      for (let i = sorted.length - 1; i >= 0; i--) {
        if (sorted[i] < height - 10) return sorted[i]
      }
      return sorted[0]
    }
  }

  function snapTo(indexOrHeight) {
    let target
    if (typeof indexOrHeight === 'number' && indexOrHeight < snapPoints.value.length && Number.isInteger(indexOrHeight)) {
      target = snapPoints.value[indexOrHeight]
    } else {
      target = indexOrHeight
    }
    isDragging.value = false
    currentHeight.value = target

    if (target <= 0 && onClose) {
      // Small delay to let animation finish before closing
      setTimeout(() => onClose(), SPRING_DURATION)
    }
  }

  function updateSnapPoints(newPoints) {
    snapPoints.value = [...newPoints]
  }

  function onTouchStart(e) {
    const touch = e.touches[0]
    startY = touch.clientY
    startHeight = currentHeight.value
    lastTouches = [{ y: touch.clientY, time: Date.now() }]
    isDragging.value = true
  }

  function onTouchMove(e) {
    if (!isDragging.value) return
    e.preventDefault()

    const touch = e.touches[0]
    const deltaY = startY - touch.clientY // positive = dragging up
    const rawHeight = startHeight + deltaY

    currentHeight.value = clampWithRubberBand(rawHeight)

    lastTouches.push({ y: touch.clientY, time: Date.now() })
    if (lastTouches.length > 5) lastTouches.shift()
  }

  function onTouchEnd() {
    if (!isDragging.value) return

    const velocity = getVelocity() // px/ms, positive = upward
    const height = currentHeight.value

    let target
    if (Math.abs(velocity) > FLICK_THRESHOLD) {
      // Flick — go to next snap in direction of velocity
      target = findNextSnap(height, velocity > 0 ? 1 : -1)
    } else {
      // Settle to nearest snap
      target = findNearestSnap(height)
    }

    snapTo(target <= 0 && onClose ? 0 : target)
  }

  function attachListeners() {
    const handle = handleRef.value
    if (!handle) return

    handle.addEventListener('touchstart', onTouchStart, { passive: true })
    handle.addEventListener('touchmove', onTouchMove, { passive: false })
    handle.addEventListener('touchend', onTouchEnd, { passive: true })
  }

  function detachListeners() {
    const handle = handleRef.value
    if (!handle) return

    handle.removeEventListener('touchstart', onTouchStart)
    handle.removeEventListener('touchmove', onTouchMove)
    handle.removeEventListener('touchend', onTouchEnd)
  }

  // Re-attach listeners when handleRef changes (supports v-if)
  let prevHandle = null
  watch(handleRef, (newHandle) => {
    if (prevHandle) {
      prevHandle.removeEventListener('touchstart', onTouchStart)
      prevHandle.removeEventListener('touchmove', onTouchMove)
      prevHandle.removeEventListener('touchend', onTouchEnd)
    }
    prevHandle = newHandle
    if (newHandle) attachListeners()
  })

  onMounted(() => {
    nextTick(() => attachListeners())
  })

  onBeforeUnmount(() => {
    detachListeners()
  })

  return {
    sheetRef,
    handleRef,
    sheetStyle,
    currentHeight,
    isDragging,
    snapTo,
    updateSnapPoints,
  }
}
