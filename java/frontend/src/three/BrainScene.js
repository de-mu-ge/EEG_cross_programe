import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js'

const COLOR_BLUE = new THREE.Color('#3d6bff')
const COLOR_PURPLE = new THREE.Color('#a04dff')
const BG_COLOR = '#05060f'

const MOUSE_RADIUS = 0.7
const MOUSE_FORCE = 5.5
const SPRING_K = 6.0
const DAMPING = 0.9

const DISSOLVE_DURATION = 1.15
const MORPH_DURATION = 1.35
const MORPH_DELAY_SPREAD = 0.45

function buildBrainVoxels() {
  // 体素网格填充椭球，留出左右半球中缝
  const spacing = 0.085
  const rx = 0.82, ry = 0.62, rz = 0.7
  const cy = 0.15
  const points = []
  for (let x = -rx; x <= rx; x += spacing) {
    for (let y = -ry; y <= ry; y += spacing) {
      for (let z = -rz; z <= rz; z += spacing) {
        const n = (x * x) / (rx * rx) + (y * y) / (ry * ry) + (z * z) / (rz * rz)
        if (n > 1) continue
        if (Math.abs(x) < 0.05) continue
        if (y < -0.4) continue
        points.push(
          x + (Math.random() - 0.5) * 0.012,
          cy + y + (Math.random() - 0.5) * 0.012,
          z + (Math.random() - 0.5) * 0.012
        )
      }
    }
  }
  return points
}

function superellipsePoint(theta, a, b, n) {
  const c = Math.cos(theta)
  const s = Math.sin(theta)
  const p = 2 / n
  return [
    a * Math.sign(c) * Math.pow(Math.abs(c), p),
    b * Math.sign(s) * Math.pow(Math.abs(s), p)
  ]
}

function buildPanelTarget(count) {
  // 上传面板轮廓：超椭圆边框 + 上传箭头 + 底部横线
  const targets = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    const r = Math.random()
    let x, y
    if (r < 0.68) {
      ;[x, y] = superellipsePoint(Math.random() * Math.PI * 2, 1.65, 1.0, 4.5)
    } else if (r < 0.9) {
      const seg = Math.random()
      if (seg < 0.5) {
        x = 0
        y = -0.3 + Math.random() * 0.6
      } else {
        const t = Math.random()
        const side = Math.random() < 0.5 ? -1 : 1
        x = side * t * 0.22
        y = 0.3 - t * 0.26
      }
    } else {
      x = -0.42 + Math.random() * 0.84
      y = -0.6
    }
    targets[i * 3] = x + (Math.random() - 0.5) * 0.02
    targets[i * 3 + 1] = y + (Math.random() - 0.5) * 0.02
    targets[i * 3 + 2] = (Math.random() - 0.5) * 0.03
  }
  return targets
}

function buildHeadGeometry() {
  const geo = new THREE.SphereGeometry(1.12, 26, 20)
  const pos = geo.attributes.position
  for (let i = 0; i < pos.count; i++) {
    let x = pos.getX(i)
    let y = pos.getY(i) * 1.15
    let z = pos.getZ(i)
    if (y < -0.2) {
      // 下颌收缩
      const k = Math.min(1, (-y - 0.2) / 1.09)
      const s = 1 - 0.48 * k * k
      x *= s
      z *= s
    }
    x *= 0.92
    z *= 0.98
    pos.setXYZ(i, x, y, z)
  }
  return geo
}

export class BrainScene {
  constructor(container, { onFormed } = {}) {
    this.container = container
    this.onFormed = onFormed
    this.phase = 'idle'
    this.phaseTime = 0
    this.clock = new THREE.Clock()
    this.pointer = new THREE.Vector2()
    this.pointerActive = false
    this._raycaster = new THREE.Raycaster()
    this._plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)
    this._mouseLocal = new THREE.Vector3()
    this._dummy = new THREE.Object3D()
    this._disposed = false

    this._initRenderer()
    this._initScene()
    this._initHead()
    this._initBrain()
    this._bindEvents()
    this._onResize()
    this._animate()
  }

  _initRenderer() {
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.setClearColor(BG_COLOR)
    this.container.appendChild(this.renderer.domElement)
  }

  _initScene() {
    this.scene = new THREE.Scene()
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100)
    this.camera.position.set(0, 0.1, 4.6)
    this.camera.lookAt(0, 0.05, 0)

    this.root = new THREE.Group()
    this.scene.add(this.root)

    this.composer = new EffectComposer(this.renderer)
    this.composer.addPass(new RenderPass(this.scene, this.camera))
    this.bloomPass = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.85, 0.55, 0.12)
    this.composer.addPass(this.bloomPass)
    this.composer.addPass(new OutputPass())
  }

  _initHead() {
    this.headMaterial = new THREE.MeshBasicMaterial({
      color: 0x4a6cff,
      wireframe: true,
      transparent: true,
      opacity: 0.14,
      depthWrite: false
    })
    this.head = new THREE.Mesh(buildHeadGeometry(), this.headMaterial)
    this.root.add(this.head)
  }

  _initBrain() {
    const voxels = buildBrainVoxels()
    this.count = voxels.length / 3
    this.home = new Float32Array(voxels)
    this.pos = new Float32Array(voxels)
    this.vel = new Float32Array(this.count * 3)
    this.target = buildPanelTarget(this.count)
    this.morphFrom = new Float32Array(this.count * 3)
    this.morphDelay = new Float32Array(this.count)
    for (let i = 0; i < this.count; i++) this.morphDelay[i] = Math.random() * MORPH_DELAY_SPREAD

    const geo = new THREE.BoxGeometry(0.032, 0.032, 0.032)
    const mat = new THREE.MeshBasicMaterial()
    this.brain = new THREE.InstancedMesh(geo, mat, this.count)

    const color = new THREE.Color()
    for (let i = 0; i < this.count; i++) {
      const t = Math.min(1, Math.max(0, 0.5 + this.home[i * 3] * 0.55 + (Math.random() - 0.5) * 0.5))
      color.lerpColors(COLOR_BLUE, COLOR_PURPLE, t).multiplyScalar(1.25)
      this.brain.setColorAt(i, color)
    }
    this.brain.instanceColor.needsUpdate = true
    this.brainGroup = new THREE.Group()
    this.brainGroup.add(this.brain)
    this.root.add(this.brainGroup)
  }

  _bindEvents() {
    this._onPointerMove = (e) => {
      const rect = this.renderer.domElement.getBoundingClientRect()
      this.pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
      this.pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
      this.pointerActive = true
    }
    this._onPointerLeave = () => {
      this.pointerActive = false
    }
    this._resizeHandler = () => this._onResize()
    window.addEventListener('pointermove', this._onPointerMove)
    window.addEventListener('pointerleave', this._onPointerLeave)
    window.addEventListener('resize', this._resizeHandler)
  }

  _onResize() {
    const w = this.container.clientWidth
    const h = this.container.clientHeight
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(w, h)
    this.composer.setSize(w, h)
    // 宽屏时模型右移，为左侧文案留出空间（转场后面板居中）
    this.root.position.x = this.phase === 'idle' && this.camera.aspect > 1.2 ? 0.55 : 0
  }

  startTransition() {
    if (this.phase !== 'idle') return
    this.phase = 'dissolve'
    this.phaseTime = 0
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      const dx = this.home[ix] + (Math.random() - 0.5) * 1.6
      const dy = this.home[ix + 1] - 0.15 + (Math.random() - 0.5) * 1.6
      const dz = this.home[ix + 2] + (Math.random() - 0.5) * 1.6
      const len = Math.hypot(dx, dy, dz) || 1
      const speed = 1.6 + Math.random() * 2.2
      this.vel[ix] = (dx / len) * speed
      this.vel[ix + 1] = (dy / len) * speed
      this.vel[ix + 2] = (dz / len) * speed
    }
  }

  _updateIdle(dt, t) {
    const hasMouse = this.pointerActive && this._updateMouseLocal()
    const m = this._mouseLocal
    const damp = Math.pow(DAMPING, dt * 60)
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      let ax = (this.home[ix] - this.pos[ix]) * SPRING_K
      let ay = (this.home[ix + 1] - this.pos[ix + 1]) * SPRING_K
      let az = (this.home[ix + 2] - this.pos[ix + 2]) * SPRING_K
      if (hasMouse) {
        const dx = this.pos[ix] - m.x
        const dy = this.pos[ix + 1] - m.y
        const dz = this.pos[ix + 2] - m.z
        const d = Math.hypot(dx, dy, dz)
        if (d < MOUSE_RADIUS && d > 1e-4) {
          const f = Math.pow(1 - d / MOUSE_RADIUS, 2) * MOUSE_FORCE
          ax += (dx / d) * f
          ay += (dy / d) * f
          az += (dz / d) * f * 0.6
        }
      }
      this.vel[ix] = (this.vel[ix] + ax * dt) * damp
      this.vel[ix + 1] = (this.vel[ix + 1] + ay * dt) * damp
      this.vel[ix + 2] = (this.vel[ix + 2] + az * dt) * damp
      this.pos[ix] += this.vel[ix] * dt
      this.pos[ix + 1] += this.vel[ix + 1] * dt
      this.pos[ix + 2] += this.vel[ix + 2] * dt
    }
    const breath = 1 + 0.015 * Math.sin(t * 1.2)
    this.brainGroup.scale.setScalar(breath)
    this.brainGroup.rotation.y = Math.sin(t * 0.35) * 0.12
    this.head.rotation.y = this.brainGroup.rotation.y
  }

  _updateDissolve(dt) {
    const damp = Math.pow(0.985, dt * 60)
    for (let i = 0; i < this.count * 3; i++) {
      this.vel[i] *= damp
      this.pos[i] += this.vel[i] * dt
    }
    this.headMaterial.opacity = Math.max(0, 0.14 * (1 - this.phaseTime / 0.8))
    this.head.visible = this.headMaterial.opacity > 0.001
    if (this.phaseTime >= DISSOLVE_DURATION) {
      this.phase = 'morph'
      this.phaseTime = 0
      this.morphFrom.set(this.pos)
      this.vel.fill(0)
    }
  }

  _updateMorph(dt) {
    this.root.position.x += (0 - this.root.position.x) * Math.min(1, dt * 2.5)
    let settled = 0
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      const local = Math.min(1, Math.max(0, (this.phaseTime - this.morphDelay[i]) / MORPH_DURATION))
      const e = local < 0.5 ? 4 * local ** 3 : 1 - Math.pow(-2 * local + 2, 3) / 2
      this.pos[ix] = this.morphFrom[ix] + (this.target[ix] - this.morphFrom[ix]) * e
      this.pos[ix + 1] = this.morphFrom[ix + 1] + (this.target[ix + 1] - this.morphFrom[ix + 1]) * e
      this.pos[ix + 2] = this.morphFrom[ix + 2] + (this.target[ix + 2] - this.morphFrom[ix + 2]) * e
      if (local >= 1) settled++
    }
    this.brainGroup.rotation.y *= 0.95
    this.brainGroup.scale.setScalar(1)
    if (settled === this.count) {
      this.phase = 'panel'
      this.phaseTime = 0
      if (this.onFormed) this.onFormed()
    }
  }

  _updatePanel(t) {
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      this.pos[ix] = this.target[ix] + Math.sin(t * 1.6 + i * 0.7) * 0.006
      this.pos[ix + 1] = this.target[ix + 1] + Math.cos(t * 1.4 + i * 1.3) * 0.006
      this.pos[ix + 2] = this.target[ix + 2]
    }
  }

  _updateMouseLocal() {
    this._raycaster.setFromCamera(this.pointer, this.camera)
    const hit = new THREE.Vector3()
    if (!this._raycaster.ray.intersectPlane(this._plane, hit)) return false
    this.brainGroup.worldToLocal(this._mouseLocal.copy(hit))
    return true
  }

  _writeMatrices() {
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      this._dummy.position.set(this.pos[ix], this.pos[ix + 1], this.pos[ix + 2])
      this._dummy.updateMatrix()
      this.brain.setMatrixAt(i, this._dummy.matrix)
    }
    this.brain.instanceMatrix.needsUpdate = true
  }

  _animate() {
    if (this._disposed) return
    this._raf = requestAnimationFrame(() => this._animate())
    const dt = Math.min(this.clock.getDelta(), 0.05)
    const t = this.clock.elapsedTime
    this.phaseTime += dt

    if (this.phase === 'idle') this._updateIdle(dt, t)
    else if (this.phase === 'dissolve') this._updateDissolve(dt)
    else if (this.phase === 'morph') this._updateMorph(dt)
    else this._updatePanel(t)

    this._writeMatrices()
    this.composer.render()
  }

  dispose() {
    this._disposed = true
    cancelAnimationFrame(this._raf)
    window.removeEventListener('pointermove', this._onPointerMove)
    window.removeEventListener('pointerleave', this._onPointerLeave)
    window.removeEventListener('resize', this._resizeHandler)
    this.head.geometry.dispose()
    this.headMaterial.dispose()
    this.brain.geometry.dispose()
    this.brain.material.dispose()
    this.composer.dispose()
    this.renderer.dispose()
    this.renderer.domElement.remove()
  }
}
