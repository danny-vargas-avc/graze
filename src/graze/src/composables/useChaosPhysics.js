/**
 * Drift physics for chaos elements (floating menus, PDFs, etc.)
 * Creates slow, organic movement with gentle vertical bob
 */
import { ref, onMounted } from 'vue'

export function useChaosPhysics(count = 20) {
  const elements = ref([])

  // Element types for the chaos scene
  const ELEMENT_TYPES = [
    { type: 'menu', aspect: 0.75, depth: 0.02 },      // Menu (portrait)
    { type: 'pdf', aspect: 0.77, depth: 0.01 },       // PDF page
    { type: 'spreadsheet', aspect: 1.33, depth: 0.01 }, // Spreadsheet (landscape)
    { type: 'app', aspect: 0.5, depth: 0.02 },        // App screenshot
  ]

  // Initialize elements with random positions and physics properties
  function initializeElements() {
    const items = []

    for (let i = 0; i < count; i++) {
      const elementType = ELEMENT_TYPES[i % ELEMENT_TYPES.length]

      // Distribute in a wide area
      const angle = (i / count) * Math.PI * 2 + Math.random() * 0.5
      const radius = 3 + Math.random() * 8
      const height = (Math.random() - 0.5) * 6

      const x = Math.cos(angle) * radius
      const z = Math.sin(angle) * radius - 3 // Push slightly back

      items.push({
        id: i,
        type: elementType.type,
        aspect: elementType.aspect,
        depth: elementType.depth,

        // Position
        position: [x, height, z],
        originalPosition: [x, height, z],

        // Rotation (slight random tilt)
        rotation: [
          (Math.random() - 0.5) * 0.3,
          Math.random() * Math.PI * 2,
          (Math.random() - 0.5) * 0.2,
        ],
        originalRotation: [
          (Math.random() - 0.5) * 0.3,
          Math.random() * Math.PI * 2,
          (Math.random() - 0.5) * 0.2,
        ],

        // Scale
        scale: 0.8 + Math.random() * 0.6,

        // Physics properties
        driftSpeed: 0.1 + Math.random() * 0.2,
        bobSpeed: 0.3 + Math.random() * 0.3,
        bobAmplitude: 0.1 + Math.random() * 0.2,
        driftAmplitude: 0.15 + Math.random() * 0.1,
        rotateSpeed: 0.05 + Math.random() * 0.1,
        phase: Math.random() * Math.PI * 2,

        // Animation state
        opacity: 1,
        visible: true,
      })
    }

    elements.value = items
  }

  // Update physics for a single frame
  function updatePhysics(elapsed, scrollProgress = 0) {
    elements.value.forEach((element) => {
      if (!element.visible) return

      // Slow drift in X/Z plane
      const driftX = Math.sin(elapsed * element.driftSpeed + element.phase) * element.driftAmplitude
      const driftZ = Math.cos(elapsed * element.driftSpeed * 0.7 + element.phase) * element.driftAmplitude

      // Gentle vertical bob
      const bobY = Math.sin(elapsed * element.bobSpeed + element.phase) * element.bobAmplitude

      // Update position
      element.position[0] = element.originalPosition[0] + driftX
      element.position[1] = element.originalPosition[1] + bobY
      element.position[2] = element.originalPosition[2] + driftZ

      // Slow rotation
      element.rotation[1] = element.originalRotation[1] + elapsed * element.rotateSpeed
    })
  }

  // Prepare elements for transformation (shrink and move to center)
  function prepareForTransformation(progress) {
    const transformStart = 0.2 // When chaos starts shrinking
    const transformEnd = 0.6   // When chaos is fully collapsed

    if (progress < transformStart) return

    const t = Math.min(1, (progress - transformStart) / (transformEnd - transformStart))
    const eased = easeInPower3(t)

    elements.value.forEach((element) => {
      // Scale down
      const targetScale = element.scale * (1 - eased * 0.7)

      // Move toward center
      element.position[0] = element.originalPosition[0] * (1 - eased)
      element.position[1] = element.originalPosition[1] * (1 - eased)
      element.position[2] = element.originalPosition[2] * (1 - eased) - eased * 2

      // Fade out
      element.opacity = 1 - eased
      element.visible = element.opacity > 0.01
    })
  }

  // Reset elements to original state
  function resetElements() {
    elements.value.forEach((element) => {
      element.position = [...element.originalPosition]
      element.rotation = [...element.originalRotation]
      element.opacity = 1
      element.visible = true
    })
  }

  // Easing function
  function easeInPower3(t) {
    return t * t * t
  }

  onMounted(() => {
    initializeElements()
  })

  return {
    elements,
    updatePhysics,
    prepareForTransformation,
    resetElements,
    initializeElements,
  }
}
