/**
 * Scroll state machine for 7-section landing page
 * Manages scroll progress and section transitions
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// Section breakpoints as percentages of total scroll
const SECTIONS = {
  HERO: { start: 0, end: 0.15, id: 0 },
  TRANSFORMATION: { start: 0.15, end: 0.35, id: 1 },
  MACRO_SPACE: { start: 0.35, end: 0.50, id: 2 },
  SPEED: { start: 0.50, end: 0.62, id: 3 },
  TRUST: { start: 0.62, end: 0.75, id: 4 },
  ZILLOW: { start: 0.75, end: 0.88, id: 5 },
  CTA: { start: 0.88, end: 1.0, id: 6 },
}

export function useLandingScroll() {
  const scrollProgress = ref(0)
  const activeSection = ref(0)
  const sectionProgress = ref(0) // Progress within current section (0-1)

  // Derived state for each section
  const heroProgress = computed(() => getSectionProgress(SECTIONS.HERO))
  const transformationProgress = computed(() => getSectionProgress(SECTIONS.TRANSFORMATION))
  const macroSpaceProgress = computed(() => getSectionProgress(SECTIONS.MACRO_SPACE))
  const speedProgress = computed(() => getSectionProgress(SECTIONS.SPEED))
  const trustProgress = computed(() => getSectionProgress(SECTIONS.TRUST))
  const zillowProgress = computed(() => getSectionProgress(SECTIONS.ZILLOW))
  const ctaProgress = computed(() => getSectionProgress(SECTIONS.CTA))

  // Get normalized progress within a specific section (0-1)
  function getSectionProgress(section) {
    const progress = scrollProgress.value
    if (progress < section.start) return 0
    if (progress > section.end) return 1
    return (progress - section.start) / (section.end - section.start)
  }

  // Determine which section is active based on scroll
  function updateActiveSection(progress) {
    for (const [name, section] of Object.entries(SECTIONS)) {
      if (progress >= section.start && progress < section.end) {
        activeSection.value = section.id
        sectionProgress.value = getSectionProgress(section)
        return
      }
    }
    // At the end
    activeSection.value = SECTIONS.CTA.id
    sectionProgress.value = 1
  }

  let scrollTrigger = null

  onMounted(() => {
    scrollTrigger = ScrollTrigger.create({
      trigger: 'body',
      start: 'top top',
      end: 'bottom bottom',
      onUpdate: (self) => {
        scrollProgress.value = self.progress
        updateActiveSection(self.progress)
      },
    })
  })

  onUnmounted(() => {
    if (scrollTrigger) {
      scrollTrigger.kill()
    }
    ScrollTrigger.getAll().forEach(t => t.kill())
  })

  return {
    scrollProgress,
    activeSection,
    sectionProgress,
    heroProgress,
    transformationProgress,
    macroSpaceProgress,
    speedProgress,
    trustProgress,
    zillowProgress,
    ctaProgress,
    SECTIONS,
  }
}
