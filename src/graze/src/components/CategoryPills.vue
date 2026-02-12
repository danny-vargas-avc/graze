<script setup>
import { ref } from 'vue'

const props = defineProps({
  active: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['change'])

const categories = [
  { id: 'bowl', label: 'Bowls', icon: 'bowl' },
  { id: 'salad', label: 'Salads', icon: 'salad' },
  { id: 'sandwich', label: 'Sandwiches', icon: 'sandwich' },
  { id: 'breakfast', label: 'Breakfast', icon: 'breakfast' },
  { id: 'soup', label: 'Soups', icon: 'soup' },
  { id: 'plate', label: 'Plates', icon: 'plate' },
  { id: 'flatbread', label: 'Flatbread', icon: 'flatbread' },
  { id: 'side', label: 'Sides', icon: 'side' },
]

function handleClick(id) {
  emit('change', props.active === id ? null : id)
}
</script>

<template>
  <div class="category-pills hide-scrollbar">
    <button
      v-for="cat in categories"
      :key="cat.id"
      class="pill"
      :class="{ active: active === cat.id }"
      @click="handleClick(cat.id)"
    >
      <div class="pill-icon">
        <!-- Bowl -->
        <svg v-if="cat.icon === 'bowl'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M3 12h18" />
          <path stroke-linecap="round" d="M5 12c0 3.866 3.134 7 7 7s7-3.134 7-7" />
          <path stroke-linecap="round" d="M9 12V8" />
          <path stroke-linecap="round" d="M12 12V6" />
          <path stroke-linecap="round" d="M15 12V8" />
        </svg>
        <!-- Salad -->
        <svg v-else-if="cat.icon === 'salad'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c-1.5 0-3 .5-4 2-1 1.5-.5 3 0 4H4c0 4.418 3.582 8 8 8s8-3.582 8-8h-4c.5-1 1-2.5 0-4-1-1.5-2.5-2-4-2z" />
          <path stroke-linecap="round" d="M8 17l-1 4M16 17l1 4" />
        </svg>
        <!-- Sandwich -->
        <svg v-else-if="cat.icon === 'sandwich'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 17h16l-1-3H5l-1 3z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 14l1-4h12l1 4" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 10c0-3 2.686-5 6-5s6 2 6 5" />
        </svg>
        <!-- Breakfast -->
        <svg v-else-if="cat.icon === 'breakfast'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="9" cy="12" r="5" />
          <circle cx="9" cy="12" r="2" />
          <path stroke-linecap="round" d="M17 9c1.5 0 3 1 3 3s-1.5 3-3 3" />
          <path stroke-linecap="round" d="M14 12h3" />
        </svg>
        <!-- Soup -->
        <svg v-else-if="cat.icon === 'soup'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M3 13h18" />
          <path stroke-linecap="round" d="M5 13c0 3.866 3.134 7 7 7s7-3.134 7-7" />
          <path stroke-linecap="round" d="M8 9c0-1 .5-2 1-2s1 1 1 2" />
          <path stroke-linecap="round" d="M13 8c0-1 .5-2 1-2s1 1 1 2" />
        </svg>
        <!-- Default plate/other -->
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="8" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </div>
      <span class="pill-label">{{ cat.label }}</span>
    </button>
  </div>
</template>

<style scoped>
.category-pills {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  overflow-x: auto;
  flex-shrink: 0;
}

.pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  min-width: 64px;
  flex-shrink: 0;
}

.pill-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface);
  border: 1.5px solid var(--color-border);
  transition: all 150ms ease;
}

.pill-icon svg {
  width: 24px;
  height: 24px;
  color: var(--color-text-secondary);
  transition: color 150ms ease;
}

.pill:hover .pill-icon {
  border-color: var(--color-primary);
}

.pill:hover .pill-icon svg {
  color: var(--color-primary);
}

.pill.active .pill-icon {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.pill.active .pill-icon svg {
  color: white;
}

.pill-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-secondary);
  white-space: nowrap;
  transition: color 150ms ease;
}

.pill.active .pill-label {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
