import * as THREE from 'three'
import { sampleBrainVoxels } from './particles/brainShape.js'
import { sampleDustPoints, DUST_BOUNDS } from './particles/dustShape.js'
import { samplePanelTargets } from './particles/panelShape.js'

const SILVER = new THREE.Color('#8A939B')
const WHITE = new THREE.Color('#FFFFFF')
const TEAL = new THREE.Color('#00E5A8')

const KIND_BRAIN = 1
const KIND_DUST = 2

const SPRING_K = 3.6
const DAMPING = 0.92
const MOUSE_RADIUS = 0.62
const MOUSE_FORCE = 4.0

const Z_AXIS = new THREE.Vector3(0, 0, 1)

// 粒子场：大脑体素 + 环境尘埃，共用一个 InstancedMesh
// 头部轮廓由 HeadWireframe（线网）承担，不再使用粒子
// 黑暗 = 未知意识（暗银微光）；鼠标照亮 = 探索（白）；青绿 = 神经活动
export class ParticleField {
  constructor(scene) {
    const brain = sampleBrainVoxels()
    const dust = sampleDustPoints(950)

    this.brainCount = brain.length / 3
    this.dustCount = dust.length / 3
    this.figureCount = this.brainCount
    this.count = this.figureCount + this.dustCount

    const n = this.count
    this.home = new Float32Array(n * 3)
    this.pos = new Float32Array(n * 3)
    this.vel = new Float32Array(n * 3)
    this.kind = new Uint8Array(n)
    this.size = new Float32Array(n)
    this.baseBright = new Float32Array(n)
    this.seed = new Float32Array(n)

    this._fill(0, brain, KIND_BRAIN, 0.03, 1.55)
    this._fill(this.figureCount, dust, KIND_DUST, 0.013, 0.55)

    // 尘埃的恒定漂移速度（vel 对尘埃即漂移）
    for (let i = this.figureCount; i < n; i++) {
      const ix = i * 3
      const speed = 0.03 + Math.random() * 0.07
      const angle = Math.random() * Math.PI * 2
      this.vel[ix] = Math.cos(angle) * speed
      this.vel[ix + 1] = (Math.random() - 0.5) * speed * 0.4
      this.vel[ix + 2] = 0
    }

    this.panelTargets = samplePanelTargets(this.figureCount)
    this.morphFrom = new Float32Array(this.figureCount * 3)
    this.morphDelay = new Float32Array(this.figureCount)

    // 渲染参数，由 NeuralScene / StartTransition 驱动
    this.params = {
      ambient: 0, // 人形粒子基础可见度（黑暗中若隐若现）
      ambientDust: 0.09,
      waveX: 0, // 唤醒青绿波前位置
      waveStrength: 0,
      sparkAmp: 0.55, // 神经火花强度
      speedGlow: 0, // 速度发光（转场数据流）
      tealSpeed: 0 // 高速粒子染青绿（数据流阶段）
    }

    const geo = new THREE.BoxGeometry(1, 1, 1)
    const mat = new THREE.MeshBasicMaterial()
    this.mesh = new THREE.InstancedMesh(geo, mat, n)
    this.mesh.frustumCulled = false
    this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage)
    scene.add(this.mesh)

    this._dummy = new THREE.Object3D()
    this._c = new THREE.Color()
    this._tc = new THREE.Color()
    this._dir = new THREE.Vector3()
  }

  _fill(offset, points, kind, size, bright) {
    const count = points.length / 3
    for (let i = 0; i < count; i++) {
      const g = offset + i
      const ix = g * 3
      const si = i * 3
      this.home[ix] = this.pos[ix] = points[si]
      this.home[ix + 1] = this.pos[ix + 1] = points[si + 1]
      this.home[ix + 2] = this.pos[ix + 2] = points[si + 2]
      this.kind[g] = kind
      this.size[g] = size * (0.8 + Math.random() * 0.45)
      this.baseBright[g] = bright * (0.7 + Math.random() * 0.6)
      this.seed[g] = Math.random()
    }
  }

  // 待机物理：弹簧回位 + 鼠标排斥（神经信号受扰动后缓慢恢复）+ 尘埃漂移
  updateIdle(dt, t, light) {
    const damp = Math.pow(DAMPING, dt * 60)
    const hasMouse = light.active
    const m = light.point

    for (let i = 0; i < this.figureCount; i++) {
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

    this.updateDust(dt, light)
  }

  updateDust(dt, light) {
    const hasMouse = light.active
    const m = light.point
    for (let i = this.figureCount; i < this.count; i++) {
      const ix = i * 3
      this.pos[ix] += this.vel[ix] * dt
      this.pos[ix + 1] += this.vel[ix + 1] * dt
      if (hasMouse) {
        const dx = this.pos[ix] - m.x
        const dy = this.pos[ix + 1] - m.y
        const d = Math.hypot(dx, dy)
        if (d < MOUSE_RADIUS * 0.8 && d > 1e-4) {
          const push = (1 - d / (MOUSE_RADIUS * 0.8)) * 0.35 * dt
          this.pos[ix] += (dx / d) * push
          this.pos[ix + 1] += (dy / d) * push
        }
      }
      if (this.pos[ix] > DUST_BOUNDS.x) this.pos[ix] = -DUST_BOUNDS.x
      else if (this.pos[ix] < -DUST_BOUNDS.x) this.pos[ix] = DUST_BOUNDS.x
      if (this.pos[ix + 1] > DUST_BOUNDS.y) this.pos[ix + 1] = -DUST_BOUNDS.y
      else if (this.pos[ix + 1] < -DUST_BOUNDS.y) this.pos[ix + 1] = DUST_BOUNDS.y
    }
  }

  // 每帧着色：暗银基底 → 鼠标照亮转白 → 青绿神经活动
  applyColors(t, light) {
    const P = this.params
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      const x = this.pos[ix]
      const y = this.pos[ix + 1]
      const z = this.pos[ix + 2]

      let lit = light.active ? light.intensityAt(x, y, z) : 0
      let speed = 0
      if (P.speedGlow > 0 || P.tealSpeed > 0) {
        speed = Math.hypot(this.vel[ix], this.vel[ix + 1], this.vel[ix + 2])
        if (P.speedGlow > 0) lit = Math.max(lit, Math.min(1, speed * 0.22) * P.speedGlow)
      }

      const isDust = this.kind[i] === KIND_DUST
      const base = this.baseBright[i] * (isDust ? P.ambientDust : P.ambient)
      this._c.copy(SILVER).lerp(WHITE, Math.min(1, lit * 0.85))
      this._c.multiplyScalar(base + lit * 0.95)

      let teal = 0
      if (this.kind[i] === KIND_BRAIN) {
        if (this.seed[i] > 0.92) {
          const s = Math.sin(t * 0.85 + this.seed[i] * 97)
          if (s > 0) teal += Math.pow(s, 8) * P.sparkAmp
        }
        if (P.waveStrength > 0) {
          const dx = x - P.waveX
          teal += P.waveStrength * Math.exp(-(dx * dx) / 0.06)
        }
      }
      if (!isDust && P.tealSpeed > 0 && speed > 0) {
        teal += Math.min(1, speed * 0.2) * P.tealSpeed
      }
      if (teal > 0) {
        this._tc.copy(TEAL).multiplyScalar(0.95)
        this._c.lerp(this._tc, Math.min(1, teal))
      }

      this.mesh.setColorAt(i, this._c)
    }
    this.mesh.instanceColor.needsUpdate = true
  }

  // stretch=true 时粒子沿速度方向拉伸，形成数据流拖尾
  writeMatrices(stretch, t) {
    const d = this._dummy
    for (let i = 0; i < this.count; i++) {
      const ix = i * 3
      let x = this.pos[ix]
      let y = this.pos[ix + 1]
      let z = this.pos[ix + 2]
      if (!stretch && this.kind[i] === KIND_BRAIN) {
        const s = this.seed[i] * 53
        x += Math.sin(t * 1.1 + s) * 0.005
        y += Math.cos(t * 0.9 + s * 1.7) * 0.005
      }
      d.position.set(x, y, z)
      const size = this.size[i]
      if (stretch) {
        const sp = Math.hypot(this.vel[ix], this.vel[ix + 1], this.vel[ix + 2])
        if (sp > 0.15) {
          this._dir.set(this.vel[ix], this.vel[ix + 1], this.vel[ix + 2]).normalize()
          d.quaternion.setFromUnitVectors(Z_AXIS, this._dir)
          d.scale.set(size, size, size * (1 + Math.min(2.2, sp * 0.45)))
        } else {
          d.quaternion.identity()
          d.scale.setScalar(size)
        }
      } else {
        d.quaternion.identity()
        d.scale.setScalar(size)
      }
      d.updateMatrix()
      this.mesh.setMatrixAt(i, d.matrix)
    }
    this.mesh.instanceMatrix.needsUpdate = true
  }

  dispose() {
    this.mesh.geometry.dispose()
    this.mesh.material.dispose()
  }
}
