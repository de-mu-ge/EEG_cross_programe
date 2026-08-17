// 临时验证脚本：驱动本机 Edge 截图首页各状态（验证后可删除）
import puppeteer from 'puppeteer-core'

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
const URL = 'http://localhost:4173/'
const OUT = process.env.TEMP || '/tmp'

const browser = await puppeteer.launch({
  executablePath: EDGE,
  headless: 'shell',
  args: ['--window-size=1600,900', '--use-angle=default']
})
const page = await browser.newPage()
await page.setViewport({ width: 1600, height: 900 })
page.on('console', (m) => console.log('[console]', m.type(), m.text()))
page.on('pageerror', (e) => console.log('[pageerror]', e.message))

await page.goto(URL, { waitUntil: 'networkidle0' })
await new Promise((r) => setTimeout(r, 4000)) // 入场动画完成
await page.screenshot({ path: `${OUT}/v1_idle.png` })

// 鼠标光源：移到头部右侧
await page.mouse.move(1000, 380, { steps: 20 })
await new Promise((r) => setTimeout(r, 800))
await page.screenshot({ path: `${OUT}/v2_light.png` })

// 点击 START ANALYSIS，捕捉转场各阶段
await page.mouse.move(800, 756)
await new Promise((r) => setTimeout(r, 300))
await page.click('.start-btn')
await new Promise((r) => setTimeout(r, 1200)) // awaken 中段
await page.screenshot({ path: `${OUT}/v3_awaken.png` })
await new Promise((r) => setTimeout(r, 1800)) // dissolve/stream
await page.screenshot({ path: `${OUT}/v4_stream.png` })
await new Promise((r) => setTimeout(r, 1800)) // morph
await page.screenshot({ path: `${OUT}/v5_morph.png` })
await new Promise((r) => setTimeout(r, 2500)) // panel + 上传区
await page.screenshot({ path: `${OUT}/v6_panel.png` })

await browser.close()
console.log('done')
