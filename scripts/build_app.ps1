<#
.SYNOPSIS
    《每周一山》移动端 App 自动化打包流水线 (PowerShell / pwsh)
.DESCRIPTION
    执行流程：
    0. 环境感知与前置地域离线包自动化构建 (build_region_packs.py)
    1. 检查并适配 JDK 17 与 Android SDK 编译环境
    2. 地域构建矩阵装配 (-RegionVariant standard|full)
    3. Vite 5 + Vue 3 前端工程生产构建与资源同步
    4. Capacitor 8 Android 原生容器同步
    5. Gradle 编译生成 Android Debug/Release APK
    6. 产物校验、体积量化与 release 目录自动归档 (包括 standard/full 矩阵变体)
#>

[CmdletBinding()]
param(
    [switch]$Pause,
    [switch]$NoPause,
    [switch]$Clean,
    [switch]$DryRun,
    [string]$Variant = "debug",
    [string]$RegionVariant = "standard"
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

# 参数归一化与校验
$Variant = $Variant.ToLowerInvariant()
$RegionVariant = $RegionVariant.ToLowerInvariant()

# 兼容将 standard / full 直接传入 -Variant 的调用方式
if ($Variant -eq "standard" -or $Variant -eq "full") {
    $RegionVariant = $Variant
    $Variant = "debug"
}

if ($Variant -ne "debug" -and $Variant -ne "release") {
    Write-ErrorMsg "无效的构建变体: $Variant (仅支持 debug 或 release)"
    if ($Pause -and -not $NoPause) { pause }
    exit 1
}

if ($RegionVariant -ne "standard" -and $RegionVariant -ne "full") {
    Write-ErrorMsg "无效的地域构建变体: $RegionVariant (仅支持 standard 或 full)"
    if ($Pause -and -not $NoPause) { pause }
    exit 1
}

Write-Host "==============================================================================" -ForegroundColor DarkGreen
Write-Host " 《每周一山 · 成都周边50座山》移动端 App 自动化打包流水线" -ForegroundColor Green
Write-Host " 运行引擎: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion) (Host: $($Host.Name))" -ForegroundColor DarkGray
Write-Host " 工作目录: $ProjectRoot" -ForegroundColor DarkGray
Write-Host " 打包矩阵: Variant=$Variant | RegionVariant=$RegionVariant" -ForegroundColor Magenta
Write-Host "==============================================================================" -ForegroundColor DarkGreen

# -----------------------------------------------------------------------------
# 0. 前置地域离线包自动化构建与元数据同步
# -----------------------------------------------------------------------------
Write-Step "0/5 自动同步地域分包与元数据 (python scripts/build_region_packs.py)"
Write-Info "正在执行 scripts/build_region_packs.py 确保分包与哈希处于最新状态..."

$BuildRegionPacksScript = Join-Path $PSScriptRoot "build_region_packs.py"
if (Test-Path $BuildRegionPacksScript) {
    & python $BuildRegionPacksScript
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "python scripts/build_region_packs.py 执行失败，退出码: $LASTEXITCODE"
        if ($Pause -and -not $NoPause) { pause }
        exit $LASTEXITCODE
    }
    Write-Success "地域分包与 SHA-256 元数据同步完成！"
} else {
    Write-Warning "未找到 scripts/build_region_packs.py，跳过前置地域包构建。"
}

# -----------------------------------------------------------------------------
# 1. 环境变量自适应检测与补齐
# -----------------------------------------------------------------------------
Write-Step "1/5 检查并适配 JDK 17 与 Android SDK 编译环境"

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
    if ($Pause -and -not $NoPause) { pause }
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
    if ($Pause -and -not $NoPause) { pause }
    exit 1
}

$env:PATH = "$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:PATH"
Write-Success "ANDROID_HOME: $env:ANDROID_HOME"

# -----------------------------------------------------------------------------
# 2. 构建矩阵装配与 regions.json 临时资产预置管理
# -----------------------------------------------------------------------------
$RegionsJsonPath = Join-Path $ProjectRoot "src\data\regions.json"
$RegionsBakPath = Join-Path $ProjectRoot "src\data\regions.json.matrix.bak"
$NeedRestoreRegions = $false

try {
    Write-Step "2/5 装配地域构建矩阵 (-RegionVariant $RegionVariant)"
    if ($RegionVariant -eq "full") {
        Write-Info "全量模式 (-RegionVariant full): 将所有活跃地域预置为内置资产 (成都 + 重庆)..."
        Copy-Item -Path $RegionsJsonPath -Destination $RegionsBakPath -Force
        $NeedRestoreRegions = $true

        $rawJson = Get-Content $RegionsJsonPath -Raw -Encoding UTF8
        $regionsList = $rawJson | ConvertFrom-Json
        foreach ($reg in $regionsList) {
            if ($reg.status -eq "active" -and $reg.packInfo) {
                $reg.packInfo.isDefaultInstalled = $true
            }
        }
        $updatedJson = $regionsList | ConvertTo-Json -Depth 10
        [System.IO.File]::WriteAllText($RegionsJsonPath, $updatedJson, [System.Text.Encoding]::UTF8)
        Write-Success "已将所有活跃地域装配为预置内置资产！"
    } else {
        Write-Info "标准瘦身模式 (-RegionVariant standard): 仅内置默认成都周边，其他地域应用内按需下载。"
    }

    $BuildCmd = if ($Variant -eq "release") { "build:release" } else { "build" }
    $GradleTask = if ($Variant -eq "release") { "assembleRelease" } else { "assembleDebug" }

    # 若为演练模式 (DryRun)，执行完整前置与校验逻辑后提前退出
    if ($DryRun) {
        Write-Host "`n==============================================================================" -ForegroundColor DarkYellow
        Write-Host " [DRY-RUN] 构建矩阵模拟演练模式已触发，前置验证全部就绪！" -ForegroundColor Yellow
        Write-Host " 构建参数: Variant=$Variant | RegionVariant=$RegionVariant" -ForegroundColor Gray
        Write-Host " 前端构建: npm run $BuildCmd" -ForegroundColor Gray
        Write-Host " 原生同步: npx cap sync android" -ForegroundColor Gray
        Write-Host " 原生编译: gradlew.bat $GradleTask" -ForegroundColor Gray
        Write-Host " 目标归档: releases/weekly-mountain-$RegionVariant.apk" -ForegroundColor Gray
        Write-Host "==============================================================================" -ForegroundColor DarkYellow
        Write-Success "构建矩阵校验成功通过！"
        return
    }

    # -----------------------------------------------------------------------------
    # 3. 前端工程生产构建
    # -----------------------------------------------------------------------------
    Write-Step "3/5 运行 Vite 前端生产构建 (npm run $BuildCmd - 变体: $Variant)"
    Write-Info "正在执行 npm run $BuildCmd 构建 dist/ 生产静态产物..."
    & npm run $BuildCmd
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "npm run $BuildCmd 失败，退出码: $LASTEXITCODE"
        if ($Pause -and -not $NoPause) { pause }
        exit $LASTEXITCODE
    }
    Write-Success "前端生产构建完成，dist/ 产物就绪！"

    # -----------------------------------------------------------------------------
    # 4. 同步 Web 资源至 Capacitor Android 容器
    # -----------------------------------------------------------------------------
    Write-Step "4/5 同步资源至 Capacitor Android 原生工程 (npx cap sync android)"
    Write-Info "正在将 dist 资源与原生插件同步至 android/ 容器..."
    & npx cap sync android
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "npx cap sync android 失败，退出码: $LASTEXITCODE"
        if ($Pause -and -not $NoPause) { pause }
        exit $LASTEXITCODE
    }
    Write-Success "Capacitor Android 容器资源同步完成！"

    # -----------------------------------------------------------------------------
    # 5. 运行 Gradle APK 编译
    # -----------------------------------------------------------------------------
    Write-Step "5/5 执行 Gradle APK 编译构建 (gradlew.bat $GradleTask)"

    $AndroidDir = Join-Path $ProjectRoot "android"
    if (-not (Test-Path $AndroidDir)) {
        Write-ErrorMsg "未找到 android 工程目录，请先执行 npx cap add android！"
        if ($Pause -and -not $NoPause) { pause }
        exit 1
    }

    Push-Location $AndroidDir
    try {
        if ($Clean) {
            Write-Info "正在执行 Gradle Clean 清理历史构建与缓存..."
            & .\gradlew.bat clean
        }
        Write-Info "正在启动 Gradle 进行 Native APK 打包 ($GradleTask)..."
        & .\gradlew.bat $GradleTask
        $GradleStatus = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($GradleStatus -ne 0) {
        Write-ErrorMsg "Gradle 编译 APK 失败，退出码: $GradleStatus"
        if ($Pause -and -not $NoPause) { pause }
        exit $GradleStatus
    }
    Write-Success "Gradle $GradleTask 编译完成！"

    # -----------------------------------------------------------------------------
    # 6. 产物校验与 releases 目录归档
    # -----------------------------------------------------------------------------
    $ApkSubdir = if ($Variant -eq "release") { "release" } else { "debug" }
    $ApkBaseName = if ($Variant -eq "release") { "app-release.apk" } else { "app-debug.apk" }
    $ApkSource = Join-Path $ProjectRoot "android\app\build\outputs\apk\$ApkSubdir\$ApkBaseName"
    $ReleaseDir = Join-Path $ProjectRoot "releases"

    if (-not (Test-Path $ReleaseDir)) {
        New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
    }

    if (Test-Path $ApkSource) {
        $PkgJson = Get-Content (Join-Path $ProjectRoot "package.json") -Raw | ConvertFrom-Json
        $Version = if ($PkgJson.version) { $PkgJson.version } else { "0.0.1.002" }

        # 矩阵版本归档名称
        $TargetName = "weekly-mountain-v$Version-$Variant-$RegionVariant.apk"
        $TargetPath = Join-Path $ReleaseDir $TargetName
        Copy-Item -Path $ApkSource -Destination $TargetPath -Force

        # 兼容旧版命名
        $LegacyPath = Join-Path $ReleaseDir "weekly-mountain-v$Version-$Variant.apk"
        Copy-Item -Path $ApkSource -Destination $LegacyPath -Force

        # 矩阵直接产物命名 (weekly-mountain-standard.apk / weekly-mountain-full.apk)
        $MatrixDirectPath = Join-Path $ReleaseDir "weekly-mountain-$RegionVariant.apk"
        Copy-Item -Path $ApkSource -Destination $MatrixDirectPath -Force

        # 最新镜像别名
        $LatestVariantPath = Join-Path $ReleaseDir "weekly-mountain-latest-$Variant-$RegionVariant.apk"
        Copy-Item -Path $ApkSource -Destination $LatestVariantPath -Force

        $LatestPath = Join-Path $ReleaseDir "weekly-mountain-latest-$Variant.apk"
        Copy-Item -Path $ApkSource -Destination $LatestPath -Force

        $ApkItem = Get-Item $TargetPath
        $SizeMB = [math]::Round($ApkItem.Length / 1MB, 2)

        Write-Host "`n==============================================================================" -ForegroundColor DarkGreen
        Write-Host " [成功] 移动端 APK 打包与矩阵归档全部完成！" -ForegroundColor Green
        Write-Host "==============================================================================" -ForegroundColor DarkGreen
        Write-Host " 变体类型: $Variant (编译变体) / $RegionVariant (地域分包矩阵)" -ForegroundColor Cyan
        Write-Host " 产物文件: $TargetName" -ForegroundColor Cyan
        Write-Host " 矩阵镜像: $(Split-Path $MatrixDirectPath -Leaf)" -ForegroundColor Cyan
        Write-Host " 最新镜像: $(Split-Path $LatestVariantPath -Leaf)" -ForegroundColor Cyan
        Write-Host " 物理路径: $TargetPath" -ForegroundColor White
        Write-Host " 文件大小: $SizeMB MB ($($ApkItem.Length) 字节)" -ForegroundColor Yellow
        Write-Host " 构建时间: $($ApkItem.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
        Write-Host " 支持系统: Android 7.0+ (API 24+)" -ForegroundColor DarkGray
        Write-Host "==============================================================================" -ForegroundColor DarkGreen
    } else {
        Write-ErrorMsg "未检测到 Gradle 生成的 APK 产物文件: $ApkSource"
        if ($Pause -and -not $NoPause) { pause }
        exit 1
    }

} finally {
    # 确保无论成功还是失败，均安全回滚恢复 regions.json
    if ($NeedRestoreRegions -and (Test-Path $RegionsBakPath)) {
        Copy-Item -Path $RegionsBakPath -Destination $RegionsJsonPath -Force
        Remove-Item -Path $RegionsBakPath -Force -ErrorAction SilentlyContinue
        Write-Info "已安全回滚恢复 regions.json 原始配置，保持 Git 工作区干净。"
    }
}

if ($Pause -and -not $NoPause) {
    Write-Host "`n按回车键退出..." -ForegroundColor DarkGray
    [void][System.Console]::ReadLine()
}

exit 0
