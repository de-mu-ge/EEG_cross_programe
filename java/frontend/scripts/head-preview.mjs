// 开发工具：ASCII 预览 sampleHeadPoints 的正面/侧面轮廓
// 用法: node scripts/head-preview.mjs
import { sampleHeadPoints } from '../src/three/particles/headShape.js'

const pts = sampleHeadPoints(6000)
const n = pts.length / 3

function plot(title, getU, getV, W = 72, H = 34) {
  let uMin = Infinity, uMax = -Infinity, vMin = Infinity, vMax = -Infinity
  for (let i = 0; i < n; i++) {
    const u = getU(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2])
    const v = getV(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2])
    if (u < uMin) uMin = u
    if (u > uMax) uMax = u
    if (v < vMin) vMin = v
    if (v > vMax) vMax = v
  }
  const grid = Array.from({ length: H }, () => new Array(W).fill(0))
  for (let i = 0; i < n; i++) {
    const u = getU(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2])
    const v = getV(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2])
    const cx = Math.min(W - 1, Math.floor(((u - uMin) / (uMax - uMin)) * W))
    const cy = Math.min(H - 1, Math.floor(((v - vMin) / (vMax - vMin)) * H))
    grid[cy][cx]++
  }
  const shades = [' ', '·', ':', '+', '#']
  console.log(`\n=== ${title} ===  (u: ${uMin.toFixed(2)}..${uMax.toFixed(2)}, v: ${vMin.toFixed(2)}..${vMax.toFixed(2)})`)
  for (let row = H - 1; row >= 0; row--) {
    console.log(grid[row].map((c) => shades[Math.min(4, c)]).join(''))
  }
}

// 正面：x 横轴, y 纵轴（面向 +z 观察）
plot('FRONT  (x →, y ↑)', (x) => x, (_, y) => y)
// 侧面：z 横轴（左=后脑，右=脸）, y 纵轴
plot('SIDE   (z →, y ↑)  face →', (_, __, z) => z, (_, y) => y)
// 面部特写：仅前侧点
const frontOnly = []
for (let i = 0; i < n; i++) {
  if (pts[i * 3 + 2] > 0.45) frontOnly.push(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2])
}
console.log(`\nfront-facing points (z>0.45): ${frontOnly.length / 3} / ${n}`)
