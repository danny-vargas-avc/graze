<script setup>
import { ref, onMounted, computed } from 'vue'
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

// Connection nodes for the neural network effect
const nodes = ref([])
const connections = ref([])

// Generate network on mount
onMounted(() => {
  const nodeCount = 15
  const nodeList = []

  // Create nodes in a spherical distribution
  for (let i = 0; i < nodeCount; i++) {
    const phi = Math.acos(-1 + (2 * i) / nodeCount)
    const theta = Math.sqrt(nodeCount * Math.PI) * phi
    const radius = 6 + Math.random() * 3

    nodeList.push({
      id: i,
      x: radius * Math.cos(theta) * Math.sin(phi),
      y: radius * Math.sin(theta) * Math.sin(phi),
      z: radius * Math.cos(phi),
      originalX: radius * Math.cos(theta) * Math.sin(phi),
      originalY: radius * Math.sin(theta) * Math.sin(phi),
      originalZ: radius * Math.cos(phi),
      phase: Math.random() * Math.PI * 2,
      speed: 0.2 + Math.random() * 0.3,
      color: getNodeColor(i),
    })
  }

  nodes.value = nodeList

  // Create connections between nodes
  const connList = []
  for (let i = 0; i < nodeList.length; i++) {
    for (let j = i + 1; j < nodeList.length; j++) {
      const dx = nodeList[i].x - nodeList[j].x
      const dy = nodeList[i].y - nodeList[j].y
      const dz = nodeList[i].z - nodeList[j].z
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz)

      if (dist < 8 && connList.length < 25) {
        connList.push({
          id: `${i}-${j}`,
          startNode: i,
          endNode: j,
          opacity: Math.max(0.15, 1 - dist / 8),
          pulsePhase: Math.random() * Math.PI * 2,
          color: getConnectionColor(i, j),
        })
      }
    }
  }

  connections.value = connList
})

function getNodeColor(i) {
  const colors = ['#22c55e', '#14b8a6', '#06b6d4', '#3b82f6', '#8b5cf6']
  return colors[i % colors.length]
}

function getConnectionColor(i, j) {
  const colors = ['#22c55e', '#14b8a6', '#06b6d4']
  return colors[(i + j) % colors.length]
}

// Animation loop
const { onLoop } = useRenderLoop()

onLoop(({ elapsed }) => {
  if (!nodes.value.length) return

  nodes.value.forEach((node) => {
    // Float animation
    const floatY = Math.sin(elapsed * node.speed + node.phase) * 0.4
    const floatX = Math.cos(elapsed * node.speed * 0.7 + node.phase) * 0.2
    node.x = node.originalX + floatX
    node.y = node.originalY + floatY
  })

  // Pulse connection opacity
  if (props.activeSection >= 2) {
    connections.value.forEach((conn) => {
      conn.opacity = 0.2 + Math.sin(elapsed * 1.5 + conn.pulsePhase) * 0.15
    })
  }
})

// Compute line points for each connection
const getConnectionMidpoint = (conn) => {
  const start = nodes.value[conn.startNode]
  const end = nodes.value[conn.endNode]
  if (!start || !end) return [0, 0, 0]
  return [
    (start.x + end.x) / 2,
    (start.y + end.y) / 2,
    (start.z + end.z) / 2,
  ]
}
</script>

<template>
  <TresGroup>
    <!-- Connection nodes (glowing spheres) -->
    <TresMesh
      v-for="node in nodes"
      :key="node.id"
      :position="[node.x, node.y, node.z]"
      v-show="activeSection >= 1"
    >
      <TresSphereGeometry :args="[0.12, 12, 12]" />
      <TresMeshBasicMaterial
        :color="node.color"
        :transparent="true"
        :opacity="activeSection >= 1 ? 0.9 : 0"
      />
    </TresMesh>

    <!-- Glow halos around nodes -->
    <TresMesh
      v-for="node in nodes"
      :key="`glow-${node.id}`"
      :position="[node.x, node.y, node.z]"
      v-show="activeSection >= 2"
    >
      <TresSphereGeometry :args="[0.25, 12, 12]" />
      <TresMeshBasicMaterial
        :color="node.color"
        :transparent="true"
        :opacity="0.15"
      />
    </TresMesh>

    <!-- Connection lines using cylinder primitives -->
    <TresGroup v-for="conn in connections" :key="conn.id" v-show="activeSection >= 1">
      <!-- Using a thin mesh to represent connection -->
      <TresMesh :position="getConnectionMidpoint(conn)">
        <TresSphereGeometry :args="[0.03, 4, 4]" />
        <TresMeshBasicMaterial
          :color="conn.color"
          :transparent="true"
          :opacity="activeSection >= 1 ? conn.opacity : 0"
        />
      </TresMesh>
    </TresGroup>

    <!-- Central energy core -->
    <TresMesh v-show="activeSection >= 2" :position="[0, 0, 0]">
      <TresSphereGeometry :args="[1, 32, 32]" />
      <TresMeshBasicMaterial
        color="#22c55e"
        :transparent="true"
        :opacity="0.08"
      />
    </TresMesh>

    <!-- Inner glow core -->
    <TresMesh v-show="activeSection >= 2" :position="[0, 0, 0]">
      <TresSphereGeometry :args="[0.5, 16, 16]" />
      <TresMeshBasicMaterial
        color="#14b8a6"
        :transparent="true"
        :opacity="0.15"
      />
    </TresMesh>

    <!-- Orbital rings -->
    <TresMesh
      v-show="activeSection >= 2"
      :position="[0, 0, 0]"
      :rotation="[Math.PI / 2, 0, 0]"
    >
      <TresRingGeometry :args="[5, 5.1, 64]" />
      <TresMeshBasicMaterial
        color="#22c55e"
        :transparent="true"
        :opacity="0.15"
        :side="2"
      />
    </TresMesh>

    <TresMesh
      v-show="activeSection >= 2"
      :position="[0, 0, 0]"
      :rotation="[Math.PI / 3, Math.PI / 4, 0]"
    >
      <TresRingGeometry :args="[4, 4.08, 64]" />
      <TresMeshBasicMaterial
        color="#14b8a6"
        :transparent="true"
        :opacity="0.1"
        :side="2"
      />
    </TresMesh>
  </TresGroup>
</template>
