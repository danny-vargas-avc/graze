<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  title: {
    type: String,
    required: true,
  },
  icon: {
    type: String,
    default: null,
  },
  seeAllTo: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <section class="carousel-section">
    <div class="section-header">
      <div class="title-row">
        <!-- Section icon -->
        <svg v-if="icon === 'protein'" class="section-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v2.5h-2.5a.75.75 0 000 1.5h2.5v2.5a.75.75 0 001.5 0v-2.5h2.5a.75.75 0 000-1.5h-2.5v-2.5z" clip-rule="evenodd" />
        </svg>
        <svg v-else-if="icon === 'calories'" class="section-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M12.963 2.286a.75.75 0 00-1.071-.136 9.742 9.742 0 00-3.539 6.177A7.547 7.547 0 016.648 6.61a.75.75 0 00-1.152-.082A9 9 0 1015.68 4.534a7.46 7.46 0 01-2.717-2.248zM15.75 14.25a3.75 3.75 0 11-7.313-1.172c.628.465 1.35.81 2.133 1a5.99 5.99 0 011.925-3.545 3.75 3.75 0 013.255 3.717z" />
        </svg>
        <svg v-else-if="icon === 'ratio'" class="section-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M15.98 1.804a1 1 0 00-1.96 0l-.24 1.192a1 1 0 01-.784.785l-1.192.238a1 1 0 000 1.962l1.192.238a1 1 0 01.785.785l.238 1.192a1 1 0 001.962 0l.238-1.192a1 1 0 01.785-.785l1.192-.238a1 1 0 000-1.962l-1.192-.238a1 1 0 01-.785-.785l-.238-1.192zM6.949 5.684a1 1 0 00-1.898 0l-.683 2.051a1 1 0 01-.633.633l-2.052.683a1 1 0 000 1.898l2.052.684a1 1 0 01.633.632l.683 2.052a1 1 0 001.898 0l.683-2.052a1 1 0 01.633-.632l2.052-.684a1 1 0 000-1.898l-2.052-.683a1 1 0 01-.633-.633L6.95 5.684zM13.949 13.684a1 1 0 00-1.898 0l-.184.551a1 1 0 01-.632.633l-.551.183a1 1 0 000 1.898l.551.184a1 1 0 01.633.632l.183.551a1 1 0 001.898 0l.184-.551a1 1 0 01.632-.632l.551-.184a1 1 0 000-1.898l-.551-.183a1 1 0 01-.633-.633l-.183-.551z" />
        </svg>
        <!-- Bowl icon -->
        <svg v-else-if="icon === 'bowl'" class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M3 12h18" />
          <path stroke-linecap="round" d="M5 12c0 3.866 3.134 7 7 7s7-3.134 7-7" />
          <path stroke-linecap="round" d="M8 8c0-1 .5-2 2-2M14 6c0-1.5-1-2-1-3" />
        </svg>
        <!-- Salad/leaf icon -->
        <svg v-else-if="icon === 'salad'" class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 21c-4.97 0-9-2.686-9-6h18c0 3.314-4.03 6-9 6z" />
          <path stroke-linecap="round" d="M7 10c-1-3 1-6 5-7 4 1 6 4 5 7" />
          <path stroke-linecap="round" d="M12 3v7" />
        </svg>
        <!-- Burger icon -->
        <svg v-else-if="icon === 'burger'" class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M4 15h16" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 15c0 2 1.5 3 3 3h10c1.5 0 3-1 3-3" />
          <path stroke-linecap="round" d="M3 12h18" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 12c0-4 3.5-7 9-7s9 3 9 7" />
        </svg>
        <h2 class="title">{{ title }}</h2>
      </div>
      <RouterLink v-if="seeAllTo" :to="seeAllTo" class="see-all">
        See all
        <svg class="chevron" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
        </svg>
      </RouterLink>
    </div>
    <slot />
  </section>
</template>

<style scoped>
.carousel-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: var(--color-primary);
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.see-all {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-primary);
  text-decoration: none;
  white-space: nowrap;
}

.see-all:hover {
  color: var(--color-primary-hover);
}

.chevron {
  width: 16px;
  height: 16px;
}
</style>
