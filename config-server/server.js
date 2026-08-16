const http = require("http");
const fs = require("fs");
const path = require("path");

const CONFIG_PORT_START = 18788;
const CONFIG_PORT_END = 18798;

// Determine paths relative to this script
const SCRIPT_DIR = __dirname;
const PUBLIC_DIR = path.join(SCRIPT_DIR, "public");
const DATA_DIR = path.join(SCRIPT_DIR, "..", "data");
const CONFIG_PATH = path.join(DATA_DIR, ".openclaw", "openclaw.json");
const ACTIVATION_CACHE_PATH = path.join(DATA_DIR, ".openclaw", "activation-cache.json");
const ROOT_CONFIG_PATH = path.join(SCRIPT_DIR, "..", "config.json");
const DEFAULT_BASE_URL = "https://newapi.aipdd.work/v1";
const DEFAULT_MODEL = "deepseek-v4-flash";

// Append /v1 when the value is a bare site domain (no path); keep it unchanged
// if it already ends with /v1 or carries another path (e.g. /api/v3).
function ensureApiV1(url) {
  const base = String(url || "").trim().replace(/\/+$/, "");
  if (!base || /\/v1$/i.test(base)) return base;
  const path = base.replace(/^[a-z][a-z0-9+.+-]*:\/\/[^/]+/i, "");
  return path ? base : base + "/v1";
}

// Read raw default API base URL (site domain) from root config.json
function readSiteUrl() {
  try {
    const raw = fs.readFileSync(ROOT_CONFIG_PATH, "utf-8");
    const data = JSON.parse(raw);
    const value = data && typeof data === "object" && data.defaultApiBaseUrl
      ? String(data.defaultApiBaseUrl).trim()
      : "";
    return value;
  } catch {
    return "";
  }
}

// Read site display name from root config.json
function readSiteName() {
  try {
    const raw = fs.readFileSync(ROOT_CONFIG_PATH, "utf-8");
    const data = JSON.parse(raw);
    const value = data && typeof data === "object" && data.siteName
      ? String(data.siteName).trim()
      : "";
    return value;
  } catch {
    return "";
  }
}

// Read default model from root config.json, fallback to DEFAULT_MODEL
function readDefaultModel() {
  try {
    const raw = fs.readFileSync(ROOT_CONFIG_PATH, "utf-8");
    const data = JSON.parse(raw);
    const value = data && typeof data === "object" && data.defaultModel
      ? String(data.defaultModel).trim()
      : "";
    return value || DEFAULT_MODEL;
  } catch {
    return DEFAULT_MODEL;
  }
}

// Fetch the model list from the NewAPI site and map it to OpenClaw model definitions
async function fetchSiteModels(baseUrl, apiKey) {
  const url = String(baseUrl || "").replace(/\/+$/, "") + "/models";
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const res = await fetch(url, {
      headers: { Authorization: "Bearer " + apiKey },
      signal: controller.signal,
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    const list = data && Array.isArray(data.data) ? data.data : [];
    return list.map((m) => ({
      id: m.id,
      name: m.id,
      reasoning: /(^|[-_:])r1([-_:]|$)/i.test(String(m.id)),
      input: (m.supported_endpoint_types || []).includes("openai-video")
        ? ["text", "image", "video", "audio"]
        : ["text"],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 128000,
      maxTokens: 32768,
    }));
  } finally {
    clearTimeout(timer);
  }
}

// Order models so the configured default model comes first, others keep site order
function orderModels(models, defaultModel) {
  const list = Array.isArray(models) ? models.slice() : [];
  const idx = list.findIndex((m) => m && m.id === defaultModel);
  if (idx > 0) {
    const [m] = list.splice(idx, 1);
    list.unshift(m);
  }
  return list;
}

// Read default API base URL from root config.json on each request,
// so changing config.json takes effect without restarting the server.
function readDefaultBaseUrl() {
  try {
    const raw = fs.readFileSync(ROOT_CONFIG_PATH, "utf-8");
    const data = JSON.parse(raw);
    const value = data && typeof data === "object" && data.defaultApiBaseUrl
      ? String(data.defaultApiBaseUrl).trim()
      : "";
    return ensureApiV1(value) || DEFAULT_BASE_URL;
  } catch {
    return DEFAULT_BASE_URL;
  }
}

// MIME types for static file serving
const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

function setCORSHeaders(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function readConfig() {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function writeConfig(data) {
  const dir = path.dirname(CONFIG_PATH);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(data, null, 2), "utf-8");
}

function serveStatic(req, res) {
  let filePath = req.url === "/" ? "/index.html" : req.url;
  filePath = path.normalize(filePath).replace(/^(\.\.[\/\\])+/, "");
  const fullPath = path.join(PUBLIC_DIR, filePath);

  if (!fullPath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  const ext = path.extname(fullPath);
  const contentType = MIME_TYPES[ext] || "application/octet-stream";

  try {
    const content = fs.readFileSync(fullPath);
    res.writeHead(200, { "Content-Type": contentType });
    res.end(content);
  } catch {
    res.writeHead(404);
    res.end("Not Found");
  }
}

function handleRequest(req, res) {
  setCORSHeaders(res);

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.url === "/api/config" && req.method === "GET") {
    const config = readConfig();
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(config));
    return;
  }

  if (req.url === "/api/activation-info" && req.method === "GET") {
    const defaultBaseUrl = readDefaultBaseUrl();
    const defaultModel = readDefaultModel();
    let stationUrl = "";
    // Read stationUrl from bootstrap cache
    try {
      const cacheRaw = fs.readFileSync(ACTIVATION_CACHE_PATH, "utf-8");
      const cache = JSON.parse(cacheRaw);
      stationUrl = cache.stationUrl || "";
    } catch {}
    // baseUrl always reflects root config.json (bootstrap syncs it into openclaw.json),
    // so editing config.json takes effect on next page load without a restart.
    const config = readConfig();
    const provider = config.models && config.models.providers && config.models.providers.AIPDD;
    const primaryModel = (provider && config.agents && config.agents.defaults && config.agents.defaults.model &&
      config.agents.defaults.model.primary || "").replace(/^AIPDD\//, "");
    const modelList = (provider && Array.isArray(provider.models))
      ? provider.models.map((m) => m && m.id).filter(Boolean)
      : [];
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({
      stationUrl,
      siteUrl: readSiteUrl(),
      siteName: readSiteName(),
      baseUrl: defaultBaseUrl,
      defaultModel: primaryModel || defaultModel,
      models: modelList,
      available: !!(provider && provider.baseUrl),
    }));
    return;
  }

  if (req.url === "/api/config" && req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", async () => {
      try {
        const data = JSON.parse(body);
        const provider = data.models && data.models.providers && data.models.providers.AIPDD;
        writeConfig(data);
        // Pull the full model list from the site so OpenClaw can switch models.
        // A sync failure never blocks saving. The follow-up write is skipped
        // when the serialized content is unchanged, so saving the config page
        // does not churn openclaw.json (a rewrite racing the gateway startup
        // makes OpenClaw refuse to run its startup migrations).
        let syncError = "";
        if (provider && provider.apiKey && provider.baseUrl) {
          try {
            const before = JSON.stringify(data, null, 2);
            const siteModels = await fetchSiteModels(provider.baseUrl, provider.apiKey);
            if (siteModels.length > 0) {
              provider.models = orderModels(siteModels, readDefaultModel());
              if (JSON.stringify(data, null, 2) !== before) {
                writeConfig(data);
              }
            }
          } catch (err) {
            syncError = err.message;
          }
        }
        res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({
          ok: true,
          models: (provider && Array.isArray(provider.models)) ? provider.models.map((m) => m && m.id).filter(Boolean) : [],
          syncError,
        }));
      } catch (err) {
        res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({ error: "Invalid JSON: " + err.message }));
      }
    });
    return;
  }

  // Gateway waiting page: extension-less alias so /wait serves wait.html.
  if (req.url === "/wait" || req.url === "/wait/") {
    req.url = "/wait.html";
  }

  serveStatic(req, res);
}

function tryListen(port) {
  return new Promise((resolve, reject) => {
    const server = http.createServer(handleRequest);
    server.listen(port, "127.0.0.1", () => {
      resolve({ server, port });
    });
    server.on("error", (err) => {
      if (err.code === "EADDRINUSE") {
        resolve(null);
      } else {
        reject(err);
      }
    });
  });
}

async function main() {
  for (let port = CONFIG_PORT_START; port <= CONFIG_PORT_END; port++) {
    const result = await tryListen(port);
    if (result) {
      console.log(`Config server running at http://127.0.0.1:${result.port}`);
      // The port file lets the launcher discover the actual port. On Windows a
      // stale/transient lock (leftover process, AV scan) can make the write fail
      // with EPERM; the server must keep running anyway, and launchers fall back
      // to the default port when the file is missing or stale.
      try {
        const portFile = path.join(DATA_DIR, ".config-server-port");
        fs.mkdirSync(path.dirname(portFile), { recursive: true });
        fs.writeFileSync(portFile, String(result.port), "utf-8");
      } catch (err) {
        console.warn(`[WARN] Could not write port file: ${err.message}`);
      }
      return;
    }
    console.log(`Port ${port} in use, trying next...`);
  }
  console.error("ERROR: No available port found in range 18788-18798");
  process.exit(1);
}

main().catch((err) => {
  console.error("Config server failed:", err);
  process.exit(1);
});
