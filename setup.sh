#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
NODE_VERSION="v22.22.3"
NPM_REGISTRY="https://registry.npmmirror.com"

# --- Directories (relative to this script) ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"
CORE_DIR="$APP_DIR/core"
RUNTIME_DIR="$APP_DIR/runtime"

# --- Detect OS and Architecture ---
OS="$(uname -s)"
ARCH="$(uname -m)"

if [ "$OS" != "Darwin" ]; then
    echo "ERROR: This script is for macOS only. Use setup.ps1 on Windows."
    exit 1
fi

case "$ARCH" in
    arm64)
        NODE_PLATFORM="darwin-arm64"
        NODE_DIR="$RUNTIME_DIR/node-mac-arm64"
        ;;
    x86_64)
        NODE_PLATFORM="darwin-x64"
        NODE_DIR="$RUNTIME_DIR/node-mac-x64"
        ;;
    *)
        echo "ERROR: Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

NODE_TAR_NAME="node-${NODE_VERSION}-${NODE_PLATFORM}"
NODE_DOWNLOAD_URL="https://npmmirror.com/mirrors/node/${NODE_VERSION}/${NODE_TAR_NAME}.tar.gz"
NODE_BIN="$NODE_DIR/bin/node"
NPM_BIN="$NODE_DIR/bin/npm"
TEMP_DIR="$SCRIPT_DIR/.tmp"

# --- Banner ---
echo ""
echo "========================================"
echo " OpenClaw Portable Installer (macOS)"
echo "========================================"
echo ""
echo "  Architecture: $ARCH -> $NODE_PLATFORM"
echo ""

# --- Step 1: Download Node.js ---
mkdir -p "$CORE_DIR"
mkdir -p "$RUNTIME_DIR"

if [ -f "$NODE_BIN" ]; then
    echo "[1/3] Node.js ($NODE_PLATFORM) already exists, skipping download"
else
    echo "[1/3] Downloading Node.js $NODE_VERSION ($NODE_PLATFORM)..."
    echo "       URL: $NODE_DOWNLOAD_URL"

    mkdir -p "$TEMP_DIR"
    mkdir -p "$NODE_DIR"

    TAR_PATH="$TEMP_DIR/${NODE_TAR_NAME}.tar.gz"

    curl -# -L -o "$TAR_PATH" "$NODE_DOWNLOAD_URL"

    echo "       Extracting to $NODE_DIR ..."

    tar -xzf "$TAR_PATH" -C "$TEMP_DIR"
    cp -R "$TEMP_DIR/${NODE_TAR_NAME}/"* "$NODE_DIR/"

    rm -rf "$TEMP_DIR"

    xattr -rd com.apple.quarantine "$NODE_BIN" 2>/dev/null || true

    if [ ! -f "$NODE_BIN" ]; then
        echo "ERROR: Node.js extraction failed. node not found at $NODE_BIN"
        exit 1
    fi

    echo "       Node.js installed successfully"
fi

# --- Step 2: Install OpenClaw via npm ---
OPENCLAW_DIR="$CORE_DIR/node_modules/openclaw"

if [ -d "$OPENCLAW_DIR" ]; then
    echo "[2/3] OpenClaw already installed, skipping"
else
    echo "[2/3] Installing OpenClaw (latest) via npm..."

    PACKAGE_JSON="$CORE_DIR/package.json"
    if [ ! -f "$PACKAGE_JSON" ]; then
        cat > "$PACKAGE_JSON" <<'PKGJSON'
{
  "name": "openclaw-portable",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "openclaw": "latest"
  }
}
PKGJSON
    fi

    cd "$CORE_DIR"
    "$NPM_BIN" install --registry="$NPM_REGISTRY"
    cd "$SCRIPT_DIR"

    echo "       OpenClaw installed successfully"
fi

# --- Step 3: Install built-in skills ---
SKILL_SRC="$SCRIPT_DIR/skills/aipdd-media"
SKILL_DST="$CORE_DIR/node_modules/openclaw/skills/aipdd-media"

if [ -d "$SKILL_SRC" ] && [ -d "$CORE_DIR/node_modules/openclaw" ]; then
    if [ ! -d "$SKILL_DST" ]; then
        echo "[3/3] Installing AIPDD Media Skill..."
        mkdir -p "$SKILL_DST"
        cp -R "$SKILL_SRC/"* "$SKILL_DST/"
        echo "       AIPDD Media Skill installed"
    else
        echo "[3/3] AIPDD Media Skill already installed, skipping"
    fi
fi

# --- Make macOS launchers executable ---
chmod +x "$SCRIPT_DIR/Mac-Start.command" 2>/dev/null || true

# --- Done ---
echo ""
echo "========================================"
echo " Installation Complete!"
echo "========================================"
echo ""
echo "Directory structure:"
echo "  portable/"
echo "    app/"
echo "      core/            <- OpenClaw + node_modules"
echo "      runtime/"
echo "        ${NODE_DIR##*/}/  <- Node.js $NODE_VERSION"
echo ""
echo "To start OpenClaw, run:  Mac-Start.command"
echo ""
