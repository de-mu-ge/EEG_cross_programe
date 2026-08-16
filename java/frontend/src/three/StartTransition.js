// 点击 START ANALYSIS 后的转场状态机：
// awaken(空间唤醒，青绿波扫过大脑) → dissolve(大脑解构散开)
// → morph(重组为上传面板) → panel(微光颤动)
const DURATIONS = { awaken: 1.5, dissolve: 1.1, morph: 1.7 }
const MORPH_DELAY_SPREAD = 0.3
const AMBIENT_IDLE = 0.12

function smooth(p) {
  return p * p * (3 - 2 * p)
}

export class StartTransition {
  constructor(field, { onFormed } = {}) {
    this.field = field
    this.onFormed = onFormed
    this.active = false
    this.phase = null
    this.time = 0
    this.stretch = false
  }

  start() {
    if (this.active) return
    this.active = true
    this._enter('awaken')
  }

  _enter(phase) {
    this.phase = phase
    this.time = 0
    const f = this.field

    if (phase === 'dissolve') {
      for (let i = 0; i < f.figureCount; i++) {
        const ix = i * 3
        const dx = f.pos[ix] + (Math.random() - 0.5) * 1.4
        const dy = f.pos[ix + 1] - 0.1 + (Math.random() - 0.5) * 1.4
        const dz = f.pos[ix + 2] + (Math.random() - 0.5) * 1.4
        const len = Math.hypot(dx, dy, dz) || 1
        // 适度分散：保持在画面内，避免重组前出现黑屏空窗
        const speed = 0.55 + Math.random() * 0.7
        f.vel[ix] = (dx / len) * speed
        f.vel[ix + 1] = (dy / len) * speed + 0.3
        f.vel[ix + 2] = (dz / len) * speed * 0.5
      }
      this.stretch = true
    }

    if (phase === 'morph') {
      f.morphFrom.set(f.pos.subarray(0, f.figureCount * 3))
      f.vel.fill(0)
      for (let i = 0; i < f.figureCount; i++) f.morphDelay[i] = Math.random() * MORPH_DELAY_SPREAD
      this.stretch = false
    }

    if (phase === 'panel') {
      if (this.onFormed) this.onFormed()
    }
  }

  update(dt, t, light) {
    const f = this.field
    const P = f.params
    this.time += dt

    switch (this.phase) {
      case 'awaken': {
        const p = Math.min(1, this.time / DURATIONS.awaken)
        P.ambient = AMBIENT_IDLE + (0.3 - AMBIENT_IDLE) * smooth(p)
        P.waveX = -1.35 + 2.7 * p
        P.waveStrength = Math.sin(p * Math.PI) * 1.3
        f.updateIdle(dt, t, light)
        // 粒子开始流动：给大脑粒子叠加轻微扰动
        const env = Math.sin(p * Math.PI) * 2.4 * dt
        for (let i = 0; i < f.figureCount; i++) {
          const ix = i * 3
          f.vel[ix] += (Math.random() - 0.5) * env
          f.vel[ix + 1] += (Math.random() - 0.5) * env
          f.vel[ix + 2] += (Math.random() - 0.5) * env
        }
        if (p >= 1) this._enter('dissolve')
        break
      }

      case 'dissolve': {
        const p = Math.min(1, this.time / DURATIONS.dissolve)
        P.ambient = 0.3 + (0.24 - 0.3) * smooth(p)
        P.waveStrength *= Math.pow(0.02, dt)
        P.speedGlow = smooth(Math.min(1, p * 2))
        const damp = Math.pow(0.986, dt * 60)
        for (let i = 0; i < f.figureCount * 3; i++) {
          f.vel[i] *= damp
          f.pos[i] += f.vel[i] * dt
        }
        if (p >= 1) this._enter('morph')
        break
      }

      case 'morph': {
        P.speedGlow = Math.max(0.15, P.speedGlow - dt * 0.8)
        P.ambient += (0.5 - P.ambient) * Math.min(1, dt * 2)
        let settled = 0
        for (let i = 0; i < f.figureCount; i++) {
          const ix = i * 3
          const local = Math.min(1, Math.max(0, (this.time - f.morphDelay[i]) / DURATIONS.morph))
          const e = local < 0.5 ? 4 * local ** 3 : 1 - Math.pow(-2 * local + 2, 3) / 2
          f.pos[ix] = f.morphFrom[ix] + (f.panelTargets[ix] - f.morphFrom[ix]) * e
          f.pos[ix + 1] = f.morphFrom[ix + 1] + (f.panelTargets[ix + 1] - f.morphFrom[ix + 1]) * e
          f.pos[ix + 2] = f.morphFrom[ix + 2] + (f.panelTargets[ix + 2] - f.morphFrom[ix + 2]) * e
          if (local >= 1) settled++
        }
        if (settled === f.figureCount) this._enter('panel')
        break
      }

      case 'panel': {
        P.speedGlow = Math.max(0, P.speedGlow - dt * 0.5)
        P.sparkAmp = 0.5
        for (let i = 0; i < f.figureCount; i++) {
          const ix = i * 3
          f.pos[ix] = f.panelTargets[ix] + Math.sin(t * 1.6 + i * 0.7) * 0.005
          f.pos[ix + 1] = f.panelTargets[ix + 1] + Math.cos(t * 1.4 + i * 1.3) * 0.005
          f.pos[ix + 2] = f.panelTargets[ix + 2]
        }
        break
      }
    }
  }
}
