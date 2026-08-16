@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  OpenClaw Portable Launcher (Windows)
echo ========================================
echo.

:: --- Resolve script directory ---
set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%app"
set "CORE_DIR=%APP_DIR%\core"
set "RUNTIME_DIR=%APP_DIR%\runtime"
set "NODE_DIR=%RUNTIME_DIR%\node-win-x64"
set "NODE_EXE=%NODE_DIR%\node.exe"
set "DATA_DIR=%SCRIPT_DIR%data"
set "CONFIG_SERVER_DIR=%SCRIPT_DIR%config-server"

:: --- Debug: show resolved paths ---
echo Script dir: %SCRIPT_DIR%
echo Node exe:   %NODE_EXE%
echo.

:: --- Check Node.js exists ---
if exist "%NODE_EXE%" goto :node_ok
echo ERROR: Node.js not found at: %NODE_EXE%
echo Please run setup.bat first to install the runtime.
echo.
pause
exit /b 1
:node_ok

echo Node.js found. Starting...
echo.

:: --- Set environment variables ---
set "OPENCLAW_HOME=%DATA_DIR%\"
set "OPENCLAW_STATE_DIR=%DATA_DIR%\.openclaw"
set "OPENCLAW_CONFIG_PATH=%OPENCLAW_STATE_DIR%\openclaw.json"
set "OPENCLAW_DISABLE_BONJOUR=1"
set "PATH=%NODE_DIR%;%PATH%"

:: --- Detect FAT32/exFAT data drive. SQLite WAL cannot run on FAT (the
:: -shm/-wal sidecars surface as SQLITE_IOERR "disk I/O error", aborting the
:: gateway with "Could not start the CLI"); fall back to rollback journal.
:: The gateway then uses PRAGMA journal_mode = DELETE via the patched resolver. ---
set "OPENCLAW_FORCE_ROLLBACK_JOURNAL="
for /f "delims=" %%F in ('powershell -NoProfile -Command "(Get-Volume -DriveLetter %OPENCLAW_STATE_DIR:~0,1%).FileSystemType" 2^>nul') do set "OPENCLAW_DATA_FS=%%F"
if /i "%OPENCLAW_DATA_FS%"=="FAT32" set "OPENCLAW_FORCE_ROLLBACK_JOURNAL=1"
if /i "%OPENCLAW_DATA_FS%"=="exFAT" set "OPENCLAW_FORCE_ROLLBACK_JOURNAL=1"
if defined OPENCLAW_FORCE_ROLLBACK_JOURNAL (
    echo Data drive is %OPENCLAW_DATA_FS%: using rollback journal mode, SQLite WAL disabled.
)

:: --- Create data directories ---
if not exist "%DATA_DIR%\.openclaw" mkdir "%DATA_DIR%\.openclaw"
if not exist "%DATA_DIR%\.openclaw\agents" mkdir "%DATA_DIR%\.openclaw\agents"
if not exist "%DATA_DIR%\.openclaw\devices" mkdir "%DATA_DIR%\.openclaw\devices"
if not exist "%DATA_DIR%\.openclaw\identity" mkdir "%DATA_DIR%\.openclaw\identity"
if not exist "%DATA_DIR%\.openclaw\logs" mkdir "%DATA_DIR%\.openclaw\logs"
if not exist "%DATA_DIR%\.openclaw\tasks" mkdir "%DATA_DIR%\.openclaw\tasks"
if not exist "%DATA_DIR%\.openclaw\workspace" mkdir "%DATA_DIR%\.openclaw\workspace"
if not exist "%DATA_DIR%\backups" mkdir "%DATA_DIR%\backups"
if not exist "%DATA_DIR%\memory" mkdir "%DATA_DIR%\memory"

:: --- Create default config if missing ---
if not exist "%OPENCLAW_CONFIG_PATH%" (
    echo Creating default configuration...
    (
        echo {
        echo   "gateway": {
        echo     "mode": "local",
        echo     "auth": {
        echo       "token": "aipddclaw"
        echo     }
        echo   }
        echo }
    ) > "%OPENCLAW_CONFIG_PATH%"
)

:: --- Bootstrap activation (read activation.json, call activation API, inject AIPDD config) ---
echo Running activation bootstrap...
set "AIPDDCLAW_APP_ROOT=%SCRIPT_DIR%"
"%NODE_EXE%" "%SCRIPT_DIR%lib\bootstrap-activation.mjs" "%OPENCLAW_CONFIG_PATH%" 2>nul
if errorlevel 1 (
    echo [WARN] Activation bootstrap failed, continuing with existing config.
) else (
    echo Activation bootstrap complete.
)
echo.

:: --- Patch Control UI with a boot loading animation (idempotent) ---
:: Re-applies the patch if an OpenClaw upgrade restored the pristine template.
echo Patching Control UI...
"%NODE_EXE%" "%SCRIPT_DIR%lib\patch-control-ui.mjs" "%CORE_DIR%\node_modules\openclaw\dist\control-ui\index.html"
if errorlevel 1 (
    echo [WARN] Control UI patch failed, continuing.
) else (
    echo Control UI ready.
)
echo.

:: --- Patch SQLite journal policy so the gateway skips WAL on FAT32/exFAT ---
:: Re-applies the patch if an OpenClaw upgrade replaced the dist chunk.
echo Patching SQLite journal policy...
"%NODE_EXE%" "%SCRIPT_DIR%lib\patch-journal-mode.mjs" "%CORE_DIR%\node_modules\openclaw\dist"
if errorlevel 1 (
    echo [WARN] Journal policy patch failed, continuing.
) else (
    echo Journal policy ready.
)
echo.

:: --- Clean up occupied ports (18788 for config, 18789 for gateway) ---
echo Checking ports 18788 and 18789...
for %%P in (18788 18789) do (
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING"') do (
        echo Port %%P is occupied by PID %%i, killing...
        taskkill /F /PID %%i >nul 2>&1
        timeout /t 1 /nobreak >nul
    )
)
echo Ports cleared.
echo.

:: --- Check if API key is already configured ---
set "NEED_CONFIG=0"
"%NODE_EXE%" "%SCRIPT_DIR%lib\check-apikey.mjs" "%OPENCLAW_CONFIG_PATH%" 2>nul
if errorlevel 1 set "NEED_CONFIG=1"

:: --- Start config center (background) ---
echo Starting config center...
start "OpenClaw Config" /B "%NODE_EXE%" "%CONFIG_SERVER_DIR%\server.js"

:: Wait for config center to be ready (poll up to ~15s)
set "CONFIG_PORT=18788"
for /l %%i in (1,1,15) do (
    if exist "%DATA_DIR%\.config-server-port" (
        set /p CONFIG_PORT=<"%DATA_DIR%\.config-server-port"
    )
    if "!CONFIG_PORT!"=="" set "CONFIG_PORT=18788"
    curl -s -o nul --max-time 1 "http://127.0.0.1:!CONFIG_PORT!/" >nul 2>&1
    if not errorlevel 1 goto :config_ready
    timeout /t 1 /nobreak >nul
)
echo [WARN] Config center did not respond, continuing with default port 18788.
:config_ready
echo Config center is running on port !CONFIG_PORT!.

:: --- Set gateway port ---
set "GATEWAY_PORT=18789"

if "%NEED_CONFIG%"=="1" (
    :: --- First run: wait for user to configure API key ---
    echo.
    echo ========================================
    echo  First-time setup: please configure your API key
    echo ========================================
    echo.
    echo Opening config page in browser...
    start "" "http://127.0.0.1:!CONFIG_PORT!"
    echo.
    echo Waiting for API key to be configured...
    :wait_for_apikey
    timeout /t 3 /nobreak >nul
    "%NODE_EXE%" "%SCRIPT_DIR%lib\check-apikey.mjs" "%OPENCLAW_CONFIG_PATH%" 2>nul
    if errorlevel 1 goto :wait_for_apikey
    echo API key detected! Starting gateway...
    echo.
) else (
    echo API key already configured, skipping config page.
    echo.
)

:: --- Start OpenClaw gateway (background) ---
:: Wait for openclaw.json to stop changing first. OpenClaw refuses to run when
:: the config changes between its startup snapshot and migration check, so an
:: in-flight write (bootstrap/config-server) could otherwise race the gateway
:: boot and abort it. Polls until mtime+size are stable for ~1.5s (max 6s).
echo Waiting for config to stabilize...
"%NODE_EXE%" -e "const fs=require('fs');const p=process.argv[1];let prev='';let stable=0;const t0=Date.now();while(Date.now()-t0<6000){let cur='missing';try{const s=fs.statSync(p);cur=s.mtimeMs+'|'+s.size}catch(e){}if(cur===prev){if(++stable>=3)break}else{stable=0;prev=cur}Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,500)}process.exit(0)" "%OPENCLAW_CONFIG_PATH%"
echo Config stable, starting gateway...
echo Starting OpenClaw gateway on port !GATEWAY_PORT!...
echo.

:: Open browser to the gateway waiting page. It shows the loading style right
:: away and auto-redirects to the chat page once the gateway is ready, so the
:: user never sees the browser's "can't reach this site" error while the
:: gateway is still booting.
if "%NEED_CONFIG%"=="0" start "" "http://127.0.0.1:!CONFIG_PORT!/wait"

:: Run the gateway in the background so this script can wait for it to become
:: ready before opening the chat page. The gateway takes several seconds to
:: listen on the port, so a page opened right after startup (manually or by
:: the script) would fail with ERR_CONNECTION_REFUSED.
set "GATEWAY_ATTEMPT=0"
:gateway_start
set /a GATEWAY_ATTEMPT+=1
echo Starting OpenClaw gateway on port !GATEWAY_PORT! (attempt !GATEWAY_ATTEMPT!)...
:: Make sure no leftover gateway from a previous attempt is holding the port
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":!GATEWAY_PORT! " ^| findstr "LISTENING"') do taskkill /F /PID %%i >nul 2>&1
:: Remove stale SQLite -shm/-wal sidecars left by unclean shutdowns. The state
:: DB runs in WAL mode; on a FAT32 USB stick a stale sidecar makes the gateway
:: fail with "disk I/O error" ("Could not start the CLI"). No gateway holds
:: the DB at this point, so the cleanup is safe (checkpoints data first).
"%NODE_EXE%" "%SCRIPT_DIR%lib\cleanup-state-db.mjs" "%OPENCLAW_STATE_DIR%" >nul 2>&1
start "OpenClaw Gateway" /B "%NODE_EXE%" "%CORE_DIR%\node_modules\openclaw\openclaw.mjs" gateway run --allow-unconfigured --force --port !GATEWAY_PORT!

:: Wait for the gateway to respond on its port (up to ~20s per attempt).
:: A config race can abort the first attempt with exit code 1, so retry a
:: few times before giving up.
echo Waiting for gateway to be ready...
for /l %%i in (1,1,20) do (
    curl -s -o nul --max-time 2 "http://127.0.0.1:!GATEWAY_PORT!/" >nul 2>&1
    if not errorlevel 1 goto :gateway_ready
    timeout /t 1 /nobreak >nul
)
echo.
echo [WARN] Gateway did not respond within 20s (attempt !GATEWAY_ATTEMPT!).
if !GATEWAY_ATTEMPT! LSS 3 (
    echo Gateway may have aborted during startup (config race); retrying in 3 seconds...
    timeout /t 3 /nobreak >nul
    goto :gateway_start
)
goto :gateway_open
:gateway_ready
echo Gateway is ready.
:gateway_open
echo.

:: The waiting page opened earlier auto-redirects to the chat now that the
:: gateway is up. On first-time runs it was not opened yet, so open it here
:: (the gateway is already ready, so it redirects immediately).
if "%NEED_CONFIG%"=="1" start "" "http://127.0.0.1:!CONFIG_PORT!/wait"
echo Chat page opening.

:: Keep this window open and wait for the gateway to exit
:gateway_wait
timeout /t 2 /nobreak >nul
set "GW_LISTENING=0"
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":!GATEWAY_PORT! " ^| findstr "LISTENING"') do set "GW_LISTENING=1"
if "!GW_LISTENING!"=="1" goto :gateway_wait

echo.
echo OpenClaw gateway stopped.
pause
