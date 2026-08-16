#!/usr/bin/env node
// Idempotently patch OpenClaw's SQLite journal-policy resolver so the gateway
// uses rollback (DELETE) journal mode instead of WAL when the data drive is
// FAT32/exFAT.
//
// Why: SQLite WAL relies on -shm/-wal sidecar files. FAT32 cannot support the
// shared-memory semantics they need, so the gateway's state DB write surfaces
// as SQLITE_IOERR ("disk I/O error") and the CLI aborts with "Could not start
// the CLI. Reason: disk I/O error". OpenClaw's resolver (resolvePathJournalPolicy
// in the hash-named dist chunk) treats every Windows drive-letter path as "wal"
// and only falls back to "rollback" for UNC paths, so FAT32 is never detected.
//
// How: the launcher detects the drive filesystem at boot and sets
// OPENCLAW_FORCE_ROLLBACK_JOURNAL=1 for FAT32/exFAT. This script injects an
// env check into resolvePathJournalPolicy() that makes it return "rollback"
// for those volumes, which then routes the DB through PRAGMA journal_mode =
// DELETE (no -wal/-shm sidecars). The dist chunk name is hash-based and changes
// on OpenClaw upgrades, so the chunk is located by scanning for the function's
// source; an already-patched file is skipped and re-patched after upgrades.
//
// Usage: node patch-journal-mode.mjs <openclaw-dist-dir>
import fs from "node:fs";
import path from "node:path";

const MARKER = "// openclaw-fat32-journal-patch";
const ANCHOR = "if (isWindowsDrivePath(normalizedTargetPath)) try {";

function findChunk(distDir) {
  const files = fs.readdirSync(distDir).filter((f) => f.endsWith(".js"));
  for (const file of files) {
    const full = path.join(distDir, file);
    try {
      const src = fs.readFileSync(full, "utf8");
      if (src.includes("function resolvePathJournalPolicy")) return { full, src };
    } catch {}
  }
  return null;
}

const distDir = process.argv[2];
if (!distDir) {
  console.error("Usage: node patch-journal-mode.mjs <openclaw-dist-dir>");
  process.exit(1);
}

const chunk = findChunk(distDir);
if (!chunk) {
  console.error("[patch-journal-mode] resolvePathJournalPolicy not found in dist; is OpenClaw installed?");
  process.exit(1);
}
if (chunk.src.includes(MARKER)) {
  console.log("[patch-journal-mode] already patched.");
  process.exit(0);
}

const idx = chunk.src.indexOf(ANCHOR);
if (idx === -1) {
  console.error(`[patch-journal-mode] anchor not found in ${chunk.full}; OpenClaw version changed?`);
  process.exit(1);
}
const lineStart = chunk.src.lastIndexOf("\n", idx) + 1;
const indent = chunk.src.slice(lineStart, idx); // leading whitespace of the anchor line

// Injected ahead of the original `if (isWindowsDrivePath(...)) try {...}`:
// the guard is a self-contained statement so the function's existing brace
// structure (and the win32-if that closes right after the catch) is untouched.
const injection =
  `${indent}// ${MARKER}: SQLite WAL is unsupported on FAT32/exFAT (SQLITE_IOERR\n` +
  `${indent}// "disk I/O error" on the -shm/-wal sidecars). The launcher sets\n` +
  `${indent}// OPENCLAW_FORCE_ROLLBACK_JOURNAL=1 when the data drive is FAT.\n` +
  `${indent}if (isWindowsDrivePath(normalizedTargetPath) && process.env.OPENCLAW_FORCE_ROLLBACK_JOURNAL === "1") return "rollback";\n` +
  `${indent}if (isWindowsDrivePath(normalizedTargetPath)) try {`;

const out = chunk.src.replace(ANCHOR, injection);
if (out === chunk.src) {
  console.error(`[patch-journal-mode] replacement failed for ${chunk.full}`);
  process.exit(1);
}

try {
  fs.writeFileSync(chunk.full, out, "utf8");
} catch (err) {
  console.error(`[patch-journal-mode] cannot write ${chunk.full}: ${err.message}`);
  process.exit(1);
}
console.log(`[patch-journal-mode] patched ${path.basename(chunk.full)} (rollback journal on FAT drives).`);
