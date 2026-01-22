<script setup>
import { ref, watch, onMounted } from 'vue'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, Stars } from '@tresjs/cientos'
import FoodParticles from './FoodParticles.vue'
import MacroConnections from './MacroConnections.vue'

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

const cameraPosition = ref([0, 0, 20])
const cameraTarget = ref([0, 0, 0])

// Update camera based on scroll
watch(() => props.scrollProgress, (progress) => {
  const z = 20 - progress * 8
  const y = progress * 5
  cameraPosition.value = [0, y, z]
})
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
      :fov="60"
    />

    <!-- Ambient light -->
    <TresAmbientLight :intensity="0.3" />

    <!-- Directional lights for depth -->
    <TresDirectionalLight
      :position="[10, 10, 5]"
      :intensity="0.8"
      color="#22c55e"
    />
    <TresDirectionalLight
      :position="[-10, -10, -5]"
      :intensity="0.4"
      color="#06b6d4"
    />

    <!-- Point lights for glow effect -->
    <TresPointLight
      :position="[0, 5, 0]"
      :intensity="1"
      color="#22c55e"
      :distance="30"
    />

    <!-- Stars background -->
    <Stars
      :radius="100"
      :depth="50"
      :count="3000"
      :factor="4"
      :saturation="0"
      :fade="true"
    />

    <!-- Food particles -->
    <FoodParticles
      :scroll-progress="scrollProgress"
      :active-section="activeSection"
    />

    <!-- Macro connections (glowing lines) -->
    <MacroConnections
      :scroll-progress="scrollProgress"
      :active-section="activeSection"
    />

    <!-- Fog for depth -->
    <TresFog color="#0a0a0a" :near="15" :far="40" />
  </TresCanvas>
</template>
