#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Configuration ---
$NodeVersion = "v22.22.3"
$NodeZipName = "node-$NodeVersion-win-x64"
$NodeDownloadUrl = "https://npmmirror.com/mirrors/node/$NodeVersion/$NodeZipName.zip"
$NpmRegistry = "https://registry.npmmirror.com"

# --- Directories (relative to this script) ---
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppDir = Join-Path $ScriptDir "app"
$CoreDir = Join-Path $AppDir "core"
$RuntimeDir = Join-Path $AppDir "runtime"
$NodeDir = Join-Path $RuntimeDir "node-win-x64"
$NodeExe = Join-Path $NodeDir "node.exe"
$NpmCmd = Join-Path $NodeDir "npm.cmd"
$TempDir = Join-Path $ScriptDir ".tmp"

# --- Banner ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " OpenClaw Portable Installer (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Download Node.js ---
New-Item -ItemType Directory -Force -Path $CoreDir | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

if (Test-Path $NodeExe) {
    Write-Host "[1/3] Node.js (win-x64) already exists, skipping download" -ForegroundColor Green
} else {
    Write-Host "[1/3] Downloading Node.js $NodeVersion (win-x64)..." -ForegroundColor Yellow
    Write-Host "       URL: $NodeDownloadUrl"

    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    New-Item -ItemType Directory -Force -Path $NodeDir | Out-Null

    $ZipPath = Join-Path $TempDir "$NodeZipName.zip"

    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $NodeDownloadUrl -OutFile $ZipPath -UseBasicParsing
    $ProgressPreference = 'Continue'

    Write-Host "       Extracting to $NodeDir ..."

    $extractDir = Join-Path $TempDir $NodeZipName
    Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force

    $nestedDir = Join-Path $TempDir $NodeZipName
    if (Test-Path $nestedDir) {
        Copy-Item -Path "$nestedDir\*" -Destination $NodeDir -Recurse -Force
    }

    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue

    if (-not (Test-Path $NodeExe)) {
        Write-Host "ERROR: Node.js extraction failed. node.exe not found at $NodeExe" -ForegroundColor Red
        exit 1
    }

    Write-Host "       Node.js installed successfully" -ForegroundColor Green
}

# --- Step 2: Install OpenClaw via npm ---
$OpenClawDir = Join-Path $CoreDir "node_modules\openclaw"

if (Test-Path $OpenClawDir) {
    Write-Host "[2/3] OpenClaw already installed, skipping" -ForegroundColor Green
} else {
    Write-Host "[2/3] Installing OpenClaw (latest) via npm..." -ForegroundColor Yellow

    $PackageJson = Join-Path $CoreDir "package.json"
    if (-not (Test-Path $PackageJson)) {
        $packageContent = @{
            name = "openclaw-portable"
            version = "1.0.0"
            private = $true
            dependencies = @{
                openclaw = "latest"
            }
        } | ConvertTo-Json -Depth 3
        Set-Content -Path $PackageJson -Value $packageContent -Encoding UTF8
    }

    Push-Location $CoreDir
    try {
        & $NpmCmd install --registry=$NpmRegistry
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }

    Write-Host "       OpenClaw installed successfully" -ForegroundColor Green
}

# --- Step 3: Install built-in skills ---
$SkillSrc = Join-Path $ScriptDir "skills\aipdd-media"
$SkillDst = Join-Path $CoreDir "node_modules\openclaw\skills\aipdd-media"

if ((Test-Path $SkillSrc) -and (Test-Path $OpenClawDir)) {
    if (Test-Path $SkillDst) {
        Write-Host "[3/3] AIPDD Media Skill already installed, skipping" -ForegroundColor Green
    } else {
        Write-Host "[3/3] Installing AIPDD Media Skill..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $SkillDst | Out-Null
        Copy-Item -Path (Join-Path $SkillSrc "*") -Destination $SkillDst -Recurse -Force
        Write-Host "       AIPDD Media Skill installed" -ForegroundColor Green
    }
}

# --- Done ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Directory structure:"
Write-Host "  portable/"
Write-Host "    app/"
Write-Host "      core/          <- OpenClaw + node_modules"
Write-Host "      runtime/"
Write-Host "        node-win-x64/  <- Node.js $NodeVersion"
Write-Host ""
Write-Host "To start OpenClaw, run:  Windows-Start.bat"
Write-Host ""
