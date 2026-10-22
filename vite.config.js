import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

// 手机真机即时调试反馈中间件插件
function viteFeedbackPlugin() {
  return {
    name: 'vite-plugin-mobile-feedback',
    configureServer(server) {
      server.middlewares.use('/api/feedback', (req, res, next) => {
        const scratchDir = path.resolve(__dirname, 'scratch')
        if (!fs.existsSync(scratchDir)) {
          fs.mkdirSync(scratchDir, { recursive: true })
        }
        const feedbackFile = path.join(scratchDir, 'mobile_feedback.json')
        const latestFile = path.join(scratchDir, 'latest_feedback.json')

        // 1. 静态截图文件下发 (支持移动端穿透直接加载缩略图)
        if (req.method === 'GET' && req.url.startsWith('/screenshot/')) {
          const filename = req.url.replace('/screenshot/', '').split('?')[0]
          if (!/^[a-zA-Z0-9_.-]+$/.test(filename)) {
            res.writeHead(400)
            res.end('Invalid filename')
            return
          }
          const filePath = path.join(scratchDir, filename)
          if (fs.existsSync(filePath)) {
            const ext = path.extname(filePath).toLowerCase()
            const mime = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : 'image/jpeg'
            res.writeHead(200, {
              'Content-Type': mime,
              'Cache-Control': 'public, max-age=86400'
            })
            fs.createReadStream(filePath).pipe(res)
            return
          } else {
            res.writeHead(404)
            res.end('Screenshot not found')
            return
          }
        }

        // 2. 更新单条反馈的处理进度与答复说明 (POST /api/feedback/status)
        if (req.method === 'POST' && req.url === '/status') {
          let body = ''
          req.on('data', chunk => {
            body += chunk
          })
          req.on('end', () => {
            try {
              const { id, status, reply } = JSON.parse(body || '{}')
              if (fs.existsSync(feedbackFile)) {
                const history = JSON.parse(fs.readFileSync(feedbackFile, 'utf-8'))
                const item = history.find(h => h.id == id || h.timestamp == id)
                if (item) {
                  if (status) item.status = status
                  if (reply) item.reply = reply
                  item.updatedAt = new Date().toISOString()
                  fs.writeFileSync(feedbackFile, JSON.stringify(history, null, 2), 'utf-8')
                  if (fs.existsSync(latestFile)) {
                    try {
                      const latest = JSON.parse(fs.readFileSync(latestFile, 'utf-8'))
                      if (latest.id == id || latest.timestamp == id) {
                        if (status) latest.status = status
                        if (reply) latest.reply = reply
                        latest.updatedAt = item.updatedAt
                        fs.writeFileSync(latestFile, JSON.stringify(latest, null, 2), 'utf-8')
                      }
                    } catch {}
                  }
                  res.writeHead(200, { 'Content-Type': 'application/json' })
                  res.end(JSON.stringify({ success: true, item }))
                  return
                }
              }
              res.writeHead(404, { 'Content-Type': 'application/json' })
              res.end(JSON.stringify({ success: false, error: 'Feedback not found' }))
            } catch (err) {
              res.writeHead(500, { 'Content-Type': 'application/json' })
              res.end(JSON.stringify({ success: false, error: err.message }))
            }
          })
          return
        }

        // 3. 提交新反馈 (POST /api/feedback)
        if (req.method === 'POST') {
          let body = ''
          req.on('data', chunk => {
            body += chunk
          })
          req.on('end', () => {
            try {
              const data = JSON.parse(body || '{}')
              const timeStamp = data.timestamp || Date.now()
              data.id = timeStamp
              data.receivedAt = new Date().toISOString()
              data.updatedAt = data.receivedAt
              data.status = 'pending' // 状态: pending (排队待处理) | processing (处理中) | completed (已解决)
              data.remoteInstruction = '【远程无人值守守则 (详见 AGENTS.md / GEMINI.md)】用户在手机端离线操作，严禁在 IDE 中挂起等待提问；遇细节分歧按安全默认值推进；验证完成后将答复写回 reply 字段并重启哨兵。'
              data.reply = '已送达本地 AI 哨兵，正在排队等待分析修复中...'
              data.clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress

              // 处理附带的截图文件
              if (data.screenshot && typeof data.screenshot === 'string' && data.screenshot.startsWith('data:image/')) {
                try {
                  const matches = data.screenshot.match(/^data:image\/([a-zA-Z0-9]+);base64,(.+)$/)
                  if (matches) {
                    const ext = matches[1] === 'jpeg' ? 'jpg' : matches[1]
                    const buffer = Buffer.from(matches[2], 'base64')
                    const fileName = `feedback_screenshot_${timeStamp}.${ext}`
                    const targetPath = path.join(scratchDir, fileName)
                    fs.writeFileSync(targetPath, buffer)

                    // 保存一份 latest 副本便于快速访问
                    const latestPath = path.join(scratchDir, `latest_feedback_screenshot.${ext}`)
                    fs.writeFileSync(latestPath, buffer)

                    // 同步一份到脑部 Artifact 目录
                    const brainDir = path.resolve('C:\\Users\\lylyu\\.gemini\\antigravity\\brain\\94773e75-cfd8-4fb7-87e3-d08b195b9520')
                    if (fs.existsSync(brainDir)) {
                      try {
                        fs.writeFileSync(path.join(brainDir, fileName), buffer)
                        fs.writeFileSync(path.join(brainDir, `latest_feedback_screenshot.${ext}`), buffer)
                      } catch {}
                    }

                    data.screenshotPath = `scratch/${fileName}`
                    data.screenshotFilename = fileName
                    data.screenshotExt = ext
                    data.screenshotSizeKb = Math.round(buffer.length / 1024)
                    // 移除超长 base64 避免 json 膨胀
                    delete data.screenshot
                  }
                } catch (imgErr) {
                  console.error('Failed to save screenshot image:', imgErr)
                }
              }

              let history = []
              if (fs.existsSync(feedbackFile)) {
                try {
                  const content = fs.readFileSync(feedbackFile, 'utf-8')
                  history = JSON.parse(content)
                  if (!Array.isArray(history)) history = [history]
                } catch {
                  history = []
                }
              }
              history.unshift(data)
              if (history.length > 50) history = history.slice(0, 50)

              fs.writeFileSync(feedbackFile, JSON.stringify(history, null, 2), 'utf-8')
              fs.writeFileSync(
                path.join(scratchDir, 'latest_feedback.json'),
                JSON.stringify(data, null, 2),
                'utf-8'
              )

              console.log(`\n========================================`)
              console.log(`📱 [收到手机真机调试反馈] ${data.receivedAt}`)
              console.log(`   反馈编号: #${data.id}`)
              console.log(`   机型视口: ${data.device?.viewport} (DPR: ${data.device?.dpr})`)
              console.log(`   所在页面: ${data.state?.route} (选中山峰: ${data.state?.mountain || '无'})`)
              console.log(`   反馈内容: "${data.content}"`)
              if (data.screenshotPath) {
                console.log(`   附带截图: ${data.screenshotPath} (${data.screenshotSizeKb} KB)`)
              }
              console.log(`========================================\n`)

              res.writeHead(200, { 'Content-Type': 'application/json' })
              res.end(JSON.stringify({ success: true, count: history.length, item: data, receivedAt: data.receivedAt }))
            } catch (err) {
              res.writeHead(500, { 'Content-Type': 'application/json' })
              res.end(JSON.stringify({ success: false, error: err.message }))
            }
          })
        } else if (req.method === 'GET') {
          // 4. 获取反馈历史列表与进度 (GET /api/feedback)
          let history = []
          if (fs.existsSync(feedbackFile)) {
            try {
              history = JSON.parse(fs.readFileSync(feedbackFile, 'utf-8'))
            } catch {
              history = []
            }
          }
          res.writeHead(200, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ success: true, history }))
        } else {
          next()
        }
      })
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  base: './',
  plugins: [vue(), viteFeedbackPlugin()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: true,
    allowedHosts: true
  },
  preview: {
    host: true,
    allowedHosts: true
  }
})
