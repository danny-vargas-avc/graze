<script setup>
/**
 * Typewriter filter overlay - 2D element over 3D scene
 * Types out the filter criteria during transformation
 */
import { computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  visible: {
    type: Boolean,
    default: false,
  },
  progress: {
    type: Number,
    default: 0,
  },
})

// Cursor blink state
const showCursor = computed(() => {
  return props.text.length < 32 // Full text length
})

// Parse text to highlight values
const formattedText = computed(() => {
  const text = props.text
  // Highlight numbers and operators
  return text
    .replace(/(>=|<=)/g, '<span class="operator">$1</span>')
    .replace(/(\d+g)/g, '<span class="protein">$1</span>')
    .replace(/(\d+) calories/g, '<span class="calories">$1</span> calories')
})
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="typewriter-container">
      <div class="typewriter-box">
        <span class="typewriter-text" v-html="formattedText"></span>
        <span v-if="showCursor" class="cursor">|</span>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.typewriter-container {
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  pointer-events: none;
}

.typewriter-box {
  background: rgba(10, 10, 10, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 12px;
  padding: 1rem 2rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.1);
}

.typewriter-text {
  white-space: nowrap;
}

.typewriter-text :deep(.operator) {
  color: #22c55e;
  font-weight: 600;
}

.typewriter-text :deep(.protein) {
  color: #22c55e;
  font-weight: 700;
}

.typewriter-text :deep(.calories) {
  color: #eab308;
  font-weight: 700;
}

.cursor {
  display: inline-block;
  color: #22c55e;
  animation: blink 0.8s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
