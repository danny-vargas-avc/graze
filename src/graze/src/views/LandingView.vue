<script setup>
/**
 * Graze Landing Page - Reaction-Diffusion Art
 * Gray-Scott model using float textures for full precision
 */
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let gl = null
let animationFrame = null

// Pattern presets (f, k values that create interesting patterns)
const PRESETS = [
  { name: 'mitosis', f: 0.028, k: 0.062, seeds: 600 },
  { name: 'coral', f: 0.0545, k: 0.062, seeds: 20 },
  { name: 'maze', f: 0.029, k: 0.057, seeds: 20 },
  { name: 'bubbles', f: 0.012, k: 0.050, seeds: 25 },
  { name: 'waves', f: 0.014, k: 0.045, seeds: 20 },
  { name: 'worms', f: 0.040, k: 0.060, seeds: 20 },
]

// Color palettes (warm, organic tones)
const PALETTES = [
  { bg: [0.04, 0.04, 0.04], fg: [0.76, 0.55, 0.38] },  // charcoal + terracotta
  { bg: [0.04, 0.04, 0.04], fg: [0.55, 0.65, 0.45] },  // charcoal + olive
  { bg: [0.04, 0.04, 0.04], fg: [0.85, 0.70, 0.50] },  // charcoal + amber
  { bg: [0.04, 0.04, 0.04], fg: [0.45, 0.55, 0.50] },  // charcoal + sage
]

// Simulation state
let currentPreset = null
let currentPalette = null
let mouseX = 0.5
let mouseY = 0.5
let mouseActive = false
let mouseRadius = 0.03
let simWidth = 0
let simHeight = 0

// WebGL resources
let simulationProgram = null
let displayProgram = null
let textures = []
let framebuffers = []
let currentTexture = 0
let quadBuffer = null

// Shader sources
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
  uniform vec2 u_mouse;
  uniform float u_mouseActive;
  uniform float u_mouseRadius;
  uniform float u_dt;

  varying vec2 v_uv;

  void main() {
    vec2 texel = 1.0 / u_resolution;

    // Current state (stored in RG channels)
    vec4 state = texture2D(u_texture, v_uv);
    float a = state.r;
    float b = state.g;

    // Laplacian with 9-point stencil
    float la = -a;
    float lb = -b;

    // Cardinal directions (weight 0.2)
    la += texture2D(u_texture, v_uv + vec2(-texel.x, 0.0)).r * 0.2;
    la += texture2D(u_texture, v_uv + vec2(texel.x, 0.0)).r * 0.2;
    la += texture2D(u_texture, v_uv + vec2(0.0, -texel.y)).r * 0.2;
    la += texture2D(u_texture, v_uv + vec2(0.0, texel.y)).r * 0.2;

    lb += texture2D(u_texture, v_uv + vec2(-texel.x, 0.0)).g * 0.2;
    lb += texture2D(u_texture, v_uv + vec2(texel.x, 0.0)).g * 0.2;
    lb += texture2D(u_texture, v_uv + vec2(0.0, -texel.y)).g * 0.2;
    lb += texture2D(u_texture, v_uv + vec2(0.0, texel.y)).g * 0.2;

    // Diagonal directions (weight 0.05)
    la += texture2D(u_texture, v_uv + vec2(-texel.x, -texel.y)).r * 0.05;
    la += texture2D(u_texture, v_uv + vec2(texel.x, -texel.y)).r * 0.05;
    la += texture2D(u_texture, v_uv + vec2(-texel.x, texel.y)).r * 0.05;
    la += texture2D(u_texture, v_uv + vec2(texel.x, texel.y)).r * 0.05;

    lb += texture2D(u_texture, v_uv + vec2(-texel.x, -texel.y)).g * 0.05;
    lb += texture2D(u_texture, v_uv + vec2(texel.x, -texel.y)).g * 0.05;
    lb += texture2D(u_texture, v_uv + vec2(-texel.x, texel.y)).g * 0.05;
    lb += texture2D(u_texture, v_uv + vec2(texel.x, texel.y)).g * 0.05;

    // Diffusion rates
    float Da = 1.0;
    float Db = 0.5;

    // Feed and kill rates
    float f = u_feed;
    float k = u_kill;

    // Mouse/touch interaction - adds B chemical
    float mouseDist = distance(v_uv, u_mouse);
    float mouseInfluence = smoothstep(u_mouseRadius, 0.0, mouseDist) * u_mouseActive;

    // Gray-Scott equations
    float abb = a * b * b;
    float da = Da * la - abb + f * (1.0 - a);
    float db = Db * lb + abb - (k + f) * b;

    // Update with timestep
    a = clamp(a + da * u_dt, 0.0, 1.0);
    b = clamp(b + db * u_dt + mouseInfluence * 0.1, 0.0, 1.0);

    gl_FragColor = vec4(a, b, 0.0, 1.0);
  }
`

const displayShaderSource = `
  precision highp float;

  uniform sampler2D u_texture;
  uniform vec2 u_resolution;
  uniform vec3 u_bgColor;
  uniform vec3 u_fgColor;

  varying vec2 v_uv;

  void main() {
    vec2 texel = 1.0 / u_resolution;

    // Sample B channel and neighbors for gradient
    float b = texture2D(u_texture, v_uv).g;
    float bL = texture2D(u_texture, v_uv + vec2(-texel.x, 0.0)).g;
    float bR = texture2D(u_texture, v_uv + vec2(texel.x, 0.0)).g;
    float bD = texture2D(u_texture, v_uv + vec2(0.0, -texel.y)).g;
    float bU = texture2D(u_texture, v_uv + vec2(0.0, texel.y)).g;

    // Sobel-like gradient magnitude
    float gx = bR - bL;
    float gy = bU - bD;
    float edge = sqrt(gx * gx + gy * gy);

    // Simulated light direction (top-left)
    float light = (gx + gy) * 2.0;

    // Base color from B concentration
    vec3 base = mix(u_bgColor, u_fgColor, b);

    // Add embossed edges: bright on light side, dark on shadow side
    vec3 highlight = base + vec3(0.12) * light;
    vec3 color = highlight + edge * vec3(0.08);

    gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
  }
`

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
    preserveDrawingBuffer: false
  })

  if (!gl) {
    console.error('WebGL not supported')
    return false
  }

  // Enable float textures for simulation precision
  const floatExt = gl.getExtension('OES_texture_float')
  if (!floatExt) {
    console.error('OES_texture_float not supported')
    return false
  }
  // Optional: linear filtering for float textures
  gl.getExtension('OES_texture_float_linear')

  // Create programs
  simulationProgram = createProgram(vertexShaderSource, simulationShaderSource)
  displayProgram = createProgram(vertexShaderSource, displayShaderSource)

  if (!simulationProgram || !displayProgram) {
    console.error('Failed to create shader programs')
    return false
  }

  // Create quad geometry
  quadBuffer = gl.createBuffer()
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer)
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    -1, -1, 1, -1, -1, 1,
    -1, 1, 1, -1, 1, 1
  ]), gl.STATIC_DRAW)

  // Initialize textures and framebuffers
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

  // Use lower resolution for simulation (performance)
  simWidth = Math.floor(width * 0.5)
  simHeight = Math.floor(height * 0.5)

  // Recreate textures at new size
  createTextures()
}

function createTextures() {
  // Clean up old resources
  textures.forEach(t => gl.deleteTexture(t))
  framebuffers.forEach(fb => gl.deleteFramebuffer(fb))
  textures = []
  framebuffers = []

  // Create ping-pong textures using FLOAT for precision
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

  // Initialize state
  initializeState()
}

function initializeState() {
  const data = new Float32Array(simWidth * simHeight * 4)

  // Fill with A=1.0, B=0.0
  for (let i = 0; i < simWidth * simHeight; i++) {
    data[i * 4 + 0] = 1.0  // A
    data[i * 4 + 1] = 0.0  // B
    data[i * 4 + 2] = 0.0
    data[i * 4 + 3] = 1.0
  }

  // Seed random spots of B chemical
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
          data[idx + 0] = 0.5 + 0.25 * falloff  // A reduced
          data[idx + 1] = 0.25 + 0.75 * falloff  // B seeded
        }
      }
    }
  }

  // Upload to both textures
  for (let i = 0; i < 2; i++) {
    gl.bindTexture(gl.TEXTURE_2D, textures[i])
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, simWidth, simHeight, 0, gl.RGBA, gl.FLOAT, data)
  }
}

function simulate() {
  gl.useProgram(simulationProgram)

  // Bind source texture
  gl.activeTexture(gl.TEXTURE0)
  gl.bindTexture(gl.TEXTURE_2D, textures[currentTexture])
  gl.uniform1i(gl.getUniformLocation(simulationProgram, 'u_texture'), 0)

  // Set uniforms
  gl.uniform2f(gl.getUniformLocation(simulationProgram, 'u_resolution'), simWidth, simHeight)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_feed'), currentPreset.f)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_kill'), currentPreset.k)
  gl.uniform2f(gl.getUniformLocation(simulationProgram, 'u_mouse'), mouseX, mouseY)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_mouseActive'), mouseActive ? 1.0 : 0.0)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_mouseRadius'), mouseRadius)
  gl.uniform1f(gl.getUniformLocation(simulationProgram, 'u_dt'), 1.0)

  // Render to other texture
  const nextTexture = 1 - currentTexture
  gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffers[nextTexture])
  gl.viewport(0, 0, simWidth, simHeight)

  // Draw
  const posLoc = gl.getAttribLocation(simulationProgram, 'a_position')
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer)
  gl.enableVertexAttribArray(posLoc)
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)
  gl.drawArrays(gl.TRIANGLES, 0, 6)

  currentTexture = nextTexture
}

function display() {
  gl.useProgram(displayProgram)

  // Get locations
  const texLoc = gl.getUniformLocation(displayProgram, 'u_texture')
  const posLoc = gl.getAttribLocation(displayProgram, 'a_position')

  // Bind result texture (use current after simulation)
  gl.activeTexture(gl.TEXTURE0)
  gl.bindTexture(gl.TEXTURE_2D, textures[currentTexture])
  gl.uniform1i(texLoc, 0)

  // Set uniforms
  gl.uniform2f(gl.getUniformLocation(displayProgram, 'u_resolution'), simWidth, simHeight)
  gl.uniform3f(gl.getUniformLocation(displayProgram, 'u_bgColor'),
    currentPalette.bg[0], currentPalette.bg[1], currentPalette.bg[2])
  gl.uniform3f(gl.getUniformLocation(displayProgram, 'u_fgColor'),
    currentPalette.fg[0], currentPalette.fg[1], currentPalette.fg[2])

  // Render to screen
  gl.bindFramebuffer(gl.FRAMEBUFFER, null)
  gl.viewport(0, 0, canvasRef.value.width, canvasRef.value.height)

  // Draw
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer)
  gl.enableVertexAttribArray(posLoc)
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)
  gl.drawArrays(gl.TRIANGLES, 0, 6)
}

function render() {
  // Run multiple simulation steps per frame for faster evolution
  for (let i = 0; i < 8; i++) {
    simulate()
  }

  display()

  animationFrame = requestAnimationFrame(render)
}

function onMouseMove(e) {
  mouseX = e.clientX / window.innerWidth
  mouseY = 1.0 - (e.clientY / window.innerHeight)
  mouseActive = true
}

function onMouseLeave() {
  mouseActive = false
}

function onTouchMove(e) {
  e.preventDefault()
  if (e.touches.length > 0) {
    mouseX = e.touches[0].clientX / window.innerWidth
    mouseY = 1.0 - (e.touches[0].clientY / window.innerHeight)
    mouseActive = true
  }
}

function onTouchEnd() {
  mouseActive = false
}

function onResize() {
  resizeCanvas()
}

onMounted(() => {
  // Larger touch radius on mobile
  const isMobile = 'ontouchstart' in window || window.innerWidth < 768
  mouseRadius = isMobile ? 0.08 : 0.03

  // Pick random preset and palette
  currentPreset = PRESETS[Math.floor(Math.random() * PRESETS.length)]
  currentPalette = PALETTES[Math.floor(Math.random() * PALETTES.length)]

  console.log('Starting reaction-diffusion with preset:', currentPreset.name)

  if (initWebGL()) {
    render()
  }

  window.addEventListener('resize', onResize)
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseleave', onMouseLeave)
  window.addEventListener('touchmove', onTouchMove, { passive: false })
  window.addEventListener('touchend', onTouchEnd)
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }

  window.removeEventListener('resize', onResize)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseleave', onMouseLeave)
  window.removeEventListener('touchmove', onTouchMove)
  window.removeEventListener('touchend', onTouchEnd)

  // Cleanup WebGL resources
  if (gl) {
    textures.forEach(t => gl.deleteTexture(t))
    framebuffers.forEach(fb => gl.deleteFramebuffer(fb))
    if (quadBuffer) gl.deleteBuffer(quadBuffer)
    if (simulationProgram) gl.deleteProgram(simulationProgram)
    if (displayProgram) gl.deleteProgram(displayProgram)
  }
})
</script>

<template>
  <div class="landing">
    <canvas ref="canvasRef" class="canvas"></canvas>

    <div class="content">
      <h1 class="logo">Graze</h1>
      <router-link to="/search" class="enter">
        Enter
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.landing {
  position: fixed;
  inset: 0;
  background: #0a0a0a;
  overflow: hidden;
}

.canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-start;
  padding: 3rem;
  pointer-events: none;
}

.logo {
  font-size: clamp(2.5rem, 8vw, 5rem);
  font-weight: 300;
  letter-spacing: -0.02em;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 1.5rem 0;
  mix-blend-mode: difference;
}

.enter {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 400;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  pointer-events: auto;
  transition: color 0.3s ease;
}

.enter:hover {
  color: rgba(255, 255, 255, 0.9);
}

.enter svg {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.enter:hover svg {
  transform: translateX(4px);
}
</style>
