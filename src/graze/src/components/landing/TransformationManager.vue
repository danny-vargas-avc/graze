<script setup>
/**
 * Orchestrates the chaos-to-grid collapse animation
 * Manages transition states and timing
 */
import { computed, watch } from 'vue'
import { useTransformation } from '../../composables/useTransformation'

const props = defineProps({
  progress: {
    type: Number,
    default: 0,
  },
})

const {
  updateTransformation,
  getChaosCollapseProgress,
  getMealCardProgress,
} = useTransformation()

// Update transformation based on progress
watch(() => props.progress, (progress) => {
  updateTransformation(progress)
}, { immediate: true })

// Visual indicators for collapse center
const collapseProgress = computed(() => getChaosCollapseProgress(props.progress))
const showCollapseIndicator = computed(() => collapseProgress.value > 0 && collapseProgress.value < 1)

// Glow intensity increases as collapse happens
const glowIntensity = computed(() => {
  if (props.progress < 0.2) return 0
  if (props.progress > 0.6) return 0
  return Math.sin((props.progress - 0.2) / 0.4 * Math.PI) * 0.5
})
</script>

<template>
  <TresGroup>
    <!-- Central collapse point indicator -->
    <TresGroup v-if="showCollapseIndicator">
      <!-- Inner glow sphere -->
      <TresMesh :position="[0, 0, -2]">
        <TresSphereGeometry :args="[0.3 + collapseProgress * 0.5, 16, 16]" />
        <TresMeshBasicMaterial
          color="#22c55e"
          :transparent="true"
          :opacity="glowIntensity * 0.3"
        />
      </TresMesh>

      <!-- Outer glow ring -->
      <TresMesh :position="[0, 0, -2]" :rotation="[Math.PI / 2, 0, 0]">
        <TresRingGeometry :args="[1 - collapseProgress * 0.5, 1.2 - collapseProgress * 0.4, 32]" />
        <TresMeshBasicMaterial
          color="#14b8a6"
          :transparent="true"
          :opacity="glowIntensity * 0.2"
          :side="2"
        />
      </TresMesh>

      <!-- Particle burst effect at peak -->
      <TresMesh
        v-if="collapseProgress > 0.8"
        :position="[0, 0, -2]"
        :scale="[1 + (collapseProgress - 0.8) * 5, 1 + (collapseProgress - 0.8) * 5, 1]"
      >
        <TresSphereGeometry :args="[0.5, 8, 8]" />
        <TresMeshBasicMaterial
          color="#06b6d4"
          :transparent="true"
          :opacity="(1 - collapseProgress) * 0.5"
          :wireframe="true"
        />
      </TresMesh>
    </TresGroup>
  </TresGroup>
</template>
