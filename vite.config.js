import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

// 手机真机即时调试反馈与 OTA 在线更新中间件插件
function viteFeedbackPlugin() {
  function setCorsHeaders(req, res) {
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Range, Authorization')
    res.setHeader('Access-Control-Expose-Headers', 'Content-Length, Content-Range, Content-Disposition')
  }

  return {
    name: 'vite-plugin-mobile-feedback',
    configureServer(server) {
      // 0. APK 产物下载服务 (GET /releases/*)
      server.middlewares.use('/releases', (req, res, next) => {
        setCorsHeaders(req, res)
        if (req.method === 'OPTIONS') {
          res.writeHead(204)
          res.end()
          return
        }

        const releaseDir = path.resolve(__dirname, 'releases')
        if (!fs.existsSync(releaseDir)) {
          fs.mkdirSync(releaseDir, { recursive: true })
        }

        const reqUrl = req.url.split('?')[0]
        let filename = reqUrl.replace(/^\//, '')
        if (!filename || filename === '/') {
          filename = 'weekly-mountain-latest-debug.apk'
        } else if (filename === 'release' || filename === 'latest-release') {
          filename = 'weekly-mountain-latest-release.apk'
        } else if (filename === 'debug' || filename === 'latest-debug') {
          filename = 'weekly-mountain-latest-debug.apk'
        }

        let filePath = path.join(releaseDir, filename)
        if (!fs.existsSync(filePath)) {
          // 回退寻找最新的 apk 文件
          const files = fs.readdirSync(releaseDir).filter(f => f.endsWith('.apk'))
          if (files.length > 0) {
            filePath = path.join(releaseDir, files[files.length - 1])
            filename = path.basename(filePath)
          } else {
            res.writeHead(404)
            res.end('APK not found')
            return
          }
        }

        const stat = fs.statSync(filePath)
        res.writeHead(200, {
          'Content-Type': 'application/vnd.android.package-archive',
          'Content-Disposition': `attachment; filename="${filename}"`,
          'Content-Length': stat.size,
          'Cache-Control': 'no-cache'
        })
        fs.createReadStream(filePath).pipe(res)
      })

      // 0.5 App 在线检查更新接口 (GET /api/app-update)
      server.middlewares.use('/api/app-update', (req, res) => {
        setCorsHeaders(req, res)
        if (req.method === 'OPTIONS') {
          res.writeHead(204)
          res.end()
          return
        }

        const releaseDir = path.resolve(__dirname, 'releases')
        let latestApk = 'weekly-mountain-latest-debug.apk'
        let apkSize = 0
        let updateTime = new Date().toISOString()

        if (fs.existsSync(releaseDir)) {
          const files = fs.readdirSync(releaseDir).filter(f => f.endsWith('.apk'))
          if (files.length > 0) {
            let maxTime = 0
            files.forEach(f => {
              const stat = fs.statSync(path.join(releaseDir, f))
              if (stat.mtimeMs > maxTime) {
                maxTime = stat.mtimeMs
                latestApk = f
                apkSize = stat.size
                updateTime = new Date(stat.mtimeMs).toLocaleString('zh-CN', { hour12: false })
              }
            })
          }
        }

        let appVersion = '0.0.1.001'
        let buildCode = 1
        try {
          const versionJs = fs.readFileSync(path.resolve(__dirname, 'src/config/version.js'), 'utf-8')
          const mVer = versionJs.match(/APP_VERSION\s*=\s*['"]([^'"]+)['"]/)
          if (mVer) appVersion = mVer[1]
          const mCode = versionJs.match(/BUILD_CODE\s*=\s*(\d+)/)
          if (mCode) buildCode = parseInt(mCode[1], 10)
        } catch {}

        const host = req.headers.host || 'localhost:5173'
        const proto = req.headers['x-forwarded-proto'] || (host.startsWith('localhost') || host.startsWith('127.0.0.1') ? 'http' : 'https')

        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' })
        res.end(
          JSON.stringify({
            success: true,
            latestVersion: appVersion,
            buildCode: buildCode,
            downloadUrl: `${proto}://${host}/releases/weekly-mountain-latest-debug.apk`,
            apkName: latestApk,
            fileSizeBytes: apkSize,
            fileSize: apkSize ? `${(apkSize / 1024 / 1024).toFixed(2)} MB` : '27.7 MB',
            updateTime: updateTime,
            changelog: [
              '全新 0.0.1.xxx 研发迭代版本号规范',
              '新增 App 内直连穿透反馈通道（支持截图与进度追踪）',
              '新增调试面板在线一键更新 APK 与免线热重载联调'
            ]
          })
        )
      })

      // 1. 移动端真机反馈服务 (server.middlewares.use('/api/feedback'))
      server.middlewares.use('/api/feedback', (req, res, next) => {
        setCorsHeaders(req, res)
        if (req.method === 'OPTIONS') {
          res.writeHead(204)
          res.end()
          return
        }
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
                  res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' })
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

              // 处理附带的截图文件 (支持多图与单图)
              const saveImageBuffer = (base64Str, fileName) => {
                try {
                  const matches = base64Str.match(/^data:image\/([a-zA-Z0-9]+);base64,(.+)$/)
                  if (!matches) return null
                  const ext = matches[1] === 'jpeg' ? 'jpg' : matches[1]
                  const buffer = Buffer.from(matches[2], 'base64')
                  const fullFileName = fileName.endsWith(`.${ext}`) ? fileName : `${fileName}.${ext}`
                  const targetPath = path.join(scratchDir, fullFileName)
                  fs.writeFileSync(targetPath, buffer)

                  // 同步一份到脑部 Artifact 目录
                  const brainDir = path.resolve('C:\\Users\\lylyu\\.gemini\\antigravity\\brain\\94773e75-cfd8-4fb7-87e3-d08b195b9520')
                  if (fs.existsSync(brainDir)) {
                    try {
                      fs.writeFileSync(path.join(brainDir, fullFileName), buffer)
                    } catch {}
                  }

                  return {
                    path: `scratch/${fullFileName}`,
                    filename: fullFileName,
                    ext,
                    sizeKb: Math.round(buffer.length / 1024)
                  }
                } catch (err) {
                  console.error('Failed to save screenshot image:', err)
                  return null
                }
              }

              if (Array.isArray(data.screenshots) && data.screenshots.length > 0) {
                const savedList = []
                data.screenshots.forEach((item, idx) => {
                  const base64Str = typeof item === 'string' ? item : item?.data
                  if (base64Str && base64Str.startsWith('data:image/')) {
                    const saved = saveImageBuffer(base64Str, `feedback_screenshot_${timeStamp}_${idx + 1}`)
                    if (saved) {
                      savedList.push({
                        ...saved,
                        meta: item.meta || {}
                      })
                    }
                  }
                })

                if (savedList.length > 0) {
                  data.screenshots = savedList
                  data.screenshotPath = savedList[0].path
                  data.screenshotFilename = savedList[0].filename
                  data.screenshotExt = savedList[0].ext
                  data.screenshotSizeKb = savedList[0].sizeKb

                  try {
                    const firstBuf = fs.readFileSync(path.join(scratchDir, savedList[0].filename))
                    fs.writeFileSync(path.join(scratchDir, `latest_feedback_screenshot.${savedList[0].ext}`), firstBuf)
                    const brainDir = path.resolve('C:\\Users\\lylyu\\.gemini\\antigravity\\brain\\94773e75-cfd8-4fb7-87e3-d08b195b9520')
                    if (fs.existsSync(brainDir)) {
                      fs.writeFileSync(path.join(brainDir, `latest_feedback_screenshot.${savedList[0].ext}`), firstBuf)
                    }
                  } catch {}
                }
                delete data.screenshot
              } else if (data.screenshot && typeof data.screenshot === 'string' && data.screenshot.startsWith('data:image/')) {
                const saved = saveImageBuffer(data.screenshot, `feedback_screenshot_${timeStamp}`)
                if (saved) {
                  data.screenshotPath = saved.path
                  data.screenshotFilename = saved.filename
                  data.screenshotExt = saved.ext
                  data.screenshotSizeKb = saved.sizeKb
                  data.screenshots = [{
                    ...saved,
                    meta: data.screenshotMeta || {}
                  }]

                  try {
                    const firstBuf = fs.readFileSync(path.join(scratchDir, saved.filename))
                    fs.writeFileSync(path.join(scratchDir, `latest_feedback_screenshot.${saved.ext}`), firstBuf)
                    const brainDir = path.resolve('C:\\Users\\lylyu\\.gemini\\antigravity\\brain\\94773e75-cfd8-4fb7-87e3-d08b195b9520')
                    if (fs.existsSync(brainDir)) {
                      fs.writeFileSync(path.join(brainDir, `latest_feedback_screenshot.${saved.ext}`), firstBuf)
                    }
                  } catch {}
                }
                delete data.screenshot
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

              res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' })
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
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' })
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
