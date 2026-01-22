<script setup>
/**
 * Section 3: Speed comparison - Split screen timers
 * Shows 27 minutes manual search vs 4 seconds with Graze
 */
import { ref, computed, watch, onMounted } from 'vue'
import { gsap } from 'gsap'

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

// Timer values
const manualTime = ref(0)      // Counts up to 27:00
const grazeTime = ref(0)       // Counts up to 4.2s

// Format time for display
const formatManualTime = computed(() => {
  const minutes = Math.floor(manualTime.value / 60)
  const seconds = Math.floor(manualTime.value % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const formatGrazeTime = computed(() => {
  return `${grazeTime.value.toFixed(1)}s`
})

// Animate timers when visible
watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    // Manual timer - slow count
    gsap.to(manualTime, {
      value: 1620, // 27 minutes in seconds
      duration: 3,
      ease: 'power2.out',
    })

    // Graze timer - quick flash
    gsap.to(grazeTime, {
      value: 4.2,
      duration: 0.5,
      delay: 0.5,
      ease: 'power3.out',
    })
  }
}, { immediate: true })

// Visual progress bars
const manualProgress = computed(() => Math.min(100, (manualTime.value / 1620) * 100))
const grazeProgress = computed(() => Math.min(100, (grazeTime.value / 4.2) * 100))
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="speed-comparison">
      <div class="comparison-grid">
        <!-- Manual search side -->
        <div class="side manual">
          <div class="side-label">Manual Search</div>
          <div class="timer manual-timer">{{ formatManualTime }}</div>
          <div class="progress-bar">
            <div class="progress-fill manual-fill" :style="{ width: manualProgress + '%' }"></div>
          </div>
          <div class="description">
            Googling restaurants, checking menus, comparing nutrition facts...
          </div>
        </div>

        <!-- Divider -->
        <div class="divider">
          <span class="vs">VS</span>
        </div>

        <!-- Graze side -->
        <div class="side graze">
          <div class="side-label">With Graze</div>
          <div class="timer graze-timer">{{ formatGrazeTime }}</div>
          <div class="progress-bar">
            <div class="progress-fill graze-fill" :style="{ width: grazeProgress + '%' }"></div>
          </div>
          <div class="description">
            Filter, compare, decide.
          </div>
        </div>
      </div>

      <div class="savings">
        <span class="savings-value">99.7%</span>
        <span class="savings-label">faster</span>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.speed-comparison {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 900px;
  z-index: 10;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: center;
}

.side {
  text-align: center;
  padding: 2rem;
  background: rgba(10, 10, 10, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.side-label {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 1rem;
}

.timer {
  font-size: 3rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 1rem;
}

.manual-timer {
  color: #ef4444;
}

.graze-timer {
  color: #22c55e;
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.manual-fill {
  background: linear-gradient(90deg, #ef4444, #f97316);
}

.graze-fill {
  background: linear-gradient(90deg, #22c55e, #14b8a6);
}

.description {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.5;
}

.divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.vs {
  font-size: 1.25rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.savings {
  text-align: center;
  margin-top: 2rem;
}

.savings-value {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.savings-label {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 0.5rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .comparison-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .divider {
    flex-direction: row;
  }

  .timer {
    font-size: 2rem;
  }
}
</style>
