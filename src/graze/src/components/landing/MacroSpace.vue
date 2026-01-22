<script setup>
/**
 * Section 2: 3D nutrition axes visualization
 * Shows meals positioned on protein/carbs/fat axes
 */
import { ref, computed, onMounted } from 'vue'
import { useRenderLoop } from '@tresjs/core'
import MealCard3D from './MealCard3D.vue'

const props = defineProps({
  progress: {
    type: Number,
    default: 0,
  },
  visible: {
    type: Boolean,
    default: false,
  },
})

// Sample meals positioned by their macros
const meals = ref([
  { id: 1, name: 'Grilled Chicken', restaurant: 'Chipotle', protein: 52, calories: 380, carbs: 12, fat: 14 },
  { id: 2, name: 'Salmon Bowl', restaurant: 'Sweetgreen', protein: 42, calories: 520, carbs: 35, fat: 22 },
  { id: 3, name: 'Steak Burrito', restaurant: 'Qdoba', protein: 38, calories: 680, carbs: 55, fat: 28 },
  { id: 4, name: 'Tofu Salad', restaurant: 'Panera', protein: 24, calories: 320, carbs: 28, fat: 16 },
])

// Convert macro values to 3D positions
const mealPositions = computed(() => {
  return meals.value.map(meal => {
    // Normalize values to -3 to 3 range
    const x = (meal.protein / 60) * 6 - 3  // Protein on X axis
    const y = (meal.carbs / 60) * 6 - 3    // Carbs on Y axis
    const z = (meal.fat / 40) * 4 - 2      // Fat on Z axis

    return {
      meal,
      position: [x * props.progress, y * props.progress, z * props.progress],
      scale: 0.6 * props.progress,
      opacity: props.progress,
    }
  })
})

// Axis labels
const axisLength = 4

// Rotation for orbit effect
const groupRotation = ref([0, 0, 0])
const { onLoop } = useRenderLoop()

onLoop(({ elapsed }) => {
  if (props.visible) {
    groupRotation.value = [
      Math.sin(elapsed * 0.2) * 0.1,
      elapsed * 0.15,
      0,
    ]
  }
})
</script>

<template>
  <TresGroup v-if="visible" :rotation="groupRotation">
    <!-- X Axis (Protein - Green) -->
    <TresMesh :position="[0, 0, 0]">
      <TresCylinderGeometry :args="[0.02, 0.02, axisLength * 2, 8]" />
      <TresMeshBasicMaterial color="#22c55e" :transparent="true" :opacity="0.6" />
    </TresMesh>
    <TresMesh :rotation="[0, 0, Math.PI / 2]" :position="[0, 0, 0]">
      <TresCylinderGeometry :args="[0.02, 0.02, axisLength * 2, 8]" />
      <TresMeshBasicMaterial color="#22c55e" :transparent="true" :opacity="0.6" />
    </TresMesh>

    <!-- Y Axis (Carbs - Blue) -->
    <TresMesh :position="[0, 0, 0]">
      <TresCylinderGeometry :args="[0.02, 0.02, axisLength * 2, 8]" />
      <TresMeshBasicMaterial color="#3b82f6" :transparent="true" :opacity="0.6" />
    </TresMesh>

    <!-- Z Axis (Fat - Orange) -->
    <TresMesh :rotation="[Math.PI / 2, 0, 0]" :position="[0, 0, 0]">
      <TresCylinderGeometry :args="[0.02, 0.02, axisLength * 2, 8]" />
      <TresMeshBasicMaterial color="#f97316" :transparent="true" :opacity="0.6" />
    </TresMesh>

    <!-- Axis endpoint markers -->
    <!-- Protein + -->
    <TresMesh :position="[axisLength, 0, 0]">
      <TresSphereGeometry :args="[0.1, 12, 12]" />
      <TresMeshBasicMaterial color="#22c55e" />
    </TresMesh>
    <!-- Carbs + -->
    <TresMesh :position="[0, axisLength, 0]">
      <TresSphereGeometry :args="[0.1, 12, 12]" />
      <TresMeshBasicMaterial color="#3b82f6" />
    </TresMesh>
    <!-- Fat + -->
    <TresMesh :position="[0, 0, axisLength]">
      <TresSphereGeometry :args="[0.1, 12, 12]" />
      <TresMeshBasicMaterial color="#f97316" />
    </TresMesh>

    <!-- Grid planes (subtle) -->
    <TresMesh :position="[0, 0, 0]" :rotation="[Math.PI / 2, 0, 0]">
      <TresPlaneGeometry :args="[8, 8, 8, 8]" />
      <TresMeshBasicMaterial
        color="#22c55e"
        :transparent="true"
        :opacity="0.05"
        :wireframe="true"
      />
    </TresMesh>

    <!-- Meal cards positioned by macros -->
    <MealCard3D
      v-for="item in mealPositions"
      :key="item.meal.id"
      :meal="item.meal"
      :position="item.position"
      :scale="item.scale"
      :opacity="item.opacity"
    />
  </TresGroup>
</template>
