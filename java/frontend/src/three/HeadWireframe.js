import * as THREE from 'three'

// 头部轮廓线网：变形椭球网格 + 顶点抖动，呈不规则三角网（参考图的 neural net 样式）
// 极暗的银线，承载内部粒子大脑；转场启动后整体淡出
const OPACITY = 0.1

// 与 headShape 粒子版一致的头部比例与下颌收缩；略去五官细节（线网上只会是噪点）
// 纵向略短、横向略宽的椭圆轮廓
function deform(x, y, z) {
  x *= 1.02
  y *= 1.1
  z *= 1.0
  if (y < -0.05) {
    const k = Math.min(1, (-y - 0.05) / 1.05)
    const s = 1 - 0.55 * k * k
    x *= s
    z *= s
    z += 0.05 * k
  }
  if (z < -0.2) z *= 1.1
  if (z > 0.6 && Math.abs(x) < 0.6 && y > -0.7 && y < 0.7) {
    z = 0.6 + (z - 0.6) * 0.5
  }
  return [x, y, z]
}

// 位置哈希伪随机：接缝处同一坐标的抖动一致，避免裂缝
function hash3(x, y, z) {
  const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453
  return s - Math.floor(s)
}

export class HeadWireframe {
  constructor(scene) {
    const geo = new THREE.SphereGeometry(1, 12, 16)
    const pos = geo.attributes.position
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i)
      const y = pos.getY(i)
      const z = pos.getZ(i)
      const j = 0.05
      const jx = (hash3(x, y, z) - 0.5) * j
      const jy = (hash3(y, z, x) - 0.5) * j
      const jz = (hash3(z, x, y) - 0.5) * j
      const [dx, dy, dz] = deform(x + jx, y + jy, z + jz)
      pos.setXYZ(i, dx, dy, dz)
    }

    const wire = new THREE.WireframeGeometry(geo)
    geo.dispose()
    this.material = new THREE.LineBasicMaterial({
      color: '#8A939B',
      transparent: true,
      opacity: OPACITY,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    })
    this.mesh = new THREE.LineSegments(wire, this.material)
    this.mesh.frustumCulled = false
    this.fade = 1
    this.fadeTarget = 1
    scene.add(this.mesh)
  }

  fadeToward(target) {
    this.fadeTarget = target
  }

  update(dt) {
    this.fade += (this.fadeTarget - this.fade) * Math.min(1, dt * 1.6)
    const visible = this.fade > 0.01
    this.mesh.visible = visible
    if (visible) this.material.opacity = OPACITY * this.fade
  }

  dispose() {
    this.mesh.geometry.dispose()
    this.material.dispose()
  }
}
