<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRenderLoop } from '@tresjs/core'
import * as THREE from 'three'

const props = defineProps({
  scrollProgress: {
    type: Number,
    default: 0,
  },
  activeSection: {
    type: Number,
    default: 0,
  },
})

// Generate food items with random positions
const foodItems = ref([])
const groupRef = ref(null)

// Food types with colors (representing different macro profiles)
const foodTypes = [
  { type: 'bowl', color: '#22c55e', protein: 'high' },      // High protein - green
  { type: 'plate', color: '#14b8a6', protein: 'high' },     // High protein - teal
  { type: 'bowl', color: '#3b82f6', protein: 'medium' },    // Medium - blue
  { type: 'cube', color: '#8b5cf6', protein: 'medium' },    // Medium - purple
  { type: 'sphere', color: '#f97316', protein: 'low' },     // Low - orange
  { type: 'cube', color: '#ef4444', protein: 'low' },       // Low - red
]

// Initialize food items
onMounted(() => {
  const items = []
  const count = 60

  for (let i = 0; i < count; i++) {
    const foodType = foodTypes[Math.floor(Math.random() * foodTypes.length)]
    const angle = Math.random() * Math.PI * 2
    const radius = 5 + Math.random() * 15
    const height = (Math.random() - 0.5) * 20

    items.push({
      id: i,
      position: [
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius,
      ],
      originalPosition: [
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius,
      ],
      rotation: [
        Math.random() * Math.PI,
        Math.random() * Math.PI,
        Math.random() * Math.PI,
      ],
      scale: 0.3 + Math.random() * 0.5,
      type: foodType.type,
      color: foodType.color,
      protein: foodType.protein,
      speed: 0.2 + Math.random() * 0.5,
      phase: Math.random() * Math.PI * 2,
      opacity: 1,
      // For filtering animation
      isFiltered: foodType.protein === 'high',
    })
  }

  foodItems.value = items
})

// Animation loop
const { onLoop } = useRenderLoop()

onLoop(({ elapsed }) => {
  if (!foodItems.value.length) return

  foodItems.value.forEach((item, index) => {
    // Floating animation
    const floatY = Math.sin(elapsed * item.speed + item.phase) * 0.5
    const floatX = Math.cos(elapsed * item.speed * 0.5 + item.phase) * 0.3

    // Base position with float
    let targetX = item.originalPosition[0] + floatX
    let targetY = item.originalPosition[1] + floatY
    let targetZ = item.originalPosition[2]

    // Filter animation (section 1)
    if (props.activeSection >= 1) {
      if (item.isFiltered) {
        // High protein items cluster in center and glow
        const clusterRadius = 4
        const clusterAngle = (index / foodItems.value.filter(f => f.isFiltered).length) * Math.PI * 2
        targetX = Math.cos(clusterAngle) * clusterRadius
        targetY = Math.sin(clusterAngle * 2) * 2
        targetZ = Math.sin(clusterAngle) * clusterRadius
        item.opacity = 1
      } else {
        // Non-matching items fade and drift away
        targetX = item.originalPosition[0] * 2
        targetY = item.originalPosition[1] + (props.scrollProgress * 10)
        targetZ = item.originalPosition[2] * 2
        item.opacity = Math.max(0, 1 - props.scrollProgress * 2)
      }
    }

    // Logo formation (section 3)
    if (props.activeSection >= 3) {
      // Form a loose ring/logo shape
      const logoAngle = (index / foodItems.value.length) * Math.PI * 2
      const logoRadius = 6 + Math.sin(logoAngle * 3) * 2
      targetX = Math.cos(logoAngle) * logoRadius
      targetY = Math.sin(logoAngle * 4) * 1
      targetZ = Math.sin(logoAngle) * logoRadius - 5
      item.opacity = 1
    }

    // Smooth lerp to target
    item.position[0] += (targetX - item.position[0]) * 0.02
    item.position[1] += (targetY - item.position[1]) * 0.02
    item.position[2] += (targetZ - item.position[2]) * 0.02

    // Rotation
    item.rotation[0] += 0.002 * item.speed
    item.rotation[1] += 0.003 * item.speed
  })
})

// Geometry components based on type
const getGeometry = (type) => {
  switch (type) {
    case 'bowl':
      return { is: 'TresTorusGeometry', args: [1, 0.4, 16, 32] }
    case 'plate':
      return { is: 'TresCylinderGeometry', args: [1, 1, 0.2, 32] }
    case 'cube':
      return { is: 'TresBoxGeometry', args: [1, 1, 1] }
    case 'sphere':
      return { is: 'TresSphereGeometry', args: [0.6, 16, 16] }
    default:
      return { is: 'TresSphereGeometry', args: [0.5, 16, 16] }
  }
}
</script>

<template>
  <TresGroup ref="groupRef">
    <TresGroup
      v-for="item in foodItems"
      :key="item.id"
      :position="item.position"
      :rotation="item.rotation"
      :scale="[item.scale, item.scale, item.scale]"
    >
      <!-- Main shape -->
      <TresMesh>
        <component
          :is="getGeometry(item.type).is"
          :args="getGeometry(item.type).args"
        />
        <TresMeshStandardMaterial
          :color="item.color"
          :emissive="item.color"
          :emissive-intensity="item.isFiltered && activeSection >= 1 ? 0.5 : 0.1"
          :transparent="true"
          :opacity="item.opacity"
          :metalness="0.3"
          :roughness="0.7"
        />
      </TresMesh>

      <!-- Glow ring for high-protein items -->
      <TresMesh
        v-if="item.isFiltered && activeSection >= 1"
        :scale="[1.3, 1.3, 1.3]"
      >
        <TresRingGeometry :args="[0.8, 1, 32]" />
        <TresMeshBasicMaterial
          :color="item.color"
          :transparent="true"
          :opacity="0.3"
          :side="2"
        />
      </TresMesh>
    </TresGroup>
  </TresGroup>
</template>
