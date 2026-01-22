<script setup>
/**
 * Section 5: Zillow-like filter simulation
 * Shows how bad matches fade away as filters are applied
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

// Filter state
const filters = ref({
  minProtein: 0,
  maxCalories: 1000,
})

// Sample meals with varying match quality
const meals = ref([
  { id: 1, name: 'Grilled Chicken Bowl', protein: 52, calories: 510, restaurant: 'Chipotle' },
  { id: 2, name: 'Caesar Salad', protein: 18, calories: 450, restaurant: 'Panera' },
  { id: 3, name: 'Double Bacon Burger', protein: 35, calories: 890, restaurant: "Five Guys" },
  { id: 4, name: 'Salmon Teriyaki', protein: 46, calories: 580, restaurant: 'Sweetgreen' },
  { id: 5, name: 'Veggie Wrap', protein: 12, calories: 380, restaurant: 'Subway' },
  { id: 6, name: 'Steak Power Bowl', protein: 48, calories: 520, restaurant: 'Chipotle' },
  { id: 7, name: 'Cheese Pizza', protein: 14, calories: 720, restaurant: 'Dominos' },
  { id: 8, name: 'BBQ Chicken Salad', protein: 43, calories: 490, restaurant: "Chick-fil-A" },
])

// Animate filters based on progress
watch(() => props.progress, (progress) => {
  if (props.visible) {
    // Gradually increase min protein filter
    filters.value.minProtein = Math.floor(progress * 45) // Up to 45g
    // Gradually decrease max calories filter
    filters.value.maxCalories = Math.floor(1000 - progress * 400) // Down to 600
  }
})

// Determine if meal matches current filters
const mealStates = computed(() => {
  return meals.value.map(meal => {
    const matchesProtein = meal.protein >= filters.value.minProtein
    const matchesCalories = meal.calories <= filters.value.maxCalories
    const matches = matchesProtein && matchesCalories

    // Calculate "match score" for visual feedback
    const proteinScore = meal.protein / 50
    const calorieScore = 1 - (meal.calories - 400) / 600

    return {
      ...meal,
      matches,
      matchScore: (proteinScore + calorieScore) / 2,
      opacity: matches ? 1 : 0.2,
      scale: matches ? 1 : 0.95,
    }
  })
})

// Count matching meals
const matchCount = computed(() => mealStates.value.filter(m => m.matches).length)
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="zillow-section">
      <!-- Filter controls -->
      <div class="filter-panel">
        <div class="filter-header">
          <span class="filter-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z" />
            </svg>
          </span>
          <span class="filter-title">Active Filters</span>
        </div>

        <div class="filter-tags">
          <span class="filter-tag protein">
            <span class="tag-label">Protein</span>
            <span class="tag-value">>= {{ filters.minProtein }}g</span>
          </span>
          <span class="filter-tag calories">
            <span class="tag-label">Calories</span>
            <span class="tag-value"><= {{ filters.maxCalories }}</span>
          </span>
        </div>

        <div class="match-count">
          <span class="count-value">{{ matchCount }}</span>
          <span class="count-label">matches found</span>
        </div>
      </div>

      <!-- Meal results grid -->
      <div class="results-grid">
        <div
          v-for="meal in mealStates"
          :key="meal.id"
          class="result-card"
          :class="{ 'faded': !meal.matches }"
          :style="{
            opacity: meal.opacity,
            transform: `scale(${meal.scale})`,
          }"
        >
          <div class="card-header">
            <span class="restaurant">{{ meal.restaurant }}</span>
            <span v-if="meal.matches" class="match-badge">Match</span>
          </div>
          <div class="dish-name">{{ meal.name }}</div>
          <div class="macros">
            <span class="macro protein" :class="{ 'highlight': meal.protein >= filters.minProtein }">
              {{ meal.protein }}g protein
            </span>
            <span class="macro calories" :class="{ 'highlight': meal.calories <= filters.maxCalories }">
              {{ meal.calories }} cal
            </span>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.zillow-section {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 1000px;
  z-index: 10;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

.filter-panel {
  background: rgba(15, 15, 15, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  height: fit-content;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.filter-icon {
  color: #22c55e;
}

.filter-title {
  font-weight: 600;
  color: white;
}

.filter-tags {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.filter-tag {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
}

.filter-tag.protein {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.filter-tag.calories {
  background: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.3);
}

.tag-label {
  color: rgba(255, 255, 255, 0.5);
}

.tag-value {
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
}

.filter-tag.protein .tag-value {
  color: #22c55e;
}

.filter-tag.calories .tag-value {
  color: #eab308;
}

.match-count {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.count-value {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: #22c55e;
}

.count-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.result-card {
  background: rgba(20, 20, 20, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s ease;
}

.result-card.faded {
  border-color: rgba(255, 255, 255, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.restaurant {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.match-badge {
  font-size: 0.625rem;
  padding: 0.25rem 0.5rem;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.dish-name {
  font-weight: 600;
  color: white;
  margin-bottom: 0.75rem;
}

.macros {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
}

.macro {
  color: rgba(255, 255, 255, 0.4);
  transition: color 0.3s ease;
}

.macro.highlight {
  color: rgba(255, 255, 255, 0.8);
}

.macro.protein.highlight {
  color: #22c55e;
}

.macro.calories.highlight {
  color: #eab308;
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
  .zillow-section {
    grid-template-columns: 1fr;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
