import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js'
import { ParticleField } from './ParticleField.js'
import { HeadWireframe } from './HeadWireframe.js'
import { PointerLight } from './PointerLight.js'
import { StartTransition } from './StartTransition.js'

const BG_COLOR = '#030303'
const AMBIENT_IDLE = 0.1

// 场景编排：渲染器 / 辉光后期 / 相机视差 / 主循环
export class NeuralScene {
  constructor(container, { onFormed } = {}) {
    this.container = container
    this.clock = new THREE.Clock()
    this.parallaxWeight = 1
    this._disposed = false

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.setClearColor(BG_COLOR)
    container.appendChild(this.renderer.domElement)

    this.scene = new THREE.Scene()
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100)
    this.camera.position.set(0, 0.05, 4.7)
    this.camera.lookAt(0, 0.05, 0)

    this.composer = new EffectComposer(this.renderer)
    this.composer.addPass(new RenderPass(this.scene, this.camera))
    this.composer.addPass(new UnrealBloomPass(new THREE.Vector2(1, 1), 0.5, 0.55, 0.2))
    this.composer.addPass(new OutputPass())

    this.field = new ParticleField(this.scene)
    this.field.params.ambient = AMBIENT_IDLE
    this.headMesh = new HeadWireframe(this.scene)
    this.light = new PointerLight(this.camera)
    this.transition = new StartTransition(this.field, { onFormed })

    this._camTarget = new THREE.Vector3()
    this._bindEvents()
    this._onResize()
    this._animate()
  }

  _bindEvents() {
    this._onPointerMove = (e) => {
      const rect = this.renderer.domElement.getBoundingClientRect()
      this.light.handleMove(e.clientX, e.clientY, rect)
    }
    this._onPointerLeave = () => {
      this.light.active = false
    }
    this._resizeHandler = () => this._onResize()
    window.addEventListener('pointermove', this._onPointerMove)
    document.documentElement.addEventListener('mouseleave', this._onPointerLeave)
    window.addEventListener('resize', this._resizeHandler)
  }

  _onResize() {
    const w = this.container.clientWidth
    const h = this.container.clientHeight
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(w, h)
    this.composer.setSize(w, h)
  }

  startTransition() {
    this.transition.start()
  }

  _animate() {
    if (this._disposed) return
    this._raf = requestAnimationFrame(() => this._animate())
    const dt = Math.min(this.clock.getDelta(), 0.05)
    const t = this.clock.elapsedTime

    this.light.update(dt)
    this.headMesh.fadeToward(this.transition.active ? 0 : 1)
    this.headMesh.update(dt)

    if (this.transition.active) {
      this.transition.update(dt, t, this.light)
      this.field.updateDust(dt, this.light)
    } else {
      this.field.updateIdle(dt, t, this.light)
    }
    this.field.applyColors(t, this.light)
    this.field.writeMatrices(this.transition.stretch, t)

    // 轻微相机视差，增强空间感；转场时收回正中
    const targetW = this.transition.active ? 0 : 1
    this.parallaxWeight += (targetW - this.parallaxWeight) * Math.min(1, dt * 2)
    const px = this.light.active ? this.light.ndc.x : 0
    const py = this.light.active ? this.light.ndc.y : 0
    this._camTarget.set(px * 0.14 * this.parallaxWeight, 0.05 + py * 0.1 * this.parallaxWeight, 4.7)
    this.camera.position.lerp(this._camTarget, 1 - Math.pow(0.001, dt))
    this.camera.lookAt(0, 0.05, 0)

    this.composer.render()
  }

  dispose() {
    this._disposed = true
    cancelAnimationFrame(this._raf)
    window.removeEventListener('pointermove', this._onPointerMove)
    document.documentElement.removeEventListener('mouseleave', this._onPointerLeave)
    window.removeEventListener('resize', this._resizeHandler)
    this.field.dispose()
    this.headMesh.dispose()
    this.composer.dispose()
    this.renderer.dispose()
    this.renderer.domElement.remove()
  }
}
