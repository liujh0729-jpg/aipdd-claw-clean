// Repair the OpenClaw SQLite databases before the gateway starts.
//
// The state/agent DBs run in WAL mode. After an unclean shutdown (forced kill
// or crash) the -wal/-shm sidecar files go stale. NTFS rebuilds the wal-index
// transparently on the next open, but a FAT32 USB stick cannot, and SQLite
// then fails with "disk I/O error", aborting the gateway with
// "Could not start the CLI". Since no gateway holds the DBs when this runs,
// we can safely checkpoint any pending WAL frames into the main DB (no data
// loss) and close in DELETE journal mode, which removes the sidecars. If a
// stale -shm blocks even opening, drop it first (it is only an index and is
// rebuilt from the -wal), retry, and only as a last resort delete both
// sidecars -- the main DB file alone passes integrity checks.
//
// Usage: node cleanup-state-db.mjs <OPENCLAW_STATE_DIR>
import { existsSync, readdirSync, rmSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';

const stateDir = process.argv[2];
if (!stateDir) process.exit(0);

// Remove a sidecar with retries: on a flaky FAT32 stick a deletion can hit a
// transient I/O error (or a short-lived lock from a just-killed process).
function removeWithRetry(p, attempts = 3) {
  for (let i = 0; i < attempts; i++) {
    try {
      rmSync(p);
      return true;
    } catch (err) {
      if (i === attempts - 1) {
        console.log(`[cleanup] could not remove ${path.basename(p)}: ${err.message}`);
        return false;
      }
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 250);
    }
  }
  return false;
}

// Collect every SQLite DB under the state dir (state/openclaw.sqlite, the
// agent DBs, etc.) so a stale sidecar in any of them cannot abort the gateway.
function findDatabases(dir) {
  const dbs = [];
  const walk = (p) => {
    let entries;
    try {
      entries = readdirSync(p, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = path.join(p, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.sqlite')) dbs.push(full);
    }
  };
  walk(dir);
  return dbs;
}

function openDb(dbPath) {
  const db = new DatabaseSync(dbPath);
  db.exec('PRAGMA busy_timeout = 5000;');
  return db;
}

// Checkpoint pending WAL frames into the main DB, then leave DELETE journal
// mode; closing afterwards removes the -wal/-shm sidecars cleanly.
function checkpointAndClose(db) {
  try {
    db.exec('PRAGMA wal_checkpoint(TRUNCATE);');
  } catch {}
  try {
    db.exec('PRAGMA journal_mode = DELETE;');
  } catch {}
  db.close();
}

function cleanDatabase(dbPath) {
  const shmPath = dbPath + '-shm';
  const walPath = dbPath + '-wal';
  let db;
  try {
    db = openDb(dbPath);
    checkpointAndClose(db);
    return 'clean';
  } catch {
    // Stale -shm (FAT32 cannot rebuild it): drop the index, not the data, then
    // retry the open -- a flaky stick can fail once and succeed on a retry.
    if (existsSync(shmPath)) {
      removeWithRetry(shmPath);
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          db = openDb(dbPath);
          checkpointAndClose(db);
          return 'clean (after -shm reset)';
        } catch {}
      }
    }
    // Last resort: the -wal is unusable too; the main DB alone is consistent.
    if (existsSync(shmPath)) removeWithRetry(shmPath);
    if (existsSync(walPath)) {
      if (removeWithRetry(walPath)) return 'sidecars removed';
      return 'could not remove sidecars';
    }
    return 'still failing to open';
  }
}

for (const dbPath of findDatabases(stateDir)) {
  const status = cleanDatabase(dbPath);
  if (status) console.log(`${path.relative(stateDir, dbPath)}: ${status}`);
}
process.exit(0);
