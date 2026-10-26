<#
.SYNOPSIS
    《每周一山》移动端 App 自动化打包流水线 (PowerShell / pwsh)
.DESCRIPTION
    执行流程：
    1. 环境智能感知与自动对齐 (JDK 17 LTS + Android SDK)
    2. Vite 5 + Vue 3 前端工程生产构建与资源同步
    3. Capacitor 8 Android 原生容器同步
    4. Gradle 编译生成 Android Debug/Release APK
    5. 产物校验、体积量化与 release 目录自动归档 (包括 latest-debug.apk)
#>

param(
    [switch]$Pause,
    [switch]$NoPause,
    [switch]$Clean,
    [string]$Variant = "debug"
)

# 确保 UTF-8 控制台字符集
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Host.UI.RawUI.WindowTitle = "每周一山 - 移动端 App 打包流水线"

function Write-Step([string]$title) {
    Write-Host "`n==============================================================================" -ForegroundColor DarkCyan
    Write-Host " [步骤] $title" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor DarkCyan
}

function Write-Success([string]$msg) {
    Write-Host " [成功] $msg" -ForegroundColor Green
}

function Write-Info([string]$msg) {
    Write-Host " [信息] $msg" -ForegroundColor Gray
}

function Write-Warning([string]$msg) {
    Write-Host " [警告] $msg" -ForegroundColor Yellow
}

function Write-ErrorMsg([string]$msg) {
    Write-Host " [错误] $msg" -ForegroundColor Red
}

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

Write-Host "==============================================================================" -ForegroundColor DarkGreen
Write-Host " 《每周一山 · 成都周边50座山》移动端 App 自动化打包流水线" -ForegroundColor Green
Write-Host " 运行环境: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion) (引擎: $($Host.Name))" -ForegroundColor DarkGray
Write-Host " 工作目录: $ProjectRoot" -ForegroundColor DarkGray
Write-Host "==============================================================================" -ForegroundColor DarkGreen

# -----------------------------------------------------------------------------
# 0. 环境变量自适应检测与补齐
# -----------------------------------------------------------------------------
Write-Step "0/4 检查并适配 JDK 17 与 Android SDK 编译环境"

# 检测与补齐 JAVA_HOME
$ValidJavaHome = $false
if ($env:JAVA_HOME -and (Test-Path "$env:JAVA_HOME\bin\javac.exe")) {
    $ValidJavaHome = $true
} else {
    $Candidates = @(
        "D:\soft\JDKS\jdk-17.0.16\jdk",
        "D:\soft\JDKS\jdk-17.0.16",
        "C:\Program Files\Java\jdk-17*",
        "D:\soft\Java\jdk-17*"
    )
    foreach ($cand in $Candidates) {
        $matched = Get-Item $cand -ErrorAction SilentlyContinue | Where-Object { Test-Path "$($_.FullName)\bin\javac.exe" } | Select-Object -First 1
        if ($matched) {
            $env:JAVA_HOME = $matched.FullName
            $ValidJavaHome = $true
            break
        }
    }
}

if (-not $ValidJavaHome) {
    Write-ErrorMsg "未找到有效的 JDK 17 安装目录！请检查 JAVA_HOME 配置。"
    if ($Pause) { pause }
    exit 1
}

$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
Write-Success "JAVA_HOME: $env:JAVA_HOME"

# 检测与补齐 ANDROID_HOME
$ValidAndroidHome = $false
if ($env:ANDROID_HOME -and (Test-Path "$env:ANDROID_HOME\platform-tools")) {
    $ValidAndroidHome = $true
} else {
    $AndroidCandidates = @(
        "D:\soft\android-sdk",
        "$env:LOCALAPPDATA\Android\Sdk",
        "$env:PROGRAMFILES\Android\Android Studio\sdk"
    )
    foreach ($cand in $AndroidCandidates) {
        if (Test-Path $cand) {
            $env:ANDROID_HOME = $cand
            $ValidAndroidHome = $true
            break
        }
    }
}

if (-not $ValidAndroidHome) {
    Write-ErrorMsg "未找到有效的 Android SDK 目录！请检查 ANDROID_HOME 配置。"
    if ($Pause) { pause }
    exit 1
}

$env:PATH = "$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:PATH"
Write-Success "ANDROID_HOME: $env:ANDROID_HOME"

# -----------------------------------------------------------------------------
# 1. 前端工程生产构建
# -----------------------------------------------------------------------------
$BuildCmd = if ($Variant -eq "release") { "build:release" } else { "build" }
Write-Step "1/4 运行 Vite 前端生产构建 (npm run $BuildCmd - 变体: $Variant)"

Write-Info "正在执行 npm run $BuildCmd 构建 dist/ 生产静态产物..."
& npm run $BuildCmd
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "npm run $BuildCmd 失败，退出码: $LASTEXITCODE"
    if ($Pause) { pause }
    exit $LASTEXITCODE
}
Write-Success "前端生产构建完成，dist/ 产物就绪！"

# -----------------------------------------------------------------------------
# 2. 同步 Web 资源至 Capacitor Android 容器
# -----------------------------------------------------------------------------
Write-Step "2/4 同步资源至 Capacitor Android 原生工程 (npx cap sync android)"

Write-Info "正在将 dist 资源与原生插件同步至 android/ 容器..."
& npx cap sync android
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "npx cap sync android 失败，退出码: $LASTEXITCODE"
    if ($Pause) { pause }
    exit $LASTEXITCODE
}
Write-Success "Capacitor Android 容器资源同步完成！"

# -----------------------------------------------------------------------------
# 3. 运行 Gradle APK 编译
# -----------------------------------------------------------------------------
Write-Step "3/4 执行 Gradle APK 编译构建 (gradlew assembleDebug)"

$AndroidDir = Join-Path $ProjectRoot "android"
if (-not (Test-Path $AndroidDir)) {
    Write-ErrorMsg "未找到 android 工程目录，请先执行 npx cap add android！"
    if ($Pause) { pause }
    exit 1
}

Push-Location $AndroidDir
try {
    Write-Info "正在启动 Gradle Daemon 进行 Native APK 打包..."
    & .\gradlew.bat assembleDebug
    $GradleStatus = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($GradleStatus -ne 0) {
    Write-ErrorMsg "Gradle 编译 APK 失败，退出码: $GradleStatus"
    if ($Pause) { pause }
    exit $GradleStatus
}
Write-Success "Gradle assembleDebug 编译完成！"

# -----------------------------------------------------------------------------
# 4. 产物校验与 releases 目录归档
# -----------------------------------------------------------------------------
Write-Step "4/4 校验并归档 APK 产物至 releases 目录"

$ApkSource = Join-Path $ProjectRoot "android\app\build\outputs\apk\debug\app-debug.apk"
$ReleaseDir = Join-Path $ProjectRoot "releases"

if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
}

if (Test-Path $ApkSource) {
    $PkgJson = Get-Content (Join-Path $ProjectRoot "package.json") -Raw | ConvertFrom-Json
    $Version = if ($PkgJson.version) { $PkgJson.version } else { "0.0.1.002" }

    $TargetName = "weekly-mountain-v$Version-$Variant.apk"
    $TargetPath = Join-Path $ReleaseDir $TargetName

    Copy-Item -Path $ApkSource -Destination $TargetPath -Force

    # 根据构建变体输出对应的 latest 软链/别名镜像
    if ($Variant -eq "release") {
        $LatestPath = Join-Path $ReleaseDir "weekly-mountain-latest-release.apk"
        Copy-Item -Path $ApkSource -Destination $LatestPath -Force
        Write-Info "已同步生成 release 最新镜像: weekly-mountain-latest-release.apk"
    } else {
        $LatestPath = Join-Path $ReleaseDir "weekly-mountain-latest-debug.apk"
        Copy-Item -Path $ApkSource -Destination $LatestPath -Force
        Write-Info "已同步生成 debug 最新镜像: weekly-mountain-latest-debug.apk"
    }

    $ApkItem = Get-Item $TargetPath
    $SizeMB = [math]::Round($ApkItem.Length / 1MB, 2)

    Write-Host "`n==============================================================================" -ForegroundColor DarkGreen
    Write-Host " [成功] 移动端 APK ($Variant 变体) 打包与归档全部完成！" -ForegroundColor Green
    Write-Host "==============================================================================" -ForegroundColor DarkGreen
    Write-Host " 产物文件: $TargetName" -ForegroundColor Cyan
    Write-Host " 最新镜像: $(Split-Path $LatestPath -Leaf) (供在线分发与安装)" -ForegroundColor Cyan
    Write-Host " 物理路径: $TargetPath" -ForegroundColor White
    Write-Host " 文件大小: $SizeMB MB ($($ApkItem.Length) 字节)" -ForegroundColor Yellow
    Write-Host " 构建时间: $($ApkItem.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
    Write-Host " 支持系统: Android 7.0+ (API 24+)" -ForegroundColor DarkGray
    Write-Host "==============================================================================" -ForegroundColor DarkGreen
} else {
    Write-ErrorMsg "未检测到 Gradle 生成的 app-debug.apk 产物文件！"
    if ($Pause) { pause }
    exit 1
}

if ($Pause) {
    Write-Host "`n按回车键退出..." -ForegroundColor DarkGray
    [void][System.Console]::ReadLine()
}

exit 0
