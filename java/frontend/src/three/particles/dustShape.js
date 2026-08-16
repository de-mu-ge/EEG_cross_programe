// 纯函数：黑暗空间中的环境尘埃（微弱粒子/隐藏数据流）
// 分布在一个远大于头部的空间里，正面观察时营造纵深
export const DUST_BOUNDS = { x: 4.4, y: 2.5, zMin: -3.4, zMax: 0.9 }

export function sampleDustPoints(count) {
  const points = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    points[i * 3] = (Math.random() * 2 - 1) * DUST_BOUNDS.x
    points[i * 3 + 1] = (Math.random() * 2 - 1) * DUST_BOUNDS.y
    points[i * 3 + 2] = DUST_BOUNDS.zMin + Math.random() * (DUST_BOUNDS.zMax - DUST_BOUNDS.zMin)
  }
  return points
}
