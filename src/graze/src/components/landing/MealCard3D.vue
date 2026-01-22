<script setup>
/**
 * Individual 3D meal card with canvas texture
 * Displays restaurant, dish name, protein, and calories
 */
import { ref, onMounted, watch } from 'vue'
import * as THREE from 'three'

const props = defineProps({
  meal: {
    type: Object,
    required: true,
  },
  position: {
    type: Array,
    default: () => [0, 0, 0],
  },
  rotation: {
    type: Array,
    default: () => [0, 0, 0],
  },
  scale: {
    type: Number,
    default: 1,
  },
  highlighted: {
    type: Boolean,
    default: false,
  },
  opacity: {
    type: Number,
    default: 1,
  },
})

const meshRef = ref(null)
const texture = ref(null)

// Create canvas texture for meal card
function createMealTexture(meal) {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 256
  const ctx = canvas.getContext('2d')

  // Background
  ctx.fillStyle = '#1a1a1a'
  ctx.fillRect(0, 0, 512, 256)

  // Subtle border
  ctx.strokeStyle = '#333333'
  ctx.lineWidth = 2
  ctx.strokeRect(1, 1, 510, 254)

  // Restaurant name
  ctx.fillStyle = '#888888'
  ctx.font = '500 24px system-ui, sans-serif'
  ctx.fillText(meal.restaurant || 'Restaurant', 24, 45)

  // Dish name
  ctx.fillStyle = '#ffffff'
  ctx.font = '700 32px system-ui, sans-serif'

  // Wrap long dish names
  const dishName = meal.name || 'Dish Name'
  const maxWidth = 460
  const words = dishName.split(' ')
  let line = ''
  let y = 95

  for (let word of words) {
    const testLine = line + word + ' '
    const metrics = ctx.measureText(testLine)
    if (metrics.width > maxWidth && line !== '') {
      ctx.fillText(line.trim(), 24, y)
      line = word + ' '
      y += 38
    } else {
      line = testLine
    }
  }
  ctx.fillText(line.trim(), 24, y)

  // Protein value (green)
  ctx.fillStyle = '#22c55e'
  ctx.font = '700 42px system-ui, sans-serif'
  ctx.fillText(`${meal.protein || 0}g`, 24, 200)

  // Protein label
  ctx.fillStyle = '#666666'
  ctx.font = '400 18px system-ui, sans-serif'
  ctx.fillText('protein', 24, 225)

  // Calories (right aligned)
  ctx.fillStyle = '#888888'
  ctx.font = '600 28px system-ui, sans-serif'
  const calText = `${meal.calories || 0} cal`
  const calWidth = ctx.measureText(calText).width
  ctx.fillText(calText, 488 - calWidth, 200)

  // Efficiency indicator bar
  const efficiency = meal.protein && meal.calories
    ? (meal.protein / meal.calories) * 100
    : 0
  const barWidth = Math.min(efficiency * 4, 200)

  ctx.fillStyle = '#333333'
  ctx.fillRect(200, 220, 200, 8)

  const gradient = ctx.createLinearGradient(200, 0, 400, 0)
  gradient.addColorStop(0, '#22c55e')
  gradient.addColorStop(1, '#14b8a6')
  ctx.fillStyle = gradient
  ctx.fillRect(200, 220, barWidth, 8)

  return new THREE.CanvasTexture(canvas)
}

onMounted(() => {
  texture.value = createMealTexture(props.meal)
})

// Update texture when meal changes
watch(() => props.meal, (newMeal) => {
  texture.value = createMealTexture(newMeal)
}, { deep: true })
</script>

<template>
  <TresGroup
    :position="position"
    :rotation="rotation"
    :scale="[scale, scale, scale]"
  >
    <!-- Main card body -->
    <TresMesh ref="meshRef">
      <TresBoxGeometry :args="[2, 1, 0.05]" />
      <TresMeshStandardMaterial
        v-if="texture"
        :map="texture"
        :transparent="true"
        :opacity="opacity"
        :metalness="0.1"
        :roughness="0.8"
      />
      <TresMeshStandardMaterial
        v-else
        color="#1a1a1a"
        :transparent="true"
        :opacity="opacity"
      />
    </TresMesh>

    <!-- Highlight glow when selected -->
    <TresMesh v-if="highlighted" :scale="[1.05, 1.05, 1]">
      <TresBoxGeometry :args="[2, 1, 0.02]" />
      <TresMeshBasicMaterial
        color="#22c55e"
        :transparent="true"
        :opacity="0.2"
      />
    </TresMesh>

    <!-- Edge accent -->
    <TresMesh :position="[0, 0, -0.03]">
      <TresBoxGeometry :args="[2.02, 1.02, 0.01]" />
      <TresMeshBasicMaterial
        :color="highlighted ? '#22c55e' : '#333333'"
        :transparent="true"
        :opacity="opacity * (highlighted ? 0.5 : 0.3)"
      />
    </TresMesh>
  </TresGroup>
</template>
