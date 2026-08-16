// Bootstrap: read activation.json, call activation API, inject AIPDD provider
// baseUrl and defaultModel into openclaw.json.
// Does NOT write apiKey — user provides it via config page.
// Caches stationUrl for config-server to serve to the frontend.

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { getFingerprint } from './fingerprint.mjs';
import { activateDevice, getActivationConfig, normalizeApiBaseUrl } from './activation-client.mjs';

const PROVIDER_ID = 'AIPDD';

const DEFAULT_PROVIDER_TEMPLATE = {
  baseUrl: 'https://newapi.aipdd.work/v1',
  api: 'openai-completions',
  models: [
    {
      id: 'deepseek-v4-flash',
      name: 'deepseek-v4-flash',
      reasoning: false,
      input: ['text', 'image', 'video', 'audio'],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 128000,
      maxTokens: 32768,
    },
  ],
};

const DEFAULT_PRIMARY_MODEL = `${PROVIDER_ID}/deepseek-v4-flash`;

function readJsonSafe(filePath) {
  if (!existsSync(filePath)) return null;
  try {
    const raw = readFileSync(filePath, 'utf8').replace(/^﻿/, '');
    return JSON.parse(raw);
  } catch (err) {
    process.stderr.write(`[bootstrap-activation] Cannot parse ${filePath}: ${err.message}\n`);
    return null;
  }
}

// Fetch the model list from the NewAPI site and map it to OpenClaw model definitions
async function fetchSiteModels(baseUrl, apiKey) {
  const url = String(baseUrl || '').replace(/\/+$/, '') + '/models';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(url, {
      headers: { Authorization: 'Bearer ' + apiKey },
      signal: controller.signal,
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    const list = data && Array.isArray(data.data) ? data.data : [];
    return list.map((m) => ({
      id: m.id,
      name: m.id,
      reasoning: /(^|[-_:])r1([-_:]|$)/i.test(String(m.id)),
      input: (m.supported_endpoint_types || []).includes('openai-video')
        ? ['text', 'image', 'video', 'audio']
        : ['text'],
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

// Append /v1 when the value is a bare site domain (no path); keep it unchanged
// if it already ends with /v1 or carries another path (e.g. /api/v3).
function ensureApiV1(url) {
  const base = String(url || '').trim().replace(/\/+$/, '');
  if (!base || /\/v1$/i.test(base)) return base;
  const path = base.replace(/^[a-z][a-z0-9+.+-]*:\/\/[^/]+/i, '');
  return path ? base : base + '/v1';
}

function writeJson(filePath, data) {
  writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

// Write openclaw.json only when the serialized content actually differs.
// Rewriting the file on every launch (even when nothing changed) churns the
// config mtime/hash; OpenClaw refuses to run gateway startup migrations when it
// detects the config changed between its startup snapshot and migration check,
// so an unnecessary rewrite can race the gateway boot.
// Note: no trailing newline, matching OpenClaw's canonical config format.
function writeConfigIfChanged(filePath, data) {
  const next = JSON.stringify(data, null, 2);
  try {
    if (existsSync(filePath) && readFileSync(filePath, 'utf8') === next) {
      return false;
    }
  } catch {
    // fall through to a full write
  }
  writeFileSync(filePath, next, 'utf8');
  return true;
}

// Point skills.load.extraDirs at this app's portable skills/ folder. A value
// persisted from another platform (e.g. a macOS U盘 path) or a stale location
// is dropped so skills load correctly wherever the launcher runs.
// On Windows, path comparison is case-insensitive: the launcher may be invoked
// with a different drive-letter case (H:\ vs h:\) between runs, and a
// case-sensitive comparison would re-add the same directory every time,
// rewriting openclaw.json on each launch and racing the gateway's config
// snapshot guard. Duplicate entries are also collapsed.
function ensureSkillsDirs(config, root) {
  const skillsDir = resolve(root, 'skills');
  if (!config.skills || typeof config.skills !== 'object') config.skills = {};
  if (!config.skills.load || typeof config.skills.load !== 'object') config.skills.load = {};
  const existing = Array.isArray(config.skills.load.extraDirs) ? config.skills.load.extraDirs : [];
  const normPath = (p) => (process.platform === 'win32' ? resolve(p).toLowerCase() : resolve(p));
  const valid = [];
  const seen = new Set();
  for (const d of existing) {
    if (typeof d !== 'string' || !d || !existsSync(d)) continue;
    const key = normPath(d);
    if (seen.has(key)) continue;
    seen.add(key);
    valid.push(d);
  }
  if (!valid.some((d) => normPath(d) === normPath(skillsDir))) {
    config.skills.load.extraDirs = [skillsDir, ...valid];
  } else {
    config.skills.load.extraDirs = valid;
  }
  if (config.skills.load.watch !== false) config.skills.load.watch = true;
}

function ensureModelsContainer(config) {
  if (!config.models || typeof config.models !== 'object') {
    config.models = { mode: 'merge', providers: {} };
  }
  if (!config.models.mode) config.models.mode = 'merge';
  if (!config.models.pricing || typeof config.models.pricing !== 'object') {
    config.models.pricing = {};
  }
  config.models.pricing.enabled = false;
  if (!config.models.providers || typeof config.models.providers !== 'object') {
    config.models.providers = {};
  }
  return config.models.providers;
}

function ensureAgentsDefaults(config, primaryModel = DEFAULT_PRIMARY_MODEL) {
  if (!config.agents || typeof config.agents !== 'object') {
    config.agents = {};
  }
  if (!config.agents.defaults || typeof config.agents.defaults !== 'object') {
    config.agents.defaults = {};
  }
  const defaults = config.agents.defaults;
  if (!defaults.model || typeof defaults.model !== 'object') {
    defaults.model = {};
  }
  if (!defaults.model.primary || (
    defaults.model.primary.startsWith(`${PROVIDER_ID}/`) && defaults.model.primary !== primaryModel
  )) {
    defaults.model.primary = primaryModel;
    return true;
  }
  return false;
}

export async function bootstrapActivation({ configPath, appRoot, log = console } = {}) {
  if (!configPath) {
    throw new Error('bootstrapActivation: configPath is required.');
  }
  const root = appRoot || process.cwd();

  let fingerprintInfo;
  try {
    fingerprintInfo = await getFingerprint(root);
  } catch (err) {
    log.warn?.(`[bootstrap-activation] Fingerprint detection failed: ${err.message}`);
    return { ok: false, reason: 'fingerprint-failed' };
  }

  const activationConfig = getActivationConfig(root);
  // Read default API base URL and model from root config.json, fallback to template defaults
  const configData = readJsonSafe(resolve(root, 'config.json'));
  const defaultApiBase = (configData && typeof configData === 'object' && configData.defaultApiBaseUrl)
    ? ensureApiV1(String(configData.defaultApiBaseUrl).trim())
    : DEFAULT_PROVIDER_TEMPLATE.baseUrl;
  const defaultModel = (configData && typeof configData === 'object' && configData.defaultModel)
    ? String(configData.defaultModel).trim()
    : DEFAULT_PRIMARY_MODEL.replace(`${PROVIDER_ID}/`, '');
  let baseUrl = normalizeApiBaseUrl(activationConfig.apiBaseUrl || defaultApiBase);
  let primaryModel = `${PROVIDER_ID}/${activationConfig.defaultModel || defaultModel}`;
  let stationUrl = '';
  let activationMode = 'local';

  if (activationConfig.enabled) {
    try {
      const activationResult = await activateDevice(fingerprintInfo, { appRoot: root });
      baseUrl = normalizeApiBaseUrl(activationResult.baseUrl);
      primaryModel = `${PROVIDER_ID}/${activationResult.primaryModel}`;
      stationUrl = activationResult.stationUrl || '';
      activationMode = 'remote';
    } catch (err) {
      log.warn?.(`[bootstrap-activation] Remote activation failed: ${err.message}. Falling back to local config.`);
    }
  } else if (activationConfig.source === 'partial') {
    log.warn?.('[bootstrap-activation] Activation config is incomplete. Need activationBaseUrl and activationCode.');
  }

  // Cache stationUrl for config-server to read
  const cachePath = resolve(dirname(configPath), 'activation-cache.json');
  writeJson(cachePath, { stationUrl, baseUrl, defaultModel: primaryModel.replace(`${PROVIDER_ID}/`, ''), activationMode });

  const config = readJsonSafe(configPath) || { gateway: { mode: 'local', auth: { token: 'aipddclaw' } } };
  const providers = ensureModelsContainer(config);
  const existing = providers[PROVIDER_ID];

  // Update or create AIPDD provider (preserve existing apiKey if user set one)
  if (existing && typeof existing === 'object') {
    const normalizedBaseUrl = normalizeApiBaseUrl(baseUrl);
    if (existing.baseUrl !== normalizedBaseUrl) {
      existing.baseUrl = normalizedBaseUrl;
    }
    if (!Array.isArray(existing.models) || existing.models.length === 0) {
      existing.models = DEFAULT_PROVIDER_TEMPLATE.models;
    } else if (existing.models[0] && existing.models[0].id !== defaultModel) {
      // Sync the first declared model with the configured default model
      existing.models[0] = { ...DEFAULT_PROVIDER_TEMPLATE.models[0], id: defaultModel, name: defaultModel };
    }
  } else {
    providers[PROVIDER_ID] = {
      ...DEFAULT_PROVIDER_TEMPLATE,
      baseUrl: normalizeApiBaseUrl(baseUrl),
    };
    if (defaultModel !== DEFAULT_PROVIDER_TEMPLATE.models[0].id) {
      providers[PROVIDER_ID].models = [{ ...DEFAULT_PROVIDER_TEMPLATE.models[0], id: defaultModel, name: defaultModel }];
    }
  }

  // Pull the full model list from the site when an API key exists, so OpenClaw
  // can switch between all available models. A sync failure keeps current models.
  const aipddProvider = providers[PROVIDER_ID];
  if (aipddProvider && aipddProvider.apiKey && aipddProvider.baseUrl) {
    try {
      const siteModels = await fetchSiteModels(aipddProvider.baseUrl, aipddProvider.apiKey);
      if (siteModels.length > 0) {
        aipddProvider.models = orderModels(siteModels, defaultModel);
        if (!aipddProvider.models.some((m) => m && m.id === defaultModel)) {
          const fallback = aipddProvider.models[0] && aipddProvider.models[0].id;
          log.warn?.(`[bootstrap-activation] Default model "${defaultModel}" not found on site; using "${fallback}"`);
          primaryModel = `${PROVIDER_ID}/${fallback}`;
        }
      }
    } catch (err) {
      log.warn?.(`[bootstrap-activation] Model list sync failed: ${err.message}`);
    }
  }
  const changedDefaults = ensureAgentsDefaults(config, primaryModel);
  ensureSkillsDirs(config, root);

  const wrote = writeConfigIfChanged(configPath, config);
  log.info?.(
    `[bootstrap-activation] Wrote AIPDD provider (mode=${activationMode}, baseUrl=${baseUrl})${wrote ? '' : ' [unchanged]'}`,
  );
  return {
    ok: true,
    action: 'updated',
    source: fingerprintInfo.source,
    activationMode,
    stationUrl,
    baseUrl,
    model: primaryModel,
  };
}

// CLI entrypoint
import { pathToFileURL } from 'node:url';
const isMain = (() => {
  try {
    if (!process.argv[1]) return false;
    return import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
  } catch {
    return false;
  }
})();

if (isMain) {
  const configPath = process.argv[2] || process.env.AIPDDCLAW_CONFIG_PATH;
  if (!configPath) {
    process.stderr.write('Usage: node bootstrap-activation.mjs <openclaw.json path>\n');
    process.exit(2);
  }
  const appRoot = process.env.AIPDDCLAW_APP_ROOT || resolve(configPath, '../../..');
  bootstrapActivation({ configPath, appRoot })
    .then((res) => {
      process.stdout.write(`${JSON.stringify(res)}\n`);
    })
    .catch((err) => {
      process.stderr.write(`bootstrap-activation error: ${err.message}\n`);
      process.exit(1);
    });
}
