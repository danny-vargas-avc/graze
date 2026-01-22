<script setup>
/**
 * CSS-only mobile fallback for landing page
 * No Three.js, relies on CSS animations for performance
 */
import { ref, computed } from 'vue'

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

// Sample meals for mobile display
const meals = [
  { id: 1, name: 'Grilled Chicken Bowl', restaurant: 'Chipotle', protein: 52, calories: 510 },
  { id: 2, name: 'Salmon Teriyaki', restaurant: 'Sweetgreen', protein: 46, calories: 580 },
  { id: 3, name: 'Turkey Club Wrap', restaurant: 'Panera', protein: 41, calories: 490 },
]

// Background gradient shifts with scroll
const gradientPosition = computed(() => {
  return `${props.scrollProgress * 100}%`
})
</script>

<template>
  <div class="mobile-scene">
    <!-- Animated gradient background -->
    <div
      class="gradient-bg"
      :style="{ '--gradient-pos': gradientPosition }"
    ></div>

    <!-- Floating particles (CSS only) -->
    <div class="particles">
      <div
        v-for="i in 12"
        :key="i"
        class="particle"
        :style="{
          '--delay': `${i * 0.3}s`,
          '--x': `${(i * 23) % 100}%`,
          '--y': `${(i * 17) % 100}%`,
          '--size': `${4 + (i % 4) * 2}px`,
        }"
      ></div>
    </div>

    <!-- Hero content (mobile optimized) -->
    <div v-if="activeSection === 0" class="mobile-hero">
      <h1 class="hero-title">
        Find Your
        <span class="gradient-text">Perfect Meal</span>
      </h1>
      <p class="hero-subtitle">
        Filter by protein. Filter by calories.
      </p>
    </div>

    <!-- Simplified meal cards for mobile -->
    <div v-if="activeSection >= 1 && activeSection <= 2" class="mobile-cards">
      <div
        v-for="meal in meals"
        :key="meal.id"
        class="mobile-card"
        :style="{ '--delay': `${meal.id * 0.1}s` }"
      >
        <div class="card-restaurant">{{ meal.restaurant }}</div>
        <div class="card-name">{{ meal.name }}</div>
        <div class="card-macros">
          <span class="protein">{{ meal.protein }}g</span>
          <span class="calories">{{ meal.calories }} cal</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mobile-scene {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  z-index: 0;
}

.gradient-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at 50% var(--gradient-pos, 50%),
    rgba(34, 197, 94, 0.1) 0%,
    rgba(10, 10, 10, 1) 50%
  );
  transition: background 0.5s ease;
}

.particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  left: var(--x);
  top: var(--y);
  width: var(--size);
  height: var(--size);
  background: rgba(34, 197, 94, 0.3);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-20px) scale(1.1);
    opacity: 0.6;
  }
}

.mobile-hero {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  padding: 2rem;
  width: 100%;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  margin-bottom: 1rem;
}

.gradient-text {
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.mobile-cards {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  width: 100%;
  max-width: 400px;
}

.mobile-card {
  background: rgba(20, 20, 20, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  animation: slideIn 0.5s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
  transform: translateY(20px);
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-restaurant {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.25rem;
}

.card-name {
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.card-macros {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
}

.protein {
  color: #22c55e;
  font-weight: 600;
}

.calories {
  color: rgba(255, 255, 255, 0.5);
}
</style>
