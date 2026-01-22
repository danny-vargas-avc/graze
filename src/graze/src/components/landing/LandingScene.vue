<script setup>
/**
 * Main TresCanvas for the landing page
 * Manages 3D scene, camera, and lighting
 */
import { ref, watch, computed } from 'vue'
import { TresCanvas } from '@tresjs/core'
import { Stars } from '@tresjs/cientos'
import ChaosElements from './ChaosElements.vue'
import TransformationManager from './TransformationManager.vue'
import MealGrid from './MealGrid.vue'
import MacroSpace from './MacroSpace.vue'

const props = defineProps({
  scrollProgress: {
    type: Number,
    default: 0,
  },
  activeSection: {
    type: Number,
    default: 0,
  },
  transformationProgress: {
    type: Number,
    default: 0,
  },
})

// Camera follows scroll
const cameraPosition = ref([0, 0, 12])
const cameraTarget = ref([0, 0, 0])

// Update camera based on section
watch(() => props.activeSection, (section) => {
  switch (section) {
    case 0: // Hero - Wide view of chaos
      cameraPosition.value = [0, 0, 12]
      cameraTarget.value = [0, 0, 0]
      break
    case 1: // Transformation - Pull back slightly
      cameraPosition.value = [0, 0, 14]
      cameraTarget.value = [0, 0, 0]
      break
    case 2: // Macro Space - Orbit around
      cameraPosition.value = [5, 3, 10]
      cameraTarget.value = [0, 0, 0]
      break
    case 3: // Speed - Side view
      cameraPosition.value = [-3, 0, 12]
      cameraTarget.value = [0, 0, 0]
      break
    case 4: // Trust - Front view
      cameraPosition.value = [0, 0, 10]
      cameraTarget.value = [0, 0, 0]
      break
    case 5: // Zillow - Slight angle
      cameraPosition.value = [2, 1, 11]
      cameraTarget.value = [0, 0, 0]
      break
    case 6: // CTA - Close up
      cameraPosition.value = [0, 0, 6]
      cameraTarget.value = [0, 0, 0]
      break
  }
}, { immediate: true })

// Show chaos only in hero and transformation
const showChaos = computed(() => props.activeSection <= 1)

// Show meal grid after transformation starts
const showMealGrid = computed(() => props.activeSection >= 1 && props.transformationProgress > 0.4)

// Show macro space in section 2
const showMacroSpace = computed(() => props.activeSection === 2)
</script>

<template>
  <TresCanvas
    clear-color="#0a0a0a"
    :alpha="true"
    :antialias="true"
    window-size
  >
    <!-- Camera -->
    <TresPerspectiveCamera
      :position="cameraPosition"
      :look-at="cameraTarget"
      :fov="50"
    />

    <!-- Ambient light -->
    <TresAmbientLight :intensity="0.4" />

    <!-- Key light (green tint) -->
    <TresDirectionalLight
      :position="[10, 10, 5]"
      :intensity="0.6"
      color="#22c55e"
    />

    <!-- Fill light (cyan tint) -->
    <TresDirectionalLight
      :position="[-10, -5, 5]"
      :intensity="0.3"
      color="#06b6d4"
    />

    <!-- Rim light -->
    <TresPointLight
      :position="[0, 5, -5]"
      :intensity="0.5"
      color="#ffffff"
      :distance="20"
    />

    <!-- Stars background -->
    <Stars
      :radius="80"
      :depth="40"
      :count="2000"
      :factor="3"
      :saturation="0"
      :fade="true"
    />

    <!-- Chaos elements (floating menus, PDFs) -->
    <ChaosElements
      v-if="showChaos"
      :scroll-progress="scrollProgress"
      :transformation-progress="transformationProgress"
      :active-section="activeSection"
    />

    <!-- Transformation manager -->
    <TransformationManager
      v-if="activeSection === 1"
      :progress="transformationProgress"
    />

    <!-- Meal grid (appears after transformation) -->
    <MealGrid
      v-if="showMealGrid"
      :progress="transformationProgress"
      :active-section="activeSection"
    />

    <!-- Macro space (section 2) -->
    <MacroSpace
      :progress="scrollProgress"
      :visible="showMacroSpace"
    />

    <!-- Fog for depth -->
    <TresFog color="#0a0a0a" :near="10" :far="30" />
  </TresCanvas>
</template>
