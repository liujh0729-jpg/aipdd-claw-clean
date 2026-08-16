#!/usr/bin/env bash
set -euo pipefail

# --- Resolve script directory ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"
CORE_DIR="$APP_DIR/core"
RUNTIME_DIR="$APP_DIR/runtime"
DATA_DIR="$SCRIPT_DIR/data"
CONFIG_SERVER_DIR="$SCRIPT_DIR/config-server"

echo ""
echo "========================================"
echo " OpenClaw Portable Launcher (macOS)"
echo "========================================"
echo ""

# --- Detect architecture ---
ARCH="$(uname -m)"
case "$ARCH" in
    arm64)  NODE_DIR="$RUNTIME_DIR/node-mac-arm64" ;;
    x86_64) NODE_DIR="$RUNTIME_DIR/node-mac-x64" ;;
    *)      echo "ERROR: Unsupported architecture: $ARCH"; exit 1 ;;
esac

NODE_BIN="$NODE_DIR/bin/node"

# --- Check Node.js exists ---
if [ ! -f "$NODE_BIN" ]; then
    echo "ERROR: Node.js not found at $NODE_BIN"
    echo "Please run setup.sh first to install the runtime."
    exit 1
fi

# --- Remove quarantine attribute ---
xattr -rd com.apple.quarantine "$NODE_BIN" 2>/dev/null || true

# --- Set environment variables ---
export OPENCLAW_HOME="$DATA_DIR"
export OPENCLAW_STATE_DIR="$DATA_DIR/.openclaw"
export OPENCLAW_CONFIG_PATH="$OPENCLAW_STATE_DIR/openclaw.json"
export OPENCLAW_DISABLE_BONJOUR=1
export PATH="$NODE_DIR/bin:$PATH"

# --- Create data directories ---
mkdir -p "$DATA_DIR/.openclaw/agents" "$DATA_DIR/.openclaw/devices" "$DATA_DIR/.openclaw/identity" \
        "$DATA_DIR/.openclaw/logs" "$DATA_DIR/.openclaw/tasks" "$DATA_DIR/.openclaw/workspace" \
        "$DATA_DIR/backups" "$DATA_DIR/memory"

# --- Create default config if missing ---
if [ ! -f "$OPENCLAW_CONFIG_PATH" ]; then
    echo "Creating default configuration..."
    cat > "$OPENCLAW_CONFIG_PATH" <<'DEFAULTCFG'
{
  "gateway": {
    "mode": "local",
    "auth": {
      "token": "aipddclaw"
    }
  }
}
DEFAULTCFG
fi

# --- Bootstrap activation ---
echo "Running activation bootstrap..."
export AIPDDCLAW_APP_ROOT="$SCRIPT_DIR"
if "$NODE_BIN" "$SCRIPT_DIR/lib/bootstrap-activation.mjs" "$OPENCLAW_CONFIG_PATH" 2>/dev/null; then
    echo "Activation bootstrap complete."
else
    echo "[WARN] Activation bootstrap failed, continuing with existing config."
fi
echo ""

# --- Sync skill directories into OpenClaw config ---
# Point skills.load.extraDirs at the portable skills/ folder so updated skills
# (added or removed) take effect on the next gateway start.
echo "Configuring skill directories..."
"$NODE_BIN" -e "
const fs = require('fs');
const p = process.env.OPENCLAW_CONFIG_PATH;
const cfg = JSON.parse(fs.readFileSync(p, 'utf8'));
cfg.skills = cfg.skills || {};
cfg.skills.load = cfg.skills.load || {};
cfg.skills.load.extraDirs = [process.argv[1]];
cfg.skills.load.watch = true;
fs.writeFileSync(p, JSON.stringify(cfg, null, 2));
" "$SCRIPT_DIR/skills"
echo "Skill directories: $SCRIPT_DIR/skills"
echo ""

# --- Patch Control UI with a boot loading animation (idempotent) ---
# Re-applies the patch if an OpenClaw upgrade restored the pristine template.
echo "Patching Control UI..."
if "$NODE_BIN" "$SCRIPT_DIR/lib/patch-control-ui.mjs" "$CORE_DIR/node_modules/openclaw/dist/control-ui/index.html"; then
    echo "Control UI ready."
else
    echo "[WARN] Control UI patch failed, continuing."
fi
echo ""

# --- Clean up occupied ports (18788 for config, 18789 for gateway) ---
echo "Checking ports 18788 and 18789..."
for PORT in 18788 18789; do
    PID=$(lsof -i :"$PORT" -sTCP:LISTEN -t 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo "Port $PORT is occupied by PID $PID, killing..."
        kill -9 "$PID" 2>/dev/null || true
        sleep 1
    fi
done
echo "Ports cleared."
echo ""

# --- Check if API key is already configured ---
NEED_CONFIG=0
if ! "$NODE_BIN" "$SCRIPT_DIR/lib/check-apikey.mjs" "$OPENCLAW_CONFIG_PATH" 2>/dev/null; then
    NEED_CONFIG=1
fi

# --- Set gateway port ---
GATEWAY_PORT=18789
echo "Gateway port: $GATEWAY_PORT"

# --- Cleanup trap ---
CONFIG_PID=""
GATEWAY_PID=""

cleanup() {
    echo ""
    echo "Shutting down..."
    if [ -n "$GATEWAY_PID" ] && kill -0 "$GATEWAY_PID" 2>/dev/null; then
        kill "$GATEWAY_PID" 2>/dev/null || true
        wait "$GATEWAY_PID" 2>/dev/null || true
    fi
    if [ -n "$CONFIG_PID" ] && kill -0 "$CONFIG_PID" 2>/dev/null; then
        kill "$CONFIG_PID" 2>/dev/null || true
        wait "$CONFIG_PID" 2>/dev/null || true
    fi
    echo "OpenClaw stopped."
}
trap cleanup EXIT INT TERM

# --- Start config center (background) ---
echo "Starting config center..."
"$NODE_BIN" "$CONFIG_SERVER_DIR/server.js" &
CONFIG_PID=$!

# Wait briefly for config center to start
sleep 2

# Read config center port from file
CONFIG_PORT=18788
if [ -f "$DATA_DIR/.config-server-port" ]; then
    CONFIG_PORT="$(cat "$DATA_DIR/.config-server-port")"
fi

if [ "$NEED_CONFIG" -eq 1 ]; then
    # --- First run: wait for user to configure API key ---
    echo ""
    echo "========================================"
    echo " First-time setup: please configure your API key"
    echo "========================================"
    echo ""
    echo "Opening config page in browser..."
    open "http://127.0.0.1:$CONFIG_PORT"
    echo ""
    echo "Waiting for API key to be configured..."
    while true; do
        sleep 3
        if "$NODE_BIN" "$SCRIPT_DIR/lib/check-apikey.mjs" "$OPENCLAW_CONFIG_PATH" 2>/dev/null; then
            break
        fi
    done
    echo "API key detected! Starting gateway..."
    echo ""
else
    echo "API key already configured, skipping config page."
    echo ""
fi

# --- Close stale gateway / waiting-page tabs before opening anything new ---
# Browsers do not let a page close tabs it did not open, so this is done at the
# system level: enumerate Chrome/Edge/Safari tabs and close any whose URL points
# at the gateway or the waiting page, so every start leaves exactly one clean
# chat tab. Browsers that are not running are skipped silently.
for BROWSER in "Google Chrome" "Microsoft Edge" "Safari"; do
    osascript -e "
if application \"$BROWSER\" is running then
    tell application \"$BROWSER\"
        set targets to {}
        repeat with w in windows
            repeat with t in tabs of w
                if URL of t contains \"127.0.0.1:$GATEWAY_PORT\" or URL of t contains \"/wait\" then set end of targets to t
            end repeat
        end repeat
        repeat with t in targets
            close t
        end repeat
    end tell
end if" 2>/dev/null || true
done

# Open the waiting page now: it shows the loading style while the gateway is
# still booting and auto-redirects to the chat page once the gateway answers,
# so the user never sees the browser's "can't reach this site" error.
if [ "$NEED_CONFIG" -eq 0 ]; then
    open "http://127.0.0.1:$CONFIG_PORT/wait"
fi

# --- Wait for the config file to stop changing ---
# OpenClaw refuses to run when the config changes between its startup snapshot
# and migration check (observed as "Config observe anomaly ... size-drop-vs-
# last-good"), so an in-flight write (bootstrap / config-server) could race the
# gateway boot and abort it. Polls until mtime+size are stable for ~1.5s (max 6s).
echo "Waiting for config to stabilize..."
"$NODE_BIN" -e "
const fs = require('fs');
const p = process.env.OPENCLAW_CONFIG_PATH;
let prev = '';
let stable = 0;
const t0 = Date.now();
while (Date.now() - t0 < 6000) {
  let cur = 'missing';
  try { const s = fs.statSync(p); cur = s.mtimeMs + '|' + s.size; } catch (e) {}
  if (cur === prev) { if (++stable >= 3) break; } else { stable = 0; prev = cur; }
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 500);
}
"
echo "Config stable, starting gateway..."
echo ""

# --- Start OpenClaw gateway (background) with retries ---
# A config race (see above) can abort the first attempt with exit code 1, so
# retry a few times before giving up.
GATEWAY_ATTEMPT=0
while :; do
    GATEWAY_ATTEMPT=$((GATEWAY_ATTEMPT + 1))
    echo "Starting OpenClaw gateway on port $GATEWAY_PORT (attempt $GATEWAY_ATTEMPT)..."
    # Make sure no leftover gateway is holding the port
    PID=$(lsof -i :"$GATEWAY_PORT" -sTCP:LISTEN -t 2>/dev/null || true)
    [ -n "$PID" ] && kill -9 "$PID" 2>/dev/null || true
    "$NODE_BIN" "$CORE_DIR/node_modules/openclaw/openclaw.mjs" gateway run --allow-unconfigured --force --port "$GATEWAY_PORT" &
    GATEWAY_PID=$!

    # Wait for the gateway to respond on its port (up to 20s per attempt).
    READY=0
    for i in $(seq 1 20); do
        if curl -s -o /dev/null --max-time 2 "http://127.0.0.1:$GATEWAY_PORT/"; then
            READY=1
            break
        fi
        # Stop polling if the gateway process exited mid-startup
        if ! kill -0 "$GATEWAY_PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    if [ "$READY" -eq 1 ]; then
        echo "Gateway is ready."
        break
    fi
    echo "[WARN] Gateway did not respond within 20s (attempt $GATEWAY_ATTEMPT)."
    kill "$GATEWAY_PID" 2>/dev/null || true
    wait "$GATEWAY_PID" 2>/dev/null || true
    if [ "$GATEWAY_ATTEMPT" -ge 3 ]; then
        break
    fi
    echo "Gateway may have aborted during startup (config race); retrying in 3 seconds..."
    sleep 3
done

# First-time runs: the waiting page was not opened yet (user was on the config
# page), open it now — the gateway is already ready, so it redirects immediately.
if [ "$NEED_CONFIG" -eq 1 ]; then
    open "http://127.0.0.1:$CONFIG_PORT/wait"
fi
echo ""
echo "Chat page opening..."
echo ""

# Wait for gateway to exit
wait "$GATEWAY_PID" 2>/dev/null || true
