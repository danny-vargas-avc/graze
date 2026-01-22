/**
 * GSAP timeline orchestration for chaos-to-grid transformation
 * The "money shot" animation
 */
import { ref, computed } from 'vue'
import { gsap } from 'gsap'

export function useTransformation() {
  const transformationPhase = ref('idle') // idle, typewriter, collapsing, emerging, highlight
  const typewriterText = ref('')
  const mealCardsVisible = ref(false)
  const highlightedMealIndex = ref(-1)

  const FULL_FILTER_TEXT = '>= 40g protein, <= 600 calories'

  let timeline = null
  let typewriterTimeline = null

  // Build the transformation timeline based on scroll progress
  function updateTransformation(progress) {
    // Phase 1: Typewriter (0-20% of transformation section)
    if (progress < 0.2) {
      transformationPhase.value = 'typewriter'
      const typeProgress = progress / 0.2
      const charCount = Math.floor(typeProgress * FULL_FILTER_TEXT.length)
      typewriterText.value = FULL_FILTER_TEXT.substring(0, charCount)
      mealCardsVisible.value = false
      highlightedMealIndex.value = -1
    }
    // Phase 2: Chaos collapsing (20-50%)
    else if (progress < 0.5) {
      transformationPhase.value = 'collapsing'
      typewriterText.value = FULL_FILTER_TEXT
      mealCardsVisible.value = false
    }
    // Phase 3: Meal cards emerging (40-80%, overlaps with collapse)
    else if (progress < 0.8) {
      transformationPhase.value = 'emerging'
      typewriterText.value = FULL_FILTER_TEXT
      mealCardsVisible.value = true
      highlightedMealIndex.value = -1
    }
    // Phase 4: Best match highlights (70-100%)
    else {
      transformationPhase.value = 'highlight'
      typewriterText.value = FULL_FILTER_TEXT
      mealCardsVisible.value = true
      highlightedMealIndex.value = 0 // First card is "best match"
    }
  }

  // Calculate meal card emergence progress (for scale animation)
  function getMealCardProgress(progress) {
    const emergeStart = 0.4
    const emergeEnd = 0.8
    if (progress < emergeStart) return 0
    if (progress > emergeEnd) return 1
    return (progress - emergeStart) / (emergeEnd - emergeStart)
  }

  // Calculate chaos collapse progress
  function getChaosCollapseProgress(progress) {
    const collapseStart = 0.2
    const collapseEnd = 0.5
    if (progress < collapseStart) return 0
    if (progress > collapseEnd) return 1
    return (progress - collapseStart) / (collapseEnd - collapseStart)
  }

  // Calculate highlight progress for best match card
  function getHighlightProgress(progress) {
    const highlightStart = 0.7
    const highlightEnd = 1.0
    if (progress < highlightStart) return 0
    if (progress > highlightEnd) return 1
    return (progress - highlightStart) / (highlightEnd - highlightStart)
  }

  // Easing functions
  function easeOutBack(t, overshoot = 1.7) {
    return 1 + (--t) * t * ((overshoot + 1) * t + overshoot)
  }

  function easeInPower3(t) {
    return t * t * t
  }

  // Apply eased values for smooth animation
  const chaosScale = computed(() => {
    const progress = getChaosCollapseProgress(transformationPhase.value === 'collapsing' ? 0.5 : 0)
    return 1 - easeInPower3(progress) * 0.7
  })

  const mealCardScale = computed(() => {
    const progress = getMealCardProgress(transformationPhase.value === 'emerging' ? 0.7 : 0)
    return easeOutBack(progress)
  })

  // Reset transformation state
  function reset() {
    transformationPhase.value = 'idle'
    typewriterText.value = ''
    mealCardsVisible.value = false
    highlightedMealIndex.value = -1

    if (timeline) {
      timeline.kill()
      timeline = null
    }
    if (typewriterTimeline) {
      typewriterTimeline.kill()
      typewriterTimeline = null
    }
  }

  return {
    transformationPhase,
    typewriterText,
    mealCardsVisible,
    highlightedMealIndex,
    updateTransformation,
    getMealCardProgress,
    getChaosCollapseProgress,
    getHighlightProgress,
    easeOutBack,
    easeInPower3,
    reset,
    FULL_FILTER_TEXT,
  }
}
