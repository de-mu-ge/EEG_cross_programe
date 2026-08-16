// 纯函数：在变形球面上采样正面人头轮廓粒子（面部朝 +z）
// 不依赖 three.js，方便用 scripts/head-preview.mjs 做 ASCII 预览

function g(x, s) {
  return Math.exp(-(x * x) / (2 * s * s))
}

export function sampleHeadPoints(count) {
  const points = []
  const golden = Math.PI * (3 - Math.sqrt(5))
  for (let i = 0; i < count; i++) {
    const y0 = 1 - (i / (count - 1)) * 2
    const r0 = Math.sqrt(Math.max(0, 1 - y0 * y0))
    const theta = golden * i
    let x = Math.cos(theta) * r0
    let y = y0
    let z = Math.sin(theta) * r0

    // 基础比例：头高大于头宽
    x *= 0.92
    y *= 1.22
    z *= 0.98

    // 下颌/颈部收缩，下巴略前送
    if (y < -0.05) {
      const k = Math.min(1, (-y - 0.05) / 1.05)
      const s = 1 - 0.55 * k * k
      x *= s
      z *= s
      z += 0.05 * k
    }

    // 后脑勺延展
    if (z < -0.2) z *= 1.1

    // 面部区域压平，形成脸平面
    if (z > 0.6 && Math.abs(x) < 0.6 && y > -0.7 && y < 0.7) {
      z = 0.6 + (z - 0.6) * 0.5
    }

    // 面部特征（仅前侧）
    if (z > 0.35) {
      // 眉弓
      z += 0.04 * g(y - 0.26, 0.09) * g(x, 0.45)
      // 眼窝凹陷
      z -= 0.09 * g(x - 0.3, 0.13) * g(y - 0.1, 0.11)
      z -= 0.09 * g(x + 0.3, 0.13) * g(y - 0.1, 0.11)
      // 鼻梁 + 鼻尖
      z += 0.17 * g(x, 0.085) * g(y + 0.1, 0.2)
      z += 0.07 * g(x, 0.07) * g(y + 0.3, 0.08)
      // 口唇微凸
      z += 0.03 * g(x, 0.18) * g(y + 0.48, 0.05)
      // 下巴
      z += 0.06 * g(x, 0.2) * g(y + 0.72, 0.1)
    }

    // 颈部以下裁掉，头部悬浮
    if (y < -0.98) continue

    const j = 0.012
    points.push(
      x + (Math.random() - 0.5) * j,
      y + (Math.random() - 0.5) * j,
      z + (Math.random() - 0.5) * j
    )
  }
  return Float32Array.from(points)
}
