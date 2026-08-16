import fs from "node:fs/promises";

const args = parseArgs(process.argv.slice(2));
const type = args.type;
if (!["image", "video", "audio", "chat"].includes(type)) fail("type must be image, video, audio, or chat");

const config = await loadConfig();
let baseUrl = String(config.baseUrl || "").replace(/\/$/, "");
if (!/\/v\d+$/.test(baseUrl)) baseUrl = baseUrl + "/v1";
const apiKey = config.apiKey || process.env.NEWAPI_API_KEY || "";
if (!baseUrl) fail("missing base URL");
if (!apiKey) fail("missing API key");

const body = buildBody(type, args);
const endpoint = endpointFor(type);
const initial = await request(baseUrl + endpoint, apiKey, body);
const result = await waitForResult(initial, type, baseUrl, apiKey, Number(config.pollSeconds || 10), Number(config.timeoutSeconds || 900));
console.log(JSON.stringify(result));

function parseArgs(values) {
  const output = {};
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith("--")) continue;
    const key = value.slice(2).replaceAll("-", "_");
    output[key] = values[index + 1]?.startsWith("--") ? true : values[index + 1] ?? true;
    if (output[key] !== true) index += 1;
  }
  return output;
}

async function loadConfig() {
  const configPath = defaultConfigPath("newapi-media");
  let config = {};
  try { config = JSON.parse(await fs.readFile(configPath, "utf8")); } catch (error) {}
  return {
    baseUrl: config.baseUrl || process.env.NEWAPI_BASE_URL,
    apiKey: config.apiKey || process.env.NEWAPI_API_KEY,
    pollSeconds: config.pollSeconds,
    timeoutSeconds: config.timeoutSeconds,
  };
}

function defaultConfigPath(skillName) {
  const stateDir = process.env.OPENCLAW_STATE_DIR || process.env.OPENCLAW_HOME;
  return stateDir ? stateDir + "/skills/" + skillName + "/config.json" : new URL("../config.json", import.meta.url);
}

function buildBody(kind, input) {
  const body = { model: input.model, prompt: input.prompt, input: input.input };
  if (input.image) body.image = input.image;
  if (input.audio_url) body.audio_url = input.audio_url;
  if (input.video_url) body.video_url = input.video_url;
  if (input.size) body.size = input.size;
  if (input.duration) body.duration = Number(input.duration);
  if (input.ratio) body.metadata = { ratio: input.ratio };
  if (kind === "chat") return { model: input.model, messages: [{ role: "user", content: input.input || input.prompt || "" }] };
  if (!body.model) delete body.model;
  if (!body.prompt) delete body.prompt;
  if (!body.input) delete body.input;
  return body;
}

function endpointFor(kind) {
  return { image: "/images/generations", video: "/videos", audio: "/audio/speech", chat: "/chat/completions" }[kind];
}

async function request(url, key, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "authorization": "Bearer " + key,
      "content-type": "application/json"
    },
    body: JSON.stringify(body)
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!response.ok) fail("HTTP error: " + response.status);
  return data;
}

async function waitForResult(initial, kind, baseUrl, key, pollSeconds, timeoutSeconds) {
  if (kind === "chat") return { success: true, status: "completed", type: kind, data: initial };
  const taskId = initial.id || initial.task_id || initial.data?.id || initial.data?.task_id;
  const immediateUrl = findUrl(initial);
  if (immediateUrl) return { success: true, status: "completed", type: kind, url: immediateUrl, data: initial };
  if (!taskId) return { success: true, status: "completed", type: kind, data: initial };
  const path = kind === "video" ? "/v1/videos/" + taskId : kind === "audio" ? "/v1/audio/speech/" + taskId : "/v1/images/generations/" + taskId;
  const deadline = Date.now() + timeoutSeconds * 1000;
  while (Date.now() < deadline) {
    await new Promise(resolve => setTimeout(resolve, pollSeconds * 1000));
    const data = await get(baseUrl + path, key);
    const status = String(data.status || data.data?.status || "").toLowerCase();
    if (["failed", "error", "cancelled"].includes(status)) fail("task failed");
    const url = findUrl(data);
    if (url || ["succeeded", "completed"].includes(status)) return { success: true, status: status || "completed", type: kind, taskId, url, data };
  }
  fail("task timed out");
}

async function get(url, key) {
  const response = await fetch(url, { headers: { "authorization": "Bearer " + key } });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!response.ok) fail("HTTP error: " + response.status);
  return data;
}

function findUrl(value) {
  const candidates = [value.url, value.data?.url, value.data?.[0]?.url, value.output?.[0], value.metadata?.url, value.metadata?.urls?.[0], value.choices?.[0]?.message?.content];
  for (const item of candidates) {
    if (typeof item === "string" && item.startsWith("http")) return item;
  }
  return null;
}

function fail(message) { console.error(JSON.stringify({ success: false, error: message })); process.exit(1); }
