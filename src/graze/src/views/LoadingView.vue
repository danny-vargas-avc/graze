<script setup>
/**
 * Loading Page - "Chemical Breakdown" Transition
 * Bridges landing (organic art) to search (functional app)
 */
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { useTransitionStore } from '../stores/transition'
import { useDishesStore } from '../stores/dishes'

const router = useRouter()
const transitionStore = useTransitionStore()
const dishesStore = useDishesStore()

const canvasRef = ref(null)
const termRefs = ref([])
let gl = null
let animationFrame = null
let masterTimeline = null

// Completion gates
const animationComplete = ref(false)
const dataReady = ref(false)

// Presets/palettes (same as landing, used as fallback)
const PRESETS = [
  { name: 'coral', f: 0.0545, k: 0.062, seeds: 20 },
  { name: 'maze', f: 0.029, k: 0.057, seeds: 20 },
  { name: 'bubbles', f: 0.012, k: 0.050, seeds: 25 },
  { name: 'waves', f: 0.014, k: 0.045, seeds: 20 },
  { name: 'worms', f: 0.040, k: 0.060, seeds: 20 },
]

const PALETTES = [
  { bg: [0.12, 0.12, 0.12], fg: [0.90, 0.70, 0.55] },
  { bg: [0.12, 0.12, 0.12], fg: [0.70, 0.80, 0.60] },
  { bg: [0.12, 0.12, 0.12], fg: [0.95, 0.85, 0.65] },
  { bg: [0.12, 0.12, 0.12], fg: [0.60, 0.70, 0.65] },
]

const nutritionTerms = [
  'PROTEIN', 'CARBOHYDRATE', 'LIPID', 'AMINO ACID',
  'GLUCOSE', 'ENZYME', 'PEPTIDE', 'CALORIE',
  'FIBER', 'MINERAL', 'VITAMIN', 'METABOLISM',
  'OXIDATION', 'SYNTHESIS', 'CATALYSIS', 'ATP',
]

// Simulation state
let currentPreset = null
let currentPalette = null
let simWidth = 0
let simHeight = 0

// WebGL resources
let simulationProgram = null
let breakdownProgram = null
let textures = []
let framebuffers = []
let currentTexture = 0
let quadBuffer = null

// Voronoi seeds for fracture effect
const voronoiSeeds = new Float32Array(32)
const voronoiSeedsAnimated = new Float32Array(32)

// Phase uniforms driven by GSAP
const phase = reactive({
  dtMultiplier: 1.0,
  stepsPerFrame: 8,
  patternStrength: 1.0,
  breakdownProgress: 0.0,
  convergeProgress: 0.0,
  fadeOut: 0.0,
})

// Foreground color for text styling
const fgColorCSS = ref('rgba(255,255,255,0.6)')

// --- Shaders ---

const vertexShaderSource = `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`

const simulationShaderSource = `
  precision highp float;

  uniform sampler2D u_texture;
  uniform vec2 u_resolution;
  uniform float u_feed;
  uniform float u_kill;
  uniform float u_dt;

  varying vec2 v_uv;

  void main() {
    vec2 texel = 1.0 / u_resolution;

    vec4 state = texture2D(u_texture, v_uv);
    float a = state.r;
    float b = state.g;

    float la = -a;
    float lb = -b;

    la += texture2D(u_texture, v_uv + vec2(-texel.x, 0.0)).r * 0.2;
    la += texture2D(u_texture, v_uv + vec2(texel.x, 0.0)).r * 0.2;
    la += texture2D(u_texture, v_uv + vec2(0.0, -texel.y)).r * 0.2;
    la += texture2D(u_texture, v_uv + vec2(0.0, texel.y)).r * 0.2;

    lb += texture2D(u_texture, v_uv + vec2(-texel.x, 0.0)).g * 0.2;
    lb += texture2D(u_texture, v_uv + vec2(texel.x, 0.0)).g * 0.2;
    lb += texture2D(u_texture, v_uv + vec2(0.0, -texel.y)).g * 0.2;
    lb += texture2D(u_texture, v_uv + vec2(0.0, texel.y)).g * 0.2;

    la += texture2D(u_texture, v_uv + vec2(-texel.x, -texel.y)).r * 0.05;
    la += texture2D(u_texture, v_uv + vec2(texel.x, -texel.y)).r * 0.05;
    la += texture2D(u_texture, v_uv + vec2(-texel.x, texel.y)).r * 0.05;
    la += texture2D(u_texture, v_uv + vec2(texel.x, texel.y)).r * 0.05;

    lb += texture2D(u_texture, v_uv + vec2(-texel.x, -texel.y)).g * 0.05;
    lb += texture2D(u_texture, v_uv + vec2(texel.x, -texel.y)).g * 0.05;
    lb += texture2D(u_texture, v_uv + vec2(-texel.x, texel.y)).g * 0.05;
    lb += texture2D(u_texture, v_uv + vec2(texel.x, texel.y)).g * 0.05;

    float Da = 1.0;
    float Db = 0.5;
    float f = u_feed;
    float k = u_kill;

    float abb = a * b * b;
    float da = Da * la - abb + f * (1.0 - a);
    float db = Db * lb + abb - (k + f) * b;

    a = clamp(a + da * u_dt, 0.0, 1.0);
    b = clamp(b + db * u_dt, 0.0, 1.0);

    gl_FragColor = vec4(a, b, 0.0, 1.0);
  }
`

const breakdownShaderSource = `
  precision highp float;

  uniform sampler2D u_texture;
  uniform vec2 u_resolution;
  uniform vec3 u_bgColor;
  uniform vec3 u_fgColor;

  // Phase uniforms
  uniform float u_patternStrength;
  uniform float u_breakdownProgress;
  uniform float u_convergeProgress;
  uniform float u_fadeOut;

  // Voronoi seeds
  uniform vec2 u_seeds[16];

  varying vec2 v_uv;

  void main() {
    vec2 texel = 1.0 / u_resolution;

    // --- Voronoi cell calculation ---
    float minDist = 999.0;
    float secondMinDist = 999.0;
    vec2 nearestSeed = vec2(0.5);
    int cellIdx = 0;

    for (int i = 0; i < 16; i++) {
      float d = distance(v_uv, u_seeds[i]);
      if (d < minDist) {
        secondMinDist = minDist;
        minDist = d;
        cellIdx = i;
        nearestSeed = u_seeds[i];
      } else if (d < secondMinDist) {
        secondMinDist = d;
      }
    }

    // Edge factor: 0 at cell edge, ~1 deep inside cell
    float edgeFactor = (secondMinDist - minDist) / (secondMinDist + minDist + 0.001);

    // --- Fragment displacement ---
    vec2 displaceDir = normalize(v_uv - nearestSeed + 0.001);
    float displaceAmount = u_breakdownProgress * 0.1 * (1.0 - edgeFactor);

    // Per-cell rotation
    float cellAngle = float(cellIdx) * 2.399 + 0.5;
    float rotAngle = u_breakdownProgress * cellAngle * 0.3;
    vec2 localUV = v_uv - nearestSeed;
    mat2 rot = mat2(cos(rotAngle), -sin(rotAngle), sin(rotAngle), cos(rotAngle));
    vec2 rotatedLocal = rot * localUV;

    // Displaced UV for sampling
    vec2 sampleUV = nearestSeed + rotatedLocal + displaceDir * displaceAmount;
    sampleUV = clamp(sampleUV, vec2(0.0), vec2(1.0));

    // --- Sample simulation with gradient/emboss ---
    float b = texture2D(u_texture, sampleUV).g;
    float bL = texture2D(u_texture, sampleUV + vec2(-texel.x, 0.0)).g;
    float bR = texture2D(u_texture, sampleUV + vec2(texel.x, 0.0)).g;
    float bD = texture2D(u_texture, sampleUV + vec2(0.0, -texel.y)).g;
    float bU = texture2D(u_texture, sampleUV + vec2(0.0, texel.y)).g;

    float gx = bR - bL;
    float gy = bU - bD;
    float edge = sqrt(gx * gx + gy * gy);
    float light = (gx + gy) * 2.0;

    // Fade pattern by reducing B chemical influence
    float bFaded = b * u_patternStrength;
    float gxFaded = gx * u_patternStrength;
    float gyFaded = gy * u_patternStrength;
    float edgeFaded = edge * u_patternStrength;
    float lightFaded = (gxFaded + gyFaded) * 2.0;

    vec3 base = mix(u_bgColor, u_fgColor, bFaded);
    vec3 highlight = base + vec3(0.20) * lightFaded;
    vec3 color = highlight + edgeFaded * vec3(0.15);

    // --- Crack mask ---
    float crackWidth = u_breakdownProgress * 0.15;
    float crack = smoothstep(crackWidth, crackWidth + 0.02, edgeFactor);

    // Gap color (slightly lighter bg for depth)
    vec3 gapColor = u_bgColor * 0.4;
    vec3 fragColor = mix(gapColor, color, crack);

    // Fade toward search page bg (#f9fafb)
    vec3 searchBg = vec3(0.976, 0.98, 0.984);
    fragColor = mix(fragColor, searchBg, u_fadeOut);

    gl_FragColor = vec4(clamp(fragColor, 0.0, 1.0), 1.0);
  }
`

// --- WebGL helpers ---

function createShader(type, source) {
  const shader = gl.createShader(type)
  gl.shaderSource(shader, source)
  gl.compileShader(shader)
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error('Shader compile error:', gl.getShaderInfoLog(shader))
    gl.deleteShader(shader)
    return null
  }
  return shader
}

function createProgram(vertexSource, fragmentSource) {
  const vertexShader = createShader(gl.VERTEX_SHADER, vertexSource)
  const fragmentShader = createShader(gl.FRAGMENT_SHADER, fragmentSource)
  if (!vertexShader || !fragmentShader) return null

  const program = gl.createProgram()
  gl.attachShader(program, vertexShader)
  gl.attachShader(program, fragmentShader)
  gl.linkProgram(program)

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error('Program link error:', gl.getProgramInfoLog(program))
    return null
  }
  return program
}

function initWebGL() {
  const canvas = canvasRef.value
  gl = canvas.getContext('webgl', {
    alpha: false,
    antialias: false,
    preserveDrawingBuffer: false,
  })

  if (!gl) {
    console.error('WebGL not supported')
    return false
  }

  const floatExt = gl.getExtension('OES_texture_float')
  if (!floatExt) {
    console.error('OES_texture_float not supported')
    return false
  }
  gl.getExtension('OES_texture_float_linear')

  simulationProgram = createProgram(vertexShaderSource, simulationShaderSource)
  breakdownProgram = createProgram(vertexShaderSource, breakdownShaderSource)

  if (!simulationProgram || !breakdownProgram) {
    console.error('Failed to create shader programs')
    return false
  }

  quadBuffer = gl.createBuffer()
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer)
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    -1, -1, 1, -1, -1, 1,
    -1, 1, 1, -1, 1, 1
  ]), gl.STATIC_DRAW)

  resizeCanvas()
  return true
}

function resizeCanvas() {
  const canvas = canvasRef.value
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const width = Math.floor(window.innerWidth * dpr)
  const height = Math.floor(window.innerHeight * dpr)

  canvas.width = width
  canvas.height = height
  canvas.style.width = window.innerWidth + 'px'
  canvas.style.height = window.innerHeight + 'px'

  simWidth = Math.floor(width * 0.5)
  simHeight = Math.floor(height * 0.5)

  createTextures()
}

function createTextures() {
  textures.forEach(t => gl.deleteTexture(t))
  framebuffers.forEach(fb => gl.deleteFramebuffer(fb))
  textures = []
  framebuffers = []

  for (let i = 0; i < 2; i++) {
    const texture = gl.createTexture()
    gl.bindTexture(gl.TEXTURE_2D, texture)
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, simWidth, simHeight, 0, gl.RGBA, gl.FLOAT, null)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    textures.push(texture)

    const framebuffer = gl.createFramebuffer()
    gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer)
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0)
    framebuffers.push(framebuffer)
  }

  gl.bindFramebuffer(gl.FRAMEBUFFER, null)
  initializeState()
}

function initializeState() {
  const data = new Float32Array(simWidth * simHeight * 4)

  for (let i = 0; i < simWidth * simHeight; i++) {
    data[i * 4 + 0] = 1.0
    data[i * 4 + 1] = 0.0
    data[i * 4 + 2] = 0.0
    data[i * 4 + 3] = 1.0
  }

  const baseSeeds = currentPreset ? currentPreset.seeds : 20
  const numSeeds = baseSeeds + Math.floor(Math.random() * Math.floor(baseSeeds * 0.5))
  for (let s = 0; s < numSeeds; s++) {
    const cx = Math.floor(Math.random() * simWidth)
    const cy = Math.floor(Math.random() * simHeight)
    const radius = 8 + Math.floor(Math.random() * 20)

    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < radius) {
          const x = (cx + dx + simWidth) % simWidth
          const y = (cy + dy + simHeight) % simHeight
          const idx = (y * simWidth + x) * 4
          const falloff = 1.0 - (dist / radius)
          data[idx + 0] = 0.5 + 0.25 * falloff
          data[idx + 1] = 0.25 + 0.75 * falloff
        }
      }
    }
  }

  for (let i = 0; i < 2; i++) {
    gl.bindTexture(gl.TEXTURE_2D, textures[i])
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, simWidth, simHeight, 0, gl.RGBA, gl.FLOAT, data)
  }
}

function warmUp(steps) {
  for (let i = 0; i < steps; i++) {
    simulate(1.0)
  }
}

function simulate(dt) {
  gl.useProgram(simulationProgram)

  gl.activeTexture(gl.TEXTURE0)
  gl.bindTexture(gl.TEXTURE_2D, textures[currentTexture])
  gl.uniform1i(gl.getUniformLocation(simulationProgram, 'u_texture'), 0)

  gl.uniform2f(gl.getUniformLocation(simulationProgram, 'u_resolution'), simWidth, simHeight)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_feed'), currentPreset.f)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_kill'), currentPreset.k)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_dt'), dt)

  const nextTexture = 1 - currentTexture
  gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffers[nextTexture])
  gl.viewport(0, 0, simWidth, simHeight)

  const posLoc = gl.getAttribLocation(simulationProgram, 'a_position')
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer)
  gl.enableVertexAttribArray(posLoc)
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)
  gl.drawArrays(gl.TRIANGLES, 0, 6)

  currentTexture = nextTexture
}

function displayBreakdown() {
  gl.useProgram(breakdownProgram)

  // Update animated voronoi seeds
  for (let i = 0; i < 32; i++) {
    voronoiSeedsAnimated[i] = voronoiSeeds[i] +
      (0.5 - voronoiSeeds[i]) * phase.convergeProgress
  }

  const texLoc = gl.getUniformLocation(breakdownProgram, 'u_texture')
  const posLoc = gl.getAttribLocation(breakdownProgram, 'a_position')

  gl.activeTexture(gl.TEXTURE0)
  gl.bindTexture(gl.TEXTURE_2D, textures[currentTexture])
  gl.uniform1i(texLoc, 0)

  gl.uniform2f(gl.getUniformLocation(breakdownProgram, 'u_resolution'), simWidth, simHeight)
  gl.uniform3f(gl.getUniformLocation(breakdownProgram, 'u_bgColor'),
    currentPalette.bg[0], currentPalette.bg[1], currentPalette.bg[2])
  gl.uniform3f(gl.getUniformLocation(breakdownProgram, 'u_fgColor'),
    currentPalette.fg[0], currentPalette.fg[1], currentPalette.fg[2])

  // Phase uniforms
  gl.uniform1f(gl.getUniformLocation(breakdownProgram, 'u_patternStrength'), phase.patternStrength)
  gl.uniform1f(gl.getUniformLocation(breakdownProgram, 'u_breakdownProgress'), phase.breakdownProgress)
  gl.uniform1f(gl.getUniformLocation(breakdownProgram, 'u_convergeProgress'), phase.convergeProgress)
  gl.uniform1f(gl.getUniformLocation(breakdownProgram, 'u_fadeOut'), phase.fadeOut)

  // Voronoi seeds
  gl.uniform2fv(gl.getUniformLocation(breakdownProgram, 'u_seeds[0]'), voronoiSeedsAnimated)

  gl.bindFramebuffer(gl.FRAMEBUFFER, null)
  gl.viewport(0, 0, canvasRef.value.width, canvasRef.value.height)

  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer)
  gl.enableVertexAttribArray(posLoc)
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)
  gl.drawArrays(gl.TRIANGLES, 0, 6)
}

let firstFrame = true

function render() {
  const steps = Math.round(phase.stepsPerFrame)
  for (let i = 0; i < steps; i++) {
    simulate(phase.dtMultiplier)
  }

  displayBreakdown()

  // Fade out screenshot after first frame
  if (firstFrame) {
    firstFrame = false
    requestAnimationFrame(() => {
      transitionStore.screenshotDataUrl = null
    })
  }

  animationFrame = requestAnimationFrame(render)
}

// --- GSAP Timeline ---

function buildTimeline() {
  masterTimeline = gsap.timeline({
    onComplete: () => {
      animationComplete.value = true
      checkReady()
    },
  })

  // Phase 1: Fade out pattern (0-1.5s)
  masterTimeline.to(phase, {
    patternStrength: 0.0,
    duration: 1.5,
    ease: 'power1.out',
  }, 0)

  // Phase 2: Fracture (1.5-3s)
  masterTimeline.to(phase, {
    breakdownProgress: 1.0,
    duration: 1.5,
    ease: 'power2.inOut',
  }, 1.5)

  // Phase 3: Convergence (3-4s)
  masterTimeline.to(phase, {
    convergeProgress: 1.0,
    duration: 1.0,
    ease: 'power3.in',
  }, 3.0)

  // Phase 4: Fade out (4-4.5s)
  masterTimeline.to(phase, {
    fadeOut: 1.0,
    duration: 1.2,
    ease: 'power1.in',
  }, 4.0)

  // Text animations: staggered entrance (1.5-3s, alongside fracture)
  termRefs.value.forEach((el, i) => {
    if (!el) return
    const startX = (Math.random() - 0.5) * 400
    const startY = (Math.random() - 0.5) * 400
    const targetOpacity = 0.8 + Math.random() * 0.2

    gsap.set(el, { opacity: 0, x: startX, y: startY, scale: 0.5 + Math.random() })

    masterTimeline.to(el, {
      opacity: targetOpacity,
      x: (Math.random() - 0.5) * 300,
      y: (Math.random() - 0.5) * 200,
      scale: 1,
      duration: 1,
      ease: 'power2.out',
    }, 1.5 + i * 0.06)
  })

  // Text animations: converge and fade (3-4s)
  masterTimeline.to('.nutrition-term', {
    x: 0,
    y: 0,
    opacity: 0,
    scale: 0.3,
    duration: 1.0,
    ease: 'power3.in',
    stagger: 0.02,
  }, 3.0)
}

// --- Data & Navigation ---

function checkReady() {
  if (animationComplete.value && dataReady.value) {
    transitionStore.clear()
    router.replace('/search')
  }
}

async function prefetchData() {
  try {
    await dishesStore.fetchDishes()
  } catch (e) {
    // SearchView handles errors
  }
  dataReady.value = true
  checkReady()
}

// --- Lifecycle ---

onMounted(() => {
  // Get preset/palette from transition store or use random
  if (transitionStore.preset) {
    currentPreset = transitionStore.preset
    currentPalette = transitionStore.palette
  } else {
    currentPreset = PRESETS[Math.floor(Math.random() * PRESETS.length)]
    currentPalette = PALETTES[Math.floor(Math.random() * PALETTES.length)]
  }

  // Set text color from palette
  const fg = currentPalette.fg
  fgColorCSS.value = `rgba(${Math.round(fg[0]*255)}, ${Math.round(fg[1]*255)}, ${Math.round(fg[2]*255)}, 0.9)`

  // Initialize Voronoi seeds
  for (let i = 0; i < 16; i++) {
    voronoiSeeds[i * 2] = 0.1 + Math.random() * 0.8
    voronoiSeeds[i * 2 + 1] = 0.1 + Math.random() * 0.8
  }

  if (initWebGL()) {
    // Warm up simulation to approximate where landing left off
    warmUp(80)
    render()

    // Build and start GSAP timeline
    requestAnimationFrame(() => {
      buildTimeline()
    })
  }

  // Start data fetch in parallel
  prefetchData()
})

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame)
  if (masterTimeline) masterTimeline.kill()

  if (gl) {
    textures.forEach(t => gl.deleteTexture(t))
    framebuffers.forEach(fb => gl.deleteFramebuffer(fb))
    if (quadBuffer) gl.deleteBuffer(quadBuffer)
    if (simulationProgram) gl.deleteProgram(simulationProgram)
    if (breakdownProgram) gl.deleteProgram(breakdownProgram)
  }
})
</script>

<template>
  <div class="loading-page">
    <canvas ref="canvasRef" class="canvas"></canvas>

    <div class="terms-container">
      <span
        v-for="(term, i) in nutritionTerms"
        :key="i"
        ref="termRefs"
        class="nutrition-term"
        :style="{ color: fgColorCSS }"
      >
        {{ term }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.loading-page {
  position: fixed;
  inset: 0;
  background: #1a1a1a;
  overflow: hidden;
}

.canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.terms-container {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.nutrition-term {
  position: absolute;
  font-size: 0.875rem;
  font-weight: 400;
  letter-spacing: 0.15em;
  opacity: 0;
  white-space: nowrap;
  will-change: transform, opacity;
}
</style>
