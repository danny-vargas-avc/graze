<script setup>
/**
 * Section 6: Final CTA - All meals collapse to single best match
 * Creates urgency and drives conversion
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

// The "perfect" meal that everything collapses to
const perfectMeal = ref({
  name: 'Grilled Chicken Power Bowl',
  restaurant: 'Chipotle',
  protein: 52,
  calories: 510,
  carbs: 32,
  fat: 18,
})

// Animation states
const cardScale = ref(0)
const showStats = ref(false)
const showCta = ref(false)

watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    // Card zooms in
    gsap.to(cardScale, {
      value: 1,
      duration: 0.8,
      ease: 'back.out(1.7)',
      delay: 0.2,
    })

    // Stats fade in
    setTimeout(() => {
      showStats.value = true
    }, 600)

    // CTA appears
    setTimeout(() => {
      showCta.value = true
    }, 1000)
  }
}, { immediate: true })

// Efficiency calculation
const efficiency = computed(() => {
  return ((perfectMeal.value.protein / perfectMeal.value.calories) * 100).toFixed(1)
})
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="final-cta">
      <!-- The One Card -->
      <div class="hero-card" :style="{ transform: `scale(${cardScale})` }">
        <div class="card-glow"></div>

        <div class="card-content">
          <div class="card-badge">Your Perfect Match</div>

          <div class="restaurant">{{ perfectMeal.restaurant }}</div>
          <h3 class="dish-name">{{ perfectMeal.name }}</h3>

          <div class="macro-grid" :class="{ 'visible': showStats }">
            <div class="macro-item protein">
              <span class="macro-value">{{ perfectMeal.protein }}g</span>
              <span class="macro-label">protein</span>
            </div>
            <div class="macro-item calories">
              <span class="macro-value">{{ perfectMeal.calories }}</span>
              <span class="macro-label">calories</span>
            </div>
            <div class="macro-item carbs">
              <span class="macro-value">{{ perfectMeal.carbs }}g</span>
              <span class="macro-label">carbs</span>
            </div>
            <div class="macro-item fat">
              <span class="macro-value">{{ perfectMeal.fat }}g</span>
              <span class="macro-label">fat</span>
            </div>
          </div>

          <div class="efficiency-bar" :class="{ 'visible': showStats }">
            <div class="efficiency-label">Protein Efficiency</div>
            <div class="efficiency-track">
              <div class="efficiency-fill" :style="{ width: efficiency + '%' }"></div>
            </div>
            <div class="efficiency-value">{{ efficiency }}%</div>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <div class="cta-area" :class="{ 'visible': showCta }">
        <h2 class="cta-title">
          Find yours in
          <span class="highlight">seconds</span>
        </h2>
        <p class="cta-subtitle">
          487 dishes. 28 restaurants. One perfect match.
        </p>
        <router-link to="/search" class="cta-button">
          <span>Start Searching</span>
          <svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </router-link>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.final-cta {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 600px;
  z-index: 10;
  text-align: center;
}

.hero-card {
  position: relative;
  background: rgba(15, 15, 15, 0.95);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.card-glow {
  position: absolute;
  inset: -2px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(20, 184, 166, 0.2));
  filter: blur(20px);
  z-index: -1;
}

.card-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1rem;
}

.restaurant {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.25rem;
}

.dish-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
}

.macro-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.5s ease;
}

.macro-grid.visible {
  opacity: 1;
  transform: translateY(0);
}

.macro-item {
  text-align: center;
}

.macro-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
}

.macro-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.macro-item.protein .macro-value {
  color: #22c55e;
}

.macro-item.calories .macro-value {
  color: #eab308;
}

.macro-item.carbs .macro-value {
  color: #3b82f6;
}

.macro-item.fat .macro-value {
  color: #f97316;
}

.efficiency-bar {
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.5s ease 0.2s;
}

.efficiency-bar.visible {
  opacity: 1;
  transform: translateY(0);
}

.efficiency-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.5rem;
}

.efficiency-track {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.efficiency-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #14b8a6);
  border-radius: 4px;
  transition: width 1s ease;
}

.efficiency-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #22c55e;
}

.cta-area {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease;
}

.cta-area.visible {
  opacity: 1;
  transform: translateY(0);
}

.cta-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
}

.highlight {
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cta-subtitle {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 1.5rem;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  color: white;
  font-weight: 600;
  border-radius: 100px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.cta-button:hover {
  transform: scale(1.05);
  box-shadow: 0 20px 40px rgba(34, 197, 94, 0.3);
}

.cta-button .arrow {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.cta-button:hover .arrow {
  transform: translateX(4px);
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
  .macro-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .cta-title {
    font-size: 1.5rem;
  }
}
</style>
