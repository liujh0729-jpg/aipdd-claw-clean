import { readFileSync, writeFileSync, mkdirSync, existsSync, unlinkSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dirname, "..");

const DEFAULT_API_BASE = null;
const CONFIG_NAME = "config.json";
const SESSION_NAME = "session.json";

function getStateDir() {
  const stateDir = process.env.OPENCLAW_STATE_DIR;
  if (stateDir) return join(stateDir, "skills", "manju-platform");
  const home = process.env.USERPROFILE || process.env.HOME || process.cwd();
  return join(home, ".openclaw", "state", "skills", "manju-platform");
}

function readJson(path) {
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch {
    return null;
  }
}

function writeJson(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(data, null, 2), "utf-8");
}

function loadConfig() {
  const stateDir = getStateDir();
  const stateConfig = readJson(join(stateDir, CONFIG_NAME));
  if (stateConfig && stateConfig.apiBase) return { ...stateConfig, _source: "state" };
  const skillConfig = readJson(join(SKILL_DIR, CONFIG_NAME));
  const exampleConfig = readJson(join(SKILL_DIR, "config.example.json"));
  if (skillConfig?.apiBase) return { ...skillConfig, _source: "skill-config" };
  if (exampleConfig?.apiBase) return { ...exampleConfig, _source: "example-config" };
  return { apiBase: null, _source: "unconfigured" };
}

function saveConfig(config) {
  const stateDir = getStateDir();
  const path = join(stateDir, CONFIG_NAME);
  const toSave = { ...config };
  delete toSave._source;
  delete toSave.password;
  writeJson(path, toSave);
  return path;
}

function loadSession() {
  const stateDir = getStateDir();
  return readJson(join(stateDir, SESSION_NAME));
}

function saveSession(session) {
  const stateDir = getStateDir();
  const path = join(stateDir, SESSION_NAME);
  writeJson(path, session);
  return path;
}

function clearSession() {
  const stateDir = getStateDir();
  const path = join(stateDir, SESSION_NAME);
  if (existsSync(path)) unlinkSync(path);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const key = a.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
    } else {
      args[key] = next;
      i++;
    }
  }
  return args;
}

function maskCookie(cookie) {
  if (!cookie) return "";
  return cookie.slice(0, 16) + "..." + cookie.slice(-8);
}

async function apiFetch({ apiBase, path, method = "GET", body, session, json = true }) {
  const url = `${apiBase.replace(/\/$/, "")}${path.startsWith("/") ? path : "/" + path}`;
  const headers = {
    "Accept": "application/json",
  };
  if (body) headers["Content-Type"] = "application/json";
  if (session?.cookie) headers["Cookie"] = session.cookie;

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const setCookie = res.headers.get("set-cookie");
  const text = await res.text();
  let data;
  if (json) {
    try { data = JSON.parse(text); } catch { data = text; }
  } else {
    data = text;
  }

  return { status: res.status, ok: res.ok, data, setCookie, text };
}

async function cmdConfig(args) {
  const cfg = loadConfig();
  const out = {
    configured: !!(cfg.username && cfg.apiBase),
    apiBase: cfg.apiBase,
    username: cfg.username || null,
    configSource: cfg._source,
    sessionExists: !!loadSession(),
    required: (cfg.apiBase && cfg.username && loadSession()?.cookie) ? [] : [
      ...(cfg.apiBase ? [] : ["apiBase"]),
      ...(cfg.username ? [] : ["username"]),
      ...(loadSession()?.cookie ? [] : ["password"]),
    ],
  };
  console.log(JSON.stringify({ ok: true, command: "config", data: out }, null, 2));
  return 0;
}

async function cmdLogin(args) {
  const cfg = loadConfig();
  const apiBase = args["api-base"] || cfg.apiBase;
  const username = args.username || cfg.username;
  const password = args.password;
  if (!apiBase) {
    console.log(JSON.stringify({ ok: false, error: "missing apiBase" }, null, 2));
    return 2;
  }
  if (!username || !password) {
    console.log(JSON.stringify({ ok: false, error: "missing username or password" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase,
    path: "/api/v1/auth/login",
    method: "POST",
    body: { username, password },
  });
  if (!res.ok || !res.setCookie) {
    console.log(JSON.stringify({
      ok: false,
      command: "login",
      status: res.status,
      error: res.data?.detail || "login failed",
    }, null, 2));
    return 1;
  }
  const cookieName = "st_session";
  const cookieHeader = res.setCookie;
  let stCookie = null;
  for (const part of cookieHeader.split(",")) {
    const trimmed = part.trim();
    if (trimmed.startsWith(cookieName + "=")) {
      stCookie = trimmed.split(";")[0].trim();
      break;
    }
  }
  if (!stCookie) {
    console.log(JSON.stringify({ ok: false, error: "no session cookie in response" }, null, 2));
    return 1;
  }
  const session = {
    cookie: stCookie,
    loggedInAt: new Date().toISOString(),
    apiBase,
    username,
  };
  saveSession(session);
  const newCfg = { apiBase, username };
  const configPath = saveConfig(newCfg);
  console.log(JSON.stringify({
    ok: true,
    command: "login",
    data: {
      username,
      apiBase,
      cookie: maskCookie(stCookie),
      configPath,
    },
  }, null, 2));
  return 0;
}

async function cmdMe(args) {
  const cfg = loadConfig();
  const session = loadSession();
  if (!session?.cookie) {
    console.log(JSON.stringify({ ok: false, error: "not logged in" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: "/api/v1/auth/me",
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "me",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdProjects(args) {
  const cfg = loadConfig();
  const session = loadSession();
  if (!session?.cookie) {
    console.log(JSON.stringify({ ok: false, error: "not logged in" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: "/api/v1/projects",
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "projects",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdPipelineStatus(args) {
  const cfg = loadConfig();
  const session = loadSession();
  const project = args.project;
  const episode = args.episode;
  if (!project || !episode) {
    console.log(JSON.stringify({ ok: false, error: "missing project or episode" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: `/api/v1/projects/${encodeURIComponent(project)}/episodes/${encodeURIComponent(episode)}/pipeline/status`,
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "pipeline-status",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdGenerateScript(args) {
  const cfg = loadConfig();
  const session = loadSession();
  const project = args.project;
  const episode = args.episode;
  const storyPath = args["story-file"];
  const storyPrompt = args["story-text"];
  if (!project || !episode) {
    console.log(JSON.stringify({ ok: false, error: "missing project or episode" }, null, 2));
    return 2;
  }
  let storyText = storyPrompt || "";
  if (storyPath) {
    if (!existsSync(storyPath)) {
      console.log(JSON.stringify({ ok: false, error: "story file not found" }, null, 2));
      return 2;
    }
    storyText = readFileSync(storyPath, "utf-8");
  }
  const body = {};
  if (storyText) body.prompt = storyText;
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: `/api/v1/projects/${encodeURIComponent(project)}/episodes/${encodeURIComponent(episode)}/script/generate`,
    method: "POST",
    body,
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "generate-script",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdPlanScenes(args) {
  const cfg = loadConfig();
  const session = loadSession();
  const project = args.project;
  const episode = args.episode;
  if (!project || !episode) {
    console.log(JSON.stringify({ ok: false, error: "missing project or episode" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: `/api/v1/projects/${encodeURIComponent(project)}/episodes/${encodeURIComponent(episode)}/scenes/plan`,
    method: "POST",
    body: {},
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "plan-scenes",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdPlanProps(args) {
  const cfg = loadConfig();
  const session = loadSession();
  const project = args.project;
  const episode = args.episode;
  if (!project || !episode) {
    console.log(JSON.stringify({ ok: false, error: "missing project or episode" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: `/api/v1/projects/${encodeURIComponent(project)}/episodes/${encodeURIComponent(episode)}/props/plan`,
    method: "POST",
    body: {},
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "plan-props",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdGenerateAudio(args) {
  const cfg = loadConfig();
  const session = loadSession();
  const project = args.project;
  const episode = args.episode;
  if (!project || !episode) {
    console.log(JSON.stringify({ ok: false, error: "missing project or episode" }, null, 2));
    return 2;
  }
  const res = await apiFetch({
    apiBase: cfg.apiBase,
    path: `/api/v1/projects/${encodeURIComponent(project)}/episodes/${encodeURIComponent(episode)}/audio/generate`,
    method: "POST",
    body: {},
    session,
  });
  console.log(JSON.stringify({
    ok: res.ok,
    command: "generate-audio",
    status: res.status,
    data: res.data,
  }, null, 2));
  return res.ok ? 0 : 1;
}

async function cmdWhoAmI(args) {
  const cfg = loadConfig();
  const session = loadSession();
  console.log(JSON.stringify({
    ok: true,
    command: "whoami",
    data: {
      apiBase: cfg.apiBase,
      username: cfg.username || null,
      loggedIn: !!session?.cookie,
      configSource: cfg._source,
    },
  }, null, 2));
  return 0;
}

async function cmdLogout(args) {
  clearSession();
  console.log(JSON.stringify({ ok: true, command: "logout", data: { cleared: true } }, null, 2));
  return 0;
}

async function main() {
  const args = parseArgs(process.argv);
  const command = args._ || args.command || "whoami";
  switch (command) {
    case "config": return cmdConfig(args);
    case "login": return cmdLogin(args);
    case "logout": return cmdLogout(args);
    case "me": return cmdMe(args);
    case "whoami": return cmdWhoAmI(args);
    case "projects": return cmdProjects(args);
    case "pipeline-status": return cmdPipelineStatus(args);
    case "generate-script": return cmdGenerateScript(args);
    case "plan-scenes": return cmdPlanScenes(args);
    case "plan-props": return cmdPlanProps(args);
    case "generate-audio": return cmdGenerateAudio(args);
    default:
      console.log(JSON.stringify({ ok: false, error: `unknown command: ${command}` }, null, 2));
      return 2;
  }
}

main().then((code = 0) => process.exit(code)).catch((err) => {
  console.log(JSON.stringify({ ok: false, error: err.message || String(err) }, null, 2));
  process.exit(1);
});
