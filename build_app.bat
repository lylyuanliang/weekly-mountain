@echo off
rem ==============================================================================
rem 《每周一山 · 成都周边50座山》移动端 App 跨 Shell 自动化打包脚本 (build_app.bat)
rem 调度优先级机制：
rem   1. 优先检测并调用 PowerShell 7 (pwsh.exe)
rem   2. 次选回退至 Windows 原生 PowerShell (powershell.exe)
rem   3. 兜底执行 CMD 原生批处理流水线
rem ==============================================================================
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

echo ==============================================================================
echo  [每周一山] 移动端 App 自动化打包流水线
echo ==============================================================================

:: 检查是否从文件资源管理器双击运行 (cmdcmdline 中包含当前脚本名称)
set "IS_EXPLORER_LAUNCH=0"
echo %cmdcmdline% | findstr /i /c:"%~nx0" >nul
if %ERRORLEVEL% equ 0 set "IS_EXPLORER_LAUNCH=1"

:: 命令行传入 -NoPause 或 --no-pause 时，强制静默不暂停
set "NO_PAUSE_FLAG=0"
set "FORCE_CMD=0"
for %%a in (%*) do (
    if /i "%%a"=="-NoPause" set "NO_PAUSE_FLAG=1"
    if /i "%%a"=="--no-pause" set "NO_PAUSE_FLAG=1"
    if /i "%%a"=="--cmd" set "FORCE_CMD=1"
    if /i "%%a"=="--force-cmd" set "FORCE_CMD=1"
)
if "%NO_PAUSE_FLAG%"=="1" set "IS_EXPLORER_LAUNCH=0"

if "%FORCE_CMD%"=="1" (
    echo [Shell 调度] 检测到 --cmd 参数，直接启动 CMD 原生构建流水线...
    echo.
    call :cmd_native_build %*
    set "BUILD_EXIT_CODE=!ERRORLEVEL!"
    goto :finish
)

:: -----------------------------------------------------------------------------
:: 1. 优先尝试 PowerShell 7 (pwsh.exe)
:: -----------------------------------------------------------------------------
where pwsh.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [Shell 调度] [1/3] 检测到 PowerShell 7 [pwsh.exe]，优先启动 PowerShell 7 执行打包...
    echo.
    if "!IS_EXPLORER_LAUNCH!"=="1" (
        pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_app.ps1" -Pause %*
    ) else (
        pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_app.ps1" %*
    )
    set "BUILD_EXIT_CODE=!ERRORLEVEL!"
    goto :finish
)

:: -----------------------------------------------------------------------------
:: 2. 次选尝试 Windows 原生 PowerShell (powershell.exe)
:: -----------------------------------------------------------------------------
where powershell.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [Shell 调度] [2/3] 未检测到 PowerShell 7，回退使用 Windows PowerShell [powershell.exe] 执行打包...
    echo.
    if "!IS_EXPLORER_LAUNCH!"=="1" (
        powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_app.ps1" -Pause %*
    ) else (
        powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_app.ps1" %*
    )
    set "BUILD_EXIT_CODE=!ERRORLEVEL!"
    goto :finish
)

:: -----------------------------------------------------------------------------
:: 3. 兜底纯 CMD 原生执行流程
:: -----------------------------------------------------------------------------
echo [Shell 调度] [3/3] 未检测到任何 PowerShell 环境，启动 CMD 原生构建流水线...
echo.
call :cmd_native_build %*
set "BUILD_EXIT_CODE=!ERRORLEVEL!"
goto :finish

:: -----------------------------------------------------------------------------
:: CMD 原生打包子例程 (Native CMD Fallback Routine)
:: -----------------------------------------------------------------------------
:cmd_native_build
echo ==============================================================================
echo  [步骤 0/4] 环境变量检查与自动对齐
echo ==============================================================================

if not defined JAVA_HOME (
    if exist "D:\soft\JDKS\jdk-17.0.16\jdk\bin\javac.exe" (
        set "JAVA_HOME=D:\soft\JDKS\jdk-17.0.16\jdk"
    )
)
if not defined JAVA_HOME (
    echo [错误] 未检测到有效的 JAVA_HOME，请配置 JDK 17！
    exit /b 1
)
set "PATH=%JAVA_HOME%\bin;%PATH%"
echo  [成功] JAVA_HOME: %JAVA_HOME%

if not defined ANDROID_HOME (
    if exist "D:\soft\android-sdk\platform-tools" (
        set "ANDROID_HOME=D:\soft\android-sdk"
    )
)
if not defined ANDROID_HOME (
    echo [错误] 未检测到有效的 ANDROID_HOME，请配置 Android SDK！
    exit /b 1
)
echo  [成功] ANDROID_HOME: %ANDROID_HOME%
echo.

echo ==============================================================================
echo  [步骤 1/4] 执行前端工程生产打包 (npm run build)
echo ==============================================================================
call npm run build
if !ERRORLEVEL! neq 0 (
    echo [错误] npm run build 失败，退出码: !ERRORLEVEL!
    exit /b !ERRORLEVEL!
)
echo  [成功] 前端生产构建完成，dist/ 产物就绪！
echo.

echo ==============================================================================
echo  [步骤 2/4] 同步 Web 资源至 Capacitor Android 容器 (npx cap sync android)
echo ==============================================================================
call npx cap sync android
if !ERRORLEVEL! neq 0 (
    echo [错误] npx cap sync android 失败，退出码: !ERRORLEVEL!
    exit /b !ERRORLEVEL!
)
echo  [成功] Capacitor Android 容器资源同步完成！
echo.

echo ==============================================================================
echo  [步骤 3/4] 运行 Gradle APK 编译 (gradlew.bat assembleDebug)
echo ==============================================================================
if not exist "android" (
    echo [错误] 未找到 android 目录！
    exit /b 1
)

cd android
call .\gradlew.bat assembleDebug
set "GRADLE_ERR=!ERRORLEVEL!"
cd ..
if !GRADLE_ERR! neq 0 (
    echo [错误] Gradle 编译 APK 失败，退出码: !GRADLE_ERR!
    exit /b !GRADLE_ERR!
)
echo  [成功] Gradle assembleDebug 编译完成！
echo.

echo ==============================================================================
echo  [步骤 4/4] 归档生成的 APK 产物
echo ==============================================================================
if not exist "releases" mkdir releases
set "SRC_APK=android\app\build\outputs\apk\debug\app-debug.apk"
set "DST_APK=releases\weekly-mountain-v2.0.0-debug.apk"

if exist "!SRC_APK!" (
    copy /y "!SRC_APK!" "!DST_APK!" >nul
    echo  [成功] APK 产物已归档至: !DST_APK!
) else (
    echo [警告] 未检测到生成的 app-debug.apk！
    exit /b 1
)
exit /b 0

:: -----------------------------------------------------------------------------
:: 收尾与状态反馈
:: -----------------------------------------------------------------------------
:finish
echo.
if "%BUILD_EXIT_CODE%"=="0" (
    echo ==============================================================================
    echo  [成功] 打包流程执行完毕！
    echo ==============================================================================
) else (
    echo ==============================================================================
    echo  [失败] 打包流程中途出现错误，退出码: %BUILD_EXIT_CODE%
    echo ==============================================================================
)

if "%IS_EXPLORER_LAUNCH%"=="1" (
    echo 按任意键退出...
    pause >nul
) else if not "%BUILD_EXIT_CODE%"=="0" (
    if not "%NO_PAUSE_FLAG%"=="1" (
        echo 按任意键退出...
        pause >nul
    )
)

exit /b %BUILD_EXIT_CODE%
