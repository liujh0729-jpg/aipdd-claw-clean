// Activation client for AiPddClaw.
// Reads activation.json, calls activation API to get relay station info.
// Adapted from u-claw's xiapan-client.mjs.

import { existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const DEFAULT_API_BASE = 'https://newapi.aipdd.work/v1';
const DEFAULT_ACTIVATION_BASE = 'https://api.aipdd.work';
const DEFAULT_MODEL = 'deepseek-v4-flash';
const REQUEST_TIMEOUT_MS = 10_000;

function readJsonSafe(filePath) {
  if (!existsSync(filePath)) return null;
  try {
    return JSON.parse(readFileSync(filePath, 'utf8').replace(/^﻿/, ''));
  } catch {
    return null;
  }
}

// Read default API base URL from root config.json, fallback to DEFAULT_API_BASE
function readDefaultApiBase(appRoot) {
  const configPath = appRoot ? join(appRoot, 'config.json') : null;
  const data = configPath ? readJsonSafe(configPath) : null;
  const value = data && typeof data === 'object' && data.defaultApiBaseUrl
    ? String(data.defaultApiBaseUrl).trim()
    : DEFAULT_API_BASE;
  return ensureApiV1(value);
}

// Read default model from root config.json, fallback to DEFAULT_MODEL
function readDefaultModel(appRoot) {
  const configPath = appRoot ? join(appRoot, 'config.json') : null;
  const data = configPath ? readJsonSafe(configPath) : null;
  const value = data && typeof data === 'object' && data.defaultModel
    ? String(data.defaultModel).trim()
    : DEFAULT_MODEL;
  return value;
}

async function fetchWithTimeout(url, init) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

export function normalizeApiBaseUrl(value) {
  let base = String(value || DEFAULT_API_BASE).trim().replace(/\/+$/, '');
  base = base.replace(/\/chat\/completions$/i, '');
  if (!/\/v1$/i.test(base) && /\/v1\//i.test(base)) {
    base = base.replace(/\/v1\/.*$/i, '/v1');
  }
  return base;
}

// Append /v1 when the value is a bare site domain (no path); keep it unchanged
// if it already ends with /v1 or carries another path (e.g. /api/v3).
function ensureApiV1(url) {
  const base = String(url || '').trim().replace(/\/+$/, '');
  if (!base || /\/v1$/i.test(base)) return base;
  const path = base.replace(/^[a-z][a-z0-9+.+-]*:\/\/[^/]+/i, '');
  return path ? base : base + '/v1';
}

export function getActivationConfig(appRoot) {
  const fileCandidates = [];
  if (process.env.AIPDDCLAW_ACTIVATION_CONFIG) {
    fileCandidates.push(resolve(process.env.AIPDDCLAW_ACTIVATION_CONFIG));
  }
  if (appRoot) {
    fileCandidates.push(join(appRoot, 'activation.json'));
  }

  let fileConfig = {};
  for (const filePath of fileCandidates) {
    const data = readJsonSafe(filePath);
    if (data && typeof data === 'object') {
      fileConfig = data;
      break;
    }
  }

  const activationBaseUrl = (
    process.env.AIPDDCLAW_ACTIVATION_BASE_URL
    || fileConfig.activationBaseUrl
    || DEFAULT_ACTIVATION_BASE
  ).trim().replace(/\/+$/, '');
  const activationCode = (
    process.env.AIPDDCLAW_ACTIVATION_CODE
    || fileConfig.activationCode
    || ''
  ).trim();
  const apiBaseUrl = normalizeApiBaseUrl(
    process.env.AIPDDCLAW_API_BASE_URL
    || fileConfig.apiBaseUrl
    || fileConfig.baseUrl
    || readDefaultApiBase(appRoot)
  );
  const defaultModel = (
    process.env.AIPDDCLAW_DEFAULT_MODEL
    || fileConfig.defaultModel
    || fileConfig.model
    || readDefaultModel(appRoot)
  ).trim();

  if (!activationBaseUrl || !activationCode) {
    return {
      enabled: false,
      activationBaseUrl,
      activationCode,
      apiBaseUrl,
      defaultModel,
      source: activationBaseUrl || activationCode ? 'partial' : 'none',
    };
  }

  return {
    enabled: true,
    activationBaseUrl,
    activationCode,
    apiBaseUrl,
    defaultModel,
    source: fileCandidates.some((filePath) => existsSync(filePath)) ? 'file' : 'env',
  };
}

export async function activateDevice(fingerprintInfo, { appRoot } = {}) {
  const activation = getActivationConfig(appRoot);
  if (!activation.enabled) return null;

  const response = await fetchWithTimeout(`${activation.activationBaseUrl}/uclaw/activate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      fingerprint: fingerprintInfo.fingerprint,
      source: fingerprintInfo.source,
      activationCode: activation.activationCode,
    }),
  });

  let payload = {};
  try {
    payload = await response.json();
  } catch {
    // keep payload empty
  }

  if (!response.ok || (payload.code && payload.code !== 200 && payload.code !== 0)) {
    const message = payload.message || `activation HTTP ${response.status}`;
    throw new Error(message);
  }

  const data = payload.data || payload;
  if (!data || !data.baseUrl) {
    throw new Error('activation response must include baseUrl.');
  }
  return {
    stationUrl: data.stationUrl || '',
    baseUrl: normalizeApiBaseUrl(data.baseUrl),
    primaryModel: data.primaryModel || data.model || readDefaultModel(appRoot),
    providerId: data.providerId || 'AIPDD',
    activationCode: data.activationCode || activation.activationCode,
  };
}
