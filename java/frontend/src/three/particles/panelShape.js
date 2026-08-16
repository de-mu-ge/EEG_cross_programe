// 纯函数：上传面板目标形状（超椭圆边框 + 上传箭头 + 底部横线）
function superellipsePoint(theta, a, b, n) {
  const c = Math.cos(theta)
  const s = Math.sin(theta)
  const p = 2 / n
  return [
    a * Math.sign(c) * Math.pow(Math.abs(c), p),
    b * Math.sign(s) * Math.pow(Math.abs(s), p)
  ]
}

export function samplePanelTargets(count) {
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
        // 向上箭头的两侧翼：从顶点 (0, 0.56) 向 (±0.22, 0.34)
        const t = Math.random()
        const side = Math.random() < 0.5 ? -1 : 1
        x = side * t * 0.22
        y = 0.56 - t * 0.22
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
