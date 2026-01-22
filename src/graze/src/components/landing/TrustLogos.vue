<script setup>
/**
 * Section 4: Restaurant logos that morph to meal cards
 * Builds trust by showing familiar brands
 */
import { ref, computed, watch } from 'vue'
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

// Restaurant data (would come from API)
const restaurants = ref([
  { id: 1, name: 'Chipotle', dishes: 47, color: '#A62F21' },
  { id: 2, name: 'Sweetgreen', dishes: 38, color: '#1B5E20' },
  { id: 3, name: 'Panera', dishes: 52, color: '#4E7C31' },
  { id: 4, name: "Chick-fil-A", dishes: 34, color: '#E51636' },
  { id: 5, name: 'Chipotle', dishes: 41, color: '#A62F21' },
  { id: 6, name: 'Cava', dishes: 45, color: '#2D6A4F' },
])

// Animation state for each logo
const logoStates = ref(restaurants.value.map(() => ({
  scale: 0,
  opacity: 0,
  morphProgress: 0,
})))

// Animate logos when visible
watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    logoStates.value.forEach((state, index) => {
      gsap.to(state, {
        scale: 1,
        opacity: 1,
        duration: 0.5,
        delay: index * 0.1,
        ease: 'back.out(1.7)',
      })
    })
  }
}, { immediate: true })

// Morph effect based on progress
watch(() => props.progress, (progress) => {
  if (progress > 0.5) {
    const morphAmount = (progress - 0.5) * 2
    logoStates.value.forEach((state, index) => {
      state.morphProgress = Math.min(1, morphAmount + index * 0.05)
    })
  }
})

// Total dishes count animation
const totalDishes = computed(() => {
  return restaurants.value.reduce((sum, r) => sum + r.dishes, 0)
})
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="trust-section">
      <div class="section-header">
        <div class="badge">TRUSTED DATA</div>
        <h2 class="title">
          Real nutrition from
          <span class="highlight">real restaurants</span>
        </h2>
      </div>

      <div class="logo-grid">
        <div
          v-for="(restaurant, index) in restaurants"
          :key="restaurant.id"
          class="logo-card"
          :style="{
            transform: `scale(${logoStates[index].scale})`,
            opacity: logoStates[index].opacity,
            '--accent-color': restaurant.color,
          }"
        >
          <div class="logo-placeholder" :style="{ backgroundColor: restaurant.color + '20' }">
            <span class="logo-initial">{{ restaurant.name[0] }}</span>
          </div>
          <div class="restaurant-name">{{ restaurant.name }}</div>
          <div class="dish-count">{{ restaurant.dishes }} dishes</div>

          <!-- Morph overlay -->
          <div
            class="morph-overlay"
            :style="{ opacity: logoStates[index].morphProgress }"
          >
            <div class="meal-preview">
              <div class="preview-protein">46g</div>
              <div class="preview-label">avg protein</div>
            </div>
          </div>
        </div>
      </div>

      <div class="total-stats">
        <div class="stat">
          <span class="stat-value">{{ totalDishes }}+</span>
          <span class="stat-label">dishes analyzed</span>
        </div>
        <div class="stat">
          <span class="stat-value">28</span>
          <span class="stat-label">restaurants</span>
        </div>
        <div class="stat">
          <span class="stat-value">100%</span>
          <span class="stat-label">verified data</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.trust-section {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 900px;
  z-index: 10;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: #22c55e;
  margin-bottom: 1rem;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
}

.highlight {
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.logo-card {
  position: relative;
  background: rgba(20, 20, 20, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: border-color 0.3s ease;
  overflow: hidden;
}

.logo-card:hover {
  border-color: var(--accent-color);
}

.logo-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-initial {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-color);
}

.restaurant-name {
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.dish-count {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
}

.morph-overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 10, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.meal-preview {
  text-align: center;
}

.preview-protein {
  font-size: 2rem;
  font-weight: 700;
  color: #22c55e;
}

.preview-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.total-stats {
  display: flex;
  justify-content: center;
  gap: 4rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
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
  .logo-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .total-stats {
    flex-direction: column;
    gap: 1.5rem;
  }

  .title {
    font-size: 1.75rem;
  }
}
</style>
