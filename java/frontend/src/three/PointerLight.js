import * as THREE from 'three'

// 鼠标即光源：把指针投射到 z=0 平面上，提供高斯衰减的光照强度查询
export class PointerLight {
  constructor(camera) {
    this.camera = camera
    this.ndc = new THREE.Vector2()
    this.point = new THREE.Vector3()
    this.active = false
    this.sigma = 0.45
    this._raycaster = new THREE.Raycaster()
    this._plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)
    this._hit = new THREE.Vector3()
    this._hasHit = false
  }

  handleMove(clientX, clientY, rect) {
    this.ndc.x = ((clientX - rect.left) / rect.width) * 2 - 1
    this.ndc.y = -((clientY - rect.top) / rect.height) * 2 + 1
    this.active = true
  }

  update(dt) {
    if (!this.active) return
    this._raycaster.setFromCamera(this.ndc, this.camera)
    if (!this._raycaster.ray.intersectPlane(this._plane, this._hit)) return
    if (!this._hasHit) {
      this.point.copy(this._hit)
      this._hasHit = true
    } else {
      this.point.lerp(this._hit, 1 - Math.pow(0.0001, dt))
    }
  }

  intensityAt(x, y, z) {
    const dx = x - this.point.x
    const dy = y - this.point.y
    const dz = (z - this.point.z) * 0.7
    const d2 = dx * dx + dy * dy + dz * dz
    return Math.exp(-d2 / (2 * this.sigma * this.sigma))
  }
}
