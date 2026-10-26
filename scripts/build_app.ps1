<#
.SYNOPSIS
    銆婃瘡鍛ㄤ竴灞便€嬬Щ鍔ㄧ App 鑷姩鍖栨墦鍖呮祦姘寸嚎 (PowerShell / pwsh)
.DESCRIPTION
    鎵ц娴佺▼锛?    1. 鐜鏅鸿兘鎰熺煡涓庤嚜鍔ㄥ榻?(JDK 17 LTS + Android SDK)
    2. Vite 5 + Vue 3 鍓嶇宸ョ▼鐢熶骇鏋勫缓涓庤祫婧愬悓姝?    3. Capacitor 8 Android 鍘熺敓瀹瑰櫒鍚屾
    4. Gradle 缂栬瘧鐢熸垚 Android Debug/Release APK
    5. 浜х墿鏍￠獙銆佷綋绉噺鍖栦笌 release 鐩綍鑷姩褰掓。
#>

param(
    [switch]$Pause,
    [switch]$NoPause,
    [switch]$Clean,
    [string]$Variant = "debug"
)

# 纭繚 UTF-8 鎺у埗鍙板瓧绗﹂泦
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Host.UI.RawUI.WindowTitle = "姣忓懆涓€灞?- 绉诲姩绔?App 鎵撳寘娴佹按绾?

function Write-Step([string]$title) {
    Write-Host "`n==============================================================================" -ForegroundColor DarkCyan
    Write-Host " [姝ラ] $title" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor DarkCyan
}

function Write-Success([string]$msg) {
    Write-Host " [鎴愬姛] $msg" -ForegroundColor Green
}

function Write-Info([string]$msg) {
    Write-Host " [淇℃伅] $msg" -ForegroundColor Gray
}

function Write-Warning([string]$msg) {
    Write-Host " [璀﹀憡] $msg" -ForegroundColor Yellow
}

function Write-ErrorMsg([string]$msg) {
    Write-Host " [閿欒] $msg" -ForegroundColor Red
}

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

Write-Host "==============================================================================" -ForegroundColor DarkGreen
Write-Host " 銆婃瘡鍛ㄤ竴灞?路 鎴愰兘鍛ㄨ竟50搴у北銆嬬Щ鍔ㄧ App 鑷姩鍖栨墦鍖呮祦姘寸嚎" -ForegroundColor Green
Write-Host " 杩愯鐜: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion) (寮曟搸: $($Host.Name))" -ForegroundColor DarkGray
Write-Host " 宸ヤ綔鐩綍: $ProjectRoot" -ForegroundColor DarkGray
Write-Host "==============================================================================" -ForegroundColor DarkGreen

# -----------------------------------------------------------------------------
# 0. 鐜鍙橀噺鑷€傚簲妫€娴嬩笌琛ラ綈
# -----------------------------------------------------------------------------
Write-Step "0/4 妫€鏌ュ苟閫傞厤 JDK 17 涓?Android SDK 缂栬瘧鐜"

# 妫€娴嬩笌琛ラ綈 JAVA_HOME
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
    Write-ErrorMsg "鏈壘鍒版湁鏁堢殑 JDK 17 瀹夎鐩綍锛佽妫€鏌?JAVA_HOME 閰嶇疆銆?
    if ($Pause) { pause }
    exit 1
}

# 纭繚 JAVA_HOME/bin 浼樺厛杩涘叆 PATH
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
Write-Success "JAVA_HOME: $env:JAVA_HOME"

# 妫€娴嬩笌琛ラ綈 ANDROID_HOME
$ValidAndroidHome = $false
if ($env:ANDROID_HOME -and (Test-Path "$env:ANDROID_HOME\platform-tools")) {
    $ValidAndroidHome = $true
} else {
    $AndroidCandidates = @(
        "D:\soft\android-sdk",
        "$env:LOCALAPPDATA\Android\Sdk",
        "C:\Android\sdk"
    )
    foreach ($cand in $AndroidCandidates) {
        if (Test-Path "$cand\platform-tools") {
            $env:ANDROID_HOME = $cand
            $ValidAndroidHome = $true
            break
        }
    }
}

if (-not $ValidAndroidHome) {
    Write-ErrorMsg "鏈壘鍒版湁鏁堢殑 Android SDK 鐩綍锛佽妫€鏌?ANDROID_HOME 閰嶇疆銆?
    if ($Pause) { pause }
    exit 1
}
Write-Success "ANDROID_HOME: $env:ANDROID_HOME"

# 妫€鏌?Node.js
try {
    $nodeVer = node --version
    Write-Info "Node.js 鐗堟湰: $nodeVer"
} catch {
    Write-ErrorMsg "鏈壘鍒?Node.js锛岃鍏堝畨瑁?Node 鐜锛?
    if ($Pause) { pause }
    exit 1
}

# -----------------------------------------------------------------------------
# 0.5 娣卞害娓呯悊鍘嗗彶鏋勫缓缂撳瓨 (鍙€?-Clean 寮€鍏?
# -----------------------------------------------------------------------------
if ($Clean) {
    Write-Step "0.5/4 娣卞害娓呯悊鍘嗗彶缂撳瓨 (Clean Build Mode)"
    Write-Info "姝ｅ湪娓呯┖ dist 鐢熶骇浜х墿鐩綍..."
    $DistDir = Join-Path $ProjectRoot "dist"
    if (Test-Path $DistDir) {
        Remove-Item -Path $DistDir -Recurse -Force -ErrorAction SilentlyContinue
    }

    $AndroidAssetsDir = Join-Path $ProjectRoot "android\app\src\main\assets\public"
    Write-Info "姝ｅ湪娓呯┖ Android 鍘熺敓 assets 缂撳瓨..."
    if (Test-Path $AndroidAssetsDir) {
        Remove-Item -Path $AndroidAssetsDir -Recurse -Force -ErrorAction SilentlyContinue
    }

    $AndroidDir = Join-Path $ProjectRoot "android"
    if (Test-Path $AndroidDir) {
        Write-Info "姝ｅ湪鎵ц Gradle clean 娓呯┖ Android 缂栬瘧缂撳瓨..."
        Push-Location $AndroidDir
        try {
            & .\gradlew.bat clean
        } finally {
            Pop-Location
        }
    }
    Write-Success "鍏ㄩ摼璺巻鍙茬紦瀛樻竻绌哄畬鎴愶紝鍗冲皢杩涜鏃犵紦瀛樺叏閲忕紪璇戯紒"
}

# -----------------------------------------------------------------------------
# 1. 鍓嶇宸ョ▼鐢熶骇鏋勫缓
# -----------------------------------------------------------------------------
Write-Step "1/4 杩愯 Vite 5 鍓嶇鐢熶骇鎵撳寘 (npm run build)"
Write-Info "姝ｅ湪缂栬瘧 Vue 3 鏍稿績缁勪欢骞跺悓姝?153 寮犲悕灞遍珮娓呴鏅浘璧勪骇..."

& npm run build
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "npm run build 鏋勫缓澶辫触锛岄€€鍑虹爜: $LASTEXITCODE"
    if ($Pause) { pause }
    exit $LASTEXITCODE
}
Write-Success "鍓嶇鐢熶骇鏋勫缓瀹屾垚锛宒ist/ 浜х墿涓庨鏅浘璧勪骇灏辩华锛?

# -----------------------------------------------------------------------------
# 2. Capacitor Android 瀹瑰櫒璧勬簮鍚屾
# -----------------------------------------------------------------------------
Write-Step "2/4 鍚屾 Web 璧勬簮鑷?Capacitor Android 宸ョ▼ (npx cap sync android)"

& npx cap sync android
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Capacitor 鍚屾澶辫触锛岄€€鍑虹爜: $LASTEXITCODE"
    if ($Pause) { pause }
    exit $LASTEXITCODE
}
Write-Success "Web 璧勪骇涓?Android 鍘熺敓鎻掍欢娓呭崟宸插榻愶紒"

# -----------------------------------------------------------------------------
# 3. Gradle 缂栬瘧 Android APK
# -----------------------------------------------------------------------------
Write-Step "3/4 鎵ц Gradle APK 缂栬瘧 (gradlew.bat assembleDebug)"

$AndroidDir = Join-Path $ProjectRoot "android"
if (-not (Test-Path $AndroidDir)) {
    Write-ErrorMsg "鏈壘鍒?android 宸ョ▼鐩綍锛岃鍏堟墽琛?npx cap add android锛?
    if ($Pause) { pause }
    exit 1
}

Push-Location $AndroidDir
try {
    Write-Info "姝ｅ湪鍚姩 Gradle Daemon 杩涜 Native APK 鎵撳寘..."
    & .\gradlew.bat assembleDebug
    $GradleStatus = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($GradleStatus -ne 0) {
    Write-ErrorMsg "Gradle 缂栬瘧 APK 澶辫触锛岄€€鍑虹爜: $GradleStatus"
    if ($Pause) { pause }
    exit $GradleStatus
}
Write-Success "Gradle assembleDebug 缂栬瘧瀹屾垚锛?

# -----------------------------------------------------------------------------
# 4. 浜х墿鏍￠獙涓?releases 鐩綍褰掓。
# -----------------------------------------------------------------------------
Write-Step "4/4 鏍￠獙骞跺綊妗?APK 浜х墿"

$ApkSource = Join-Path $ProjectRoot "android\app\build\outputs\apk\debug\app-debug.apk"
$ReleaseDir = Join-Path $ProjectRoot "releases"

if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
}

if (Test-Path $ApkSource) {
    $PkgJson = Get-Content (Join-Path $ProjectRoot "package.json") -Raw | ConvertFrom-Json
    $Version = if ($PkgJson.version) { $PkgJson.version } else { "2.0.0" }

    $TargetName = "weekly-mountain-v$Version-$Variant.apk"
    $TargetPath = Join-Path $ReleaseDir $TargetName

    Copy-Item -Path $ApkSource -Destination $TargetPath -Force
    $ApkItem = Get-Item $TargetPath
    $SizeMB = [math]::Round($ApkItem.Length / 1MB, 2)

    Write-Host "`n==============================================================================" -ForegroundColor DarkGreen
    Write-Host " [鎴愬姛] 绉诲姩绔?APK 鎵撳寘涓庡綊妗ｅ叏閮ㄥ畬鎴愶紒" -ForegroundColor Green
    Write-Host "==============================================================================" -ForegroundColor DarkGreen
    Write-Host " 浜х墿鏂囦欢: $TargetName" -ForegroundColor Cyan
    Write-Host " 鐗╃悊璺緞: $TargetPath" -ForegroundColor White
    Write-Host " 鏂囦欢澶у皬: $SizeMB MB ($($ApkItem.Length) 瀛楄妭)" -ForegroundColor Yellow
    Write-Host " 鏋勫缓鏃堕棿: $($ApkItem.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
    Write-Host " 鏀寔绯荤粺: Android 7.0+ (API 24+)" -ForegroundColor DarkGray
    Write-Host "==============================================================================" -ForegroundColor DarkGreen
} else {
    Write-ErrorMsg "鏈娴嬪埌 Gradle 鐢熸垚鐨?app-debug.apk 浜х墿鏂囦欢锛?
    if ($Pause) { pause }
    exit 1
}

if ($Pause) {
    Write-Host "`n鎸夊洖杞﹂敭閫€鍑?.." -ForegroundColor DarkGray
    [void][System.Console]::ReadLine()
}

exit 0
