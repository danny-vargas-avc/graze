<script setup>
/**
 * Landing Page with "Chaos to Order" narrative
 * 7 sections: Hero → Transformation → MacroSpace → Speed → Trust → Zillow → CTA
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLandingScroll } from '../composables/useLandingScroll'
import { useDeviceCapability } from '../composables/useDeviceCapability'
import { useTransformation } from '../composables/useTransformation'
import LandingScene from '../components/landing/LandingScene.vue'
import MobileScene from '../components/landing/MobileScene.vue'
import TypewriterFilter from '../components/landing/TypewriterFilter.vue'
import SpeedComparison from '../components/landing/SpeedComparison.vue'
import TrustLogos from '../components/landing/TrustLogos.vue'
import ZillowFilter from '../components/landing/ZillowFilter.vue'
import FinalCTA from '../components/landing/FinalCTA.vue'

// Scroll state machine
const {
  scrollProgress,
  activeSection,
  heroProgress,
  transformationProgress,
  macroSpaceProgress,
  speedProgress,
  trustProgress,
  zillowProgress,
  ctaProgress,
} = useLandingScroll()

// Device detection
const { shouldUseFallback, isMobile } = useDeviceCapability()

// Transformation state
const { typewriterText, updateTransformation, FULL_FILTER_TEXT } = useTransformation()

// Update transformation text based on progress
const showTypewriter = computed(() => {
  return activeSection.value === 1 && transformationProgress.value > 0 && transformationProgress.value < 0.6
})

const currentTypewriterText = computed(() => {
  if (!showTypewriter.value) return ''
  const charCount = Math.floor(transformationProgress.value * 5 * FULL_FILTER_TEXT.length)
  return FULL_FILTER_TEXT.substring(0, Math.min(charCount, FULL_FILTER_TEXT.length))
})

// Section visibility
const showMacroSpace = computed(() => activeSection.value === 2)
const showSpeed = computed(() => activeSection.value === 3)
const showTrust = computed(() => activeSection.value === 4)
const showZillow = computed(() => activeSection.value === 5)
const showCTA = computed(() => activeSection.value === 6)

// Hero text animation state
const heroVisible = computed(() => activeSection.value === 0)
</script>

<template>
  <div class="landing-page">
    <!-- 3D Canvas (Desktop) -->
    <div v-if="!shouldUseFallback" class="canvas-container">
      <LandingScene
        :scroll-progress="scrollProgress"
        :active-section="activeSection"
        :transformation-progress="transformationProgress"
      />
    </div>

    <!-- Mobile Fallback -->
    <MobileScene
      v-else
      :scroll-progress="scrollProgress"
      :active-section="activeSection"
    />

    <!-- 2D Overlay Elements -->
    <div class="overlay-container">
      <!-- Typewriter Filter (Transformation Section) -->
      <TypewriterFilter
        :text="currentTypewriterText"
        :visible="showTypewriter"
        :progress="transformationProgress"
      />

      <!-- Speed Comparison (Section 3) -->
      <SpeedComparison
        :progress="speedProgress"
        :visible="showSpeed"
      />

      <!-- Trust Logos (Section 4) -->
      <TrustLogos
        :progress="trustProgress"
        :visible="showTrust"
      />

      <!-- Zillow Filter (Section 5) -->
      <ZillowFilter
        :progress="zillowProgress"
        :visible="showZillow"
      />

      <!-- Final CTA (Section 6) -->
      <FinalCTA
        :progress="ctaProgress"
        :visible="showCTA"
      />
    </div>

    <!-- Scrollable Content Sections -->
    <div class="content-wrapper">
      <!-- Section 0: Hero -->
      <section class="section hero-section">
        <div class="hero-content" :class="{ 'visible': heroVisible }">
          <h1 class="hero-title">
            Find Your
            <span class="gradient-text">Perfect Meal</span>
          </h1>
          <p class="hero-subtitle">
            Filter by protein. Filter by calories. Eat smarter.
          </p>
          <div class="scroll-hint">
            <span>Scroll to explore</span>
            <div class="scroll-arrow"></div>
          </div>
        </div>
      </section>

      <!-- Section 1: Transformation -->
      <section class="section transformation-section">
        <div class="section-label" v-show="activeSection === 1">
          <span class="label-badge">THE FILTER</span>
        </div>
      </section>

      <!-- Section 2: Macro Space -->
      <section class="section macro-section">
        <div class="section-label" v-show="activeSection === 2">
          <span class="label-badge">3D NUTRITION</span>
          <h2 class="section-title">
            Every macro,
            <span class="gradient-text">visualized</span>
          </h2>
        </div>
      </section>

      <!-- Section 3: Speed Comparison -->
      <section class="section speed-section">
        <!-- Content handled by SpeedComparison overlay -->
      </section>

      <!-- Section 4: Trust -->
      <section class="section trust-section">
        <!-- Content handled by TrustLogos overlay -->
      </section>

      <!-- Section 5: Zillow Filter -->
      <section class="section zillow-section">
        <!-- Content handled by ZillowFilter overlay -->
      </section>

      <!-- Section 6: CTA -->
      <section class="section cta-section">
        <!-- Content handled by FinalCTA overlay -->
      </section>
    </div>

    <!-- Progress Indicator -->
    <div class="progress-indicator">
      <div
        class="progress-bar"
        :style="{ height: `${scrollProgress * 100}%` }"
      ></div>
      <div class="section-dots">
        <div
          v-for="i in 7"
          :key="i"
          class="dot"
          :class="{ 'active': activeSection >= i - 1 }"
        ></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.landing-page {
  background: #0a0a0a;
  color: white;
  overflow-x: hidden;
}

/* Canvas container */
.canvas-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 1;
}

/* Overlay for 2D elements */
.overlay-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 5;
  pointer-events: none;
}

.overlay-container > * {
  pointer-events: auto;
}

/* Scrollable content */
.content-wrapper {
  position: relative;
  z-index: 2;
  pointer-events: none;
}

.content-wrapper > * {
  pointer-events: auto;
}

.section {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

/* 700vh total for 7 sections */
.content-wrapper {
  min-height: 700vh;
}

/* Hero Section */
.hero-section {
  position: relative;
}

.hero-content {
  text-align: center;
  max-width: 900px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.hero-content.visible {
  opacity: 1;
  transform: translateY(0);
}

.hero-title {
  font-size: clamp(2.5rem, 8vw, 6rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(135deg, #22c55e 0%, #14b8a6 50%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: clamp(1rem, 2.5vw, 1.5rem);
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 3rem;
}

.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.875rem;
  animation: pulse 2s ease-in-out infinite;
}

.scroll-arrow {
  width: 20px;
  height: 20px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: rotate(45deg) translateY(0); }
  50% { transform: rotate(45deg) translateY(6px); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* Section Labels */
.section-label {
  text-align: center;
}

.label-badge {
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

.section-title {
  font-size: clamp(1.75rem, 5vw, 3rem);
  font-weight: 700;
  line-height: 1.2;
}

/* Progress Indicator */
.progress-indicator {
  position: fixed;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  width: 2px;
  background: linear-gradient(to bottom, #22c55e, #14b8a6);
  border-radius: 1px;
  transition: height 0.1s ease;
  position: absolute;
  top: 0;
}

.section-dots {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.dot.active {
  background: #22c55e;
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}

/* Hide progress on mobile */
@media (max-width: 768px) {
  .progress-indicator {
    display: none;
  }

  .section {
    padding: 1rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }
}
</style>
