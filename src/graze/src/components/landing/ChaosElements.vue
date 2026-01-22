<script setup>
/**
 * Floating chaos elements - menus, PDFs, spreadsheets, app screenshots
 * Creates the "overwhelming options" visual metaphor
 */
import { ref, onMounted, watch } from 'vue'
import { useRenderLoop } from '@tresjs/core'
import * as THREE from 'three'
import { useChaosPhysics } from '../../composables/useChaosPhysics'

const props = defineProps({
  scrollProgress: {
    type: Number,
    default: 0,
  },
  transformationProgress: {
    type: Number,
    default: 0,
  },
  activeSection: {
    type: Number,
    default: 0,
  },
})

const { elements, updatePhysics, prepareForTransformation } = useChaosPhysics(22)

// Colors for different element types (muted, document-like)
const getElementColor = (type) => {
  switch (type) {
    case 'menu': return '#3a3a3a'
    case 'pdf': return '#2d2d2d'
    case 'spreadsheet': return '#333333'
    case 'app': return '#363636'
    default: return '#303030'
  }
}

// Accent color for edge glow
const getAccentColor = (type, index) => {
  const colors = ['#22c55e', '#14b8a6', '#06b6d4', '#3b82f6', '#8b5cf6']
  return colors[index % colors.length]
}

// Animation loop
const { onLoop } = useRenderLoop()

onLoop(({ elapsed }) => {
  updatePhysics(elapsed, props.scrollProgress)

  // Apply transformation collapse if in transformation section
  if (props.activeSection === 1) {
    prepareForTransformation(props.transformationProgress)
  }
})
</script>

<template>
  <TresGroup>
    <TresGroup
      v-for="element in elements"
      :key="element.id"
      :position="element.position"
      :rotation="element.rotation"
      :visible="element.visible"
    >
      <!-- Main document plane -->
      <TresMesh :scale="[element.scale * element.aspect, element.scale, element.depth]">
        <TresBoxGeometry :args="[1.5, 2, 0.02]" />
        <TresMeshStandardMaterial
          :color="getElementColor(element.type)"
          :transparent="true"
          :opacity="element.opacity * 0.9"
          :metalness="0.1"
          :roughness="0.8"
        />
      </TresMesh>

      <!-- Content lines (to simulate text/data) -->
      <TresGroup :position="[0, 0, 0.015]">
        <!-- Header bar -->
        <TresMesh :position="[0, 0.7, 0]" :scale="[element.scale * element.aspect, element.scale, 1]">
          <TresPlaneGeometry :args="[1.2, 0.15]" />
          <TresMeshBasicMaterial
            :color="getAccentColor(element.type, element.id)"
            :transparent="true"
            :opacity="element.opacity * 0.3"
          />
        </TresMesh>

        <!-- Content lines -->
        <TresMesh
          v-for="line in 5"
          :key="line"
          :position="[0, 0.4 - line * 0.25, 0]"
          :scale="[element.scale * element.aspect, element.scale, 1]"
        >
          <TresPlaneGeometry :args="[1.0 - (line % 2) * 0.3, 0.06]" />
          <TresMeshBasicMaterial
            color="#4a4a4a"
            :transparent="true"
            :opacity="element.opacity * 0.4"
          />
        </TresMesh>
      </TresGroup>

      <!-- Edge glow -->
      <TresMesh :scale="[element.scale * element.aspect * 1.02, element.scale * 1.02, 0.01]">
        <TresBoxGeometry :args="[1.5, 2, 0.02]" />
        <TresMeshBasicMaterial
          :color="getAccentColor(element.type, element.id)"
          :transparent="true"
          :opacity="element.opacity * 0.1"
        />
      </TresMesh>
    </TresGroup>
  </TresGroup>
</template>
