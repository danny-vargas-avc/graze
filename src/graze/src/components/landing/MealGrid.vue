<script setup>
/**
 * 3D grid of meal cards that emerge from chaos
 * Positions cards in a visually appealing arrangement
 */
import { ref, computed, onMounted } from 'vue'
import { useRenderLoop } from '@tresjs/core'
import MealCard3D from './MealCard3D.vue'
import { useTransformation } from '../../composables/useTransformation'

const props = defineProps({
  progress: {
    type: Number,
    default: 0,
  },
  activeSection: {
    type: Number,
    default: 1,
  },
})

const { getMealCardProgress, getHighlightProgress, easeOutBack } = useTransformation()

// Sample meal data (would come from API in production)
const meals = ref([
  { id: 1, name: 'Grilled Chicken Bowl', restaurant: 'Chipotle', protein: 52, calories: 510 },
  { id: 2, name: 'Salmon Teriyaki', restaurant: 'Sweetgreen', protein: 46, calories: 580 },
  { id: 3, name: 'Turkey Club Wrap', restaurant: 'Panera', protein: 41, calories: 490 },
  { id: 4, name: 'Steak Burrito Bowl', restaurant: 'Chipotle', protein: 48, calories: 620 },
  { id: 5, name: 'Tuna Poke Bowl', restaurant: 'Sweetgreen', protein: 44, calories: 460 },
  { id: 6, name: 'BBQ Chicken Salad', restaurant: 'Chick-fil-A', protein: 43, calories: 520 },
])

// Grid positions for cards
const gridPositions = [
  [-2.5, 0.8, 0],   // Top left
  [0, 0.8, 0],      // Top center
  [2.5, 0.8, 0],    // Top right
  [-2.5, -0.8, 0],  // Bottom left
  [0, -0.8, 0],     // Bottom center (best match)
  [2.5, -0.8, 0],   // Bottom right
]

// Calculate emergence animation for each card
const cardStates = computed(() => {
  const baseProgress = getMealCardProgress(props.progress)

  return meals.value.map((meal, index) => {
    // Stagger card emergence
    const staggerDelay = index * 0.1
    const cardProgress = Math.max(0, Math.min(1, (baseProgress - staggerDelay) / 0.5))
    const easedProgress = cardProgress > 0 ? easeOutBack(cardProgress) : 0

    // Highlight progress for best match (card at index 4)
    const highlightProgress = getHighlightProgress(props.progress)
    const isBestMatch = index === 4
    const isHighlighted = isBestMatch && highlightProgress > 0.5

    // Position with emergence animation
    const targetPos = gridPositions[index] || [0, 0, 0]
    const startZ = -5
    const currentZ = startZ + (targetPos[2] - startZ) * easedProgress

    // Best match floats forward when highlighted
    const highlightZ = isBestMatch ? highlightProgress * 2 : 0

    return {
      meal,
      position: [
        targetPos[0] * easedProgress,
        targetPos[1] * easedProgress,
        currentZ + highlightZ,
      ],
      scale: easedProgress * (isHighlighted ? 1.2 : 1),
      opacity: Math.min(1, cardProgress * 2),
      highlighted: isHighlighted,
      rotation: [
        (1 - easedProgress) * 0.5 * (index % 2 ? 1 : -1),
        (1 - easedProgress) * 0.3,
        0,
      ],
    }
  })
})

// Gentle float animation
const floatOffset = ref(0)
const { onLoop } = useRenderLoop()

onLoop(({ elapsed }) => {
  floatOffset.value = Math.sin(elapsed * 0.5) * 0.05
})
</script>

<template>
  <TresGroup :position="[0, floatOffset, 0]">
    <MealCard3D
      v-for="(card, index) in cardStates"
      :key="meals[index].id"
      :meal="card.meal"
      :position="card.position"
      :rotation="card.rotation"
      :scale="card.scale"
      :opacity="card.opacity"
      :highlighted="card.highlighted"
    />
  </TresGroup>
</template>
