import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'
import agentFeedback from '@agent-feedback/vite-plugin'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

/**
 * 每周一山专属：Android APK 产物在线下载与 App 内测更新检查中间件插件
 * (业务定制专属，与通用的 @agent-feedback/vite-plugin 彻底解耦)
 */
function viteApkReleasePlugin() {
  function setCorsHeaders(req, res) {
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Range, Authorization')
    res.setHeader('Access-Control-Expose-Headers', 'Content-Length, Content-Range, Content-Disposition, Accept-Ranges')
  }

  return {
    name: 'vite-plugin-alpine-apk-release',
    configureServer(server) {
      // 1. APK 静态安装包流式下载与断点续传服务 (GET /releases/*)
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
        const range = req.headers.range
        if (range) {
          const parts = range.replace(/bytes=/, '').split('-')
          const start = parseInt(parts[0], 10)
          const end = parts[1] ? parseInt(parts[1], 10) : stat.size - 1
          const chunksize = (end - start) + 1
          res.writeHead(206, {
            'Content-Range': `bytes ${start}-${end}/${stat.size}`,
            'Accept-Ranges': 'bytes',
            'Content-Length': chunksize,
            'Content-Type': 'application/vnd.android.package-archive',
            'Content-Disposition': `attachment; filename="${filename}"`,
            'Cache-Control': 'no-cache'
          })
          fs.createReadStream(filePath, { start, end }).pipe(res)
        } else {
          res.writeHead(200, {
            'Content-Type': 'application/vnd.android.package-archive',
            'Content-Disposition': `attachment; filename="${filename}"`,
            'Content-Length': stat.size,
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'no-cache'
          })
          fs.createReadStream(filePath).pipe(res)
        }
      })

      // 2. App 内测检查在线更新接口 (GET /api/app-update)
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

        let appVersion = '0.0.1.202610281359'
        let buildCode = 1793165500
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
              '接入独立通用 @agent-feedback 开源服务',
              '新增日级工单时间轴流式展示与真机联调扩展面板'
            ]
          })
        )
      })

      // 3. 向后兼容：对旧版移动端 App (/api/feedback) 提供 100% 契约保真的响应
      server.middlewares.use((req, res, next) => {
        const rawUrl = req.url || ''
        const urlPath = rawUrl.split('?')[0]

        if (!urlPath.startsWith('/api/feedback')) {
          return next()
        }

        setCorsHeaders(req, res)
        if (req.method === 'OPTIONS') {
          res.writeHead(204)
          res.end()
          return
        }

        const feedbackDir = path.resolve(__dirname, 'scratch/feedback')
        const indexFile = path.join(feedbackDir, 'feedback_index.json')

        // 3.1 兼容静态截图访问：GET /api/feedback/screenshot/<filename>
        if (req.method === 'GET' && urlPath.startsWith('/api/feedback/screenshot/')) {
          const filename = path.basename(urlPath)
          const searchPaths = [
            path.join(feedbackDir, 'screenshots', filename),
            path.join(__dirname, 'scratch', filename),
            path.join(feedbackDir, filename)
          ]
          for (const sp of searchPaths) {
            if (fs.existsSync(sp)) {
              const ext = path.extname(sp).toLowerCase()
              const mime = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : 'image/jpeg'
              res.writeHead(200, {
                'Content-Type': mime,
                'Cache-Control': 'public, max-age=86400'
              })
              fs.createReadStream(sp).pipe(res)
              return
            }
          }
          res.writeHead(404)
          res.end('Screenshot not found')
          return
        }

        // 3.2 兼容 GET /api/feedback (带或不带 ?date=)
        if (req.method === 'GET') {
          let index = { dates: [], totalCount: 0 }
          if (fs.existsSync(indexFile)) {
            try {
              index = JSON.parse(fs.readFileSync(indexFile, 'utf-8'))
            } catch {}
          }

          const parsedUrl = new URL(rawUrl, 'http://localhost')
          const reqDate = parsedUrl.searchParams.get('date')
          const targetDate = reqDate || (index.dates && index.dates[0]) || new Date().toISOString().slice(0, 10)
          const shardFile = path.join(feedbackDir, `feedback_${targetDate}.json`)

          let items = []
          if (fs.existsSync(shardFile)) {
            try {
              items = JSON.parse(fs.readFileSync(shardFile, 'utf-8'))
            } catch {}
          }

          // 3.2.1 兼容旧版客户端对 screenshots 对象的严格要求 (包含 filename, path 字段)
          const normalizedItems = items.map(raw => {
            const item = { ...raw }
            if (Array.isArray(item.screenshots) && item.screenshots.length > 0) {
              item.screenshots = item.screenshots.map(s => {
                if (typeof s === 'string') {
                  const fname = path.basename(s)
                  const ext = path.extname(fname).replace('.', '') || 'jpg'
                  return {
                    filename: fname,
                    path: s,
                    ext: ext,
                    sizeKb: 50
                  }
                }
                return s
              })
              if (!item.screenshotFilename && item.screenshots[0]) {
                item.screenshotFilename = item.screenshots[0].filename
              }
            } else if (item.screenshot && typeof item.screenshot === 'string' && !item.screenshot.startsWith('data:')) {
              const fname = path.basename(item.screenshot)
              item.screenshotFilename = fname
              item.screenshots = [{
                filename: fname,
                path: item.screenshot,
                ext: path.extname(fname).replace('.', '') || 'jpg',
                sizeKb: 50
              }]
            }
            return item
          })

          const dateIdx = (index.dates || []).indexOf(targetDate)
          const hasMore = dateIdx !== -1 && dateIdx < (index.dates || []).length - 1
          const nextDate = hasMore ? index.dates[dateIdx + 1] : null

          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' })
          res.end(
            JSON.stringify({
              success: true,
              totalCount: index.totalCount || items.length,
              dates: index.dates || [targetDate],
              currentDate: targetDate,
              date: targetDate,
              dailyCount: items.length,
              items: normalizedItems,
              history: normalizedItems,
              hasMore: hasMore,
              nextDate: nextDate
            })
          )
          return
        }

        // 3.3 提交工单或更新状态重写给新插件
        if (urlPath === '/api/feedback/status' || urlPath.startsWith('/api/feedback/status?')) {
          req.url = rawUrl.replace('/api/feedback/status', '/api/__agent_feedback/status')
        } else if (req.method === 'POST') {
          req.url = '/api/__agent_feedback/submit'
        }
        next()
      })
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    // 接入每周一山业务专属 APK 更新服务 (前置兼容改写)
    viteApkReleasePlugin(),
    // 接入通用 @agent-feedback/vite-plugin 插件
    agentFeedback({
      storageDir: 'scratch/feedback',
      theme: 'dark',
      primaryColor: '#4edea3'
    })
  ],
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
