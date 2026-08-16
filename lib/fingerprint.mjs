// Device fingerprint for AiPddClaw activation binding.
// Simplified: uses seed file only (no USB/disk detection).
// Output: { source: 'seed', fingerprint: '<64-hex>' }

import { createHash, randomBytes } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir, platform } from 'node:os';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

function sha256Hex(input) {
  return createHash('sha256').update(input).digest('hex');
}

function getSeedPath(appRoot) {
  if (process.env.AIPDDCLAW_SEED_PATH) {
    return resolve(process.env.AIPDDCLAW_SEED_PATH);
  }
  const home = homedir();
  if (home) return resolve(home, '.aipddclaw', '.usb_seed');
  return resolve(appRoot, '.usb_seed');
}

function readOrCreateSeedFingerprint(appRoot) {
  const seedPath = getSeedPath(appRoot);
  let seedHex;
  if (existsSync(seedPath)) {
    seedHex = readFileSync(seedPath, 'utf8').trim();
  }
  if (!seedHex || !/^[0-9a-f]{64}$/i.test(seedHex)) {
    seedHex = randomBytes(32).toString('hex');
    mkdirSync(dirname(seedPath), { recursive: true });
    writeFileSync(seedPath, seedHex + '\n', 'utf8');
  }
  return { source: 'seed', fingerprint: seedHex.toLowerCase() };
}

let cachedPromise = null;

export async function getFingerprint(appRoot) {
  if (cachedPromise) return cachedPromise;
  cachedPromise = computeFingerprint(appRoot || process.cwd()).catch((err) => {
    cachedPromise = null;
    throw err;
  });
  return cachedPromise;
}

async function computeFingerprint(appRoot) {
  const override = (process.env.AIPDDCLAW_FINGERPRINT_OVERRIDE || '').trim();
  if (override && /^[0-9a-f]{64}$/i.test(override)) {
    return { source: 'test', fingerprint: override.toLowerCase() };
  }
  return readOrCreateSeedFingerprint(appRoot);
}

// CLI entrypoint
const isMain = (() => {
  try {
    if (!process.argv[1]) return false;
    return import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
  } catch {
    return false;
  }
})();

if (isMain) {
  const appRoot = process.env.AIPDDCLAW_APP_ROOT || process.cwd();
  getFingerprint(appRoot)
    .then((result) => {
      process.stdout.write(`${JSON.stringify(result)}\n`);
    })
    .catch((err) => {
      process.stderr.write(`fingerprint error: ${err && err.message ? err.message : err}\n`);
      process.exit(1);
    });
}
