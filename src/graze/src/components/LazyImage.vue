<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: null
  },
  fallback: {
    type: String,
    default: null
  }
})

const loaded = ref(false)
const error = ref(false)
const imageRef = ref(null)

const handleLoad = () => {
  loaded.value = true
}

const handleError = () => {
  error.value = true
  loaded.value = true
}

onMounted(() => {
  if (!imageRef.value) return

  // Use Intersection Observer for lazy loading
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target
        if (img.dataset.src) {
          img.src = img.dataset.src
          img.removeAttribute('data-src')
        }
        observer.unobserve(img)
      }
    })
  }, {
    rootMargin: '50px' // Start loading 50px before entering viewport
  })

  observer.observe(imageRef.value)
})
</script>

<template>
  <div class="lazy-image">
    <img
      ref="imageRef"
      :data-src="src"
      :alt="alt"
      :class="{ 'loaded': loaded, 'error': error }"
      @load="handleLoad"
      @error="handleError"
    />
    <div v-if="!loaded && !error" class="loading-placeholder">
      <div class="skeleton"></div>
    </div>
    <div v-if="error && fallback" class="fallback">
      <img :src="fallback" :alt="alt" />
    </div>
  </div>
</template>

<style scoped>
.lazy-image {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.lazy-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 300ms ease;
}

.lazy-image img.loaded {
  opacity: 1;
}

.lazy-image img.error {
  opacity: 0;
}

.loading-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-surface);
}

.skeleton {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--color-surface) 25%,
    var(--color-surface-elevated) 50%,
    var(--color-surface) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.fallback {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface);
}

.fallback img {
  opacity: 1;
}
</style>
