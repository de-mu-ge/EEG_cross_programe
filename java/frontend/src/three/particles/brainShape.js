// 纯函数：体素网格填充椭球大脑，留出左右半球中缝
export function sampleBrainVoxels() {
  const spacing = 0.085
  const rx = 0.78, ry = 0.58, rz = 0.66
  const cy = 0.22
  const points = []
  for (let x = -rx; x <= rx; x += spacing) {
    for (let y = -ry; y <= ry; y += spacing) {
      for (let z = -rz; z <= rz; z += spacing) {
        const n = (x * x) / (rx * rx) + (y * y) / (ry * ry) + (z * z) / (rz * rz)
        if (n > 1) continue
        if (Math.abs(x) < 0.05) continue
        if (y < -0.36) continue
        points.push(
          x + (Math.random() - 0.5) * 0.03,
          cy + y + (Math.random() - 0.5) * 0.03,
          z + (Math.random() - 0.5) * 0.03
        )
      }
    }
  }
  return Float32Array.from(points)
}
