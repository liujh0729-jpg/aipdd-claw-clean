import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const text = await readStdin();
let input;
try { input = JSON.parse(text); } catch { fail("stdin must contain valid JSON"); }
if (!input.baseUrl || !input.apiKey || !input.cli) fail("baseUrl, apiKey, and cli are required");
const stateDir = process.env.OPENCLAW_STATE_DIR || process.env.OPENCLAW_HOME;
const target = process.env.MANJU_CONFIG || (stateDir ? path.join(stateDir, "skills", "manju-platform", "config.json") : path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "config.json"));
await fs.mkdir(path.dirname(target), { recursive: true });
await fs.writeFile(target, `${JSON.stringify({ baseUrl: String(input.baseUrl).replace(/\/$/, ""), apiKey: String(input.apiKey), cli: String(input.cli), cliArgs: input.cliArgs || ["--operation", "{operation}", "--input-file", "{inputFile}", "--project-dir", "{projectDir}"], workspaceDir: input.workspaceDir || "" }, null, 2)}\n`, { encoding: "utf8", mode: 0o600 });
console.log(JSON.stringify({ success: true, configPath: target, message: "configuration saved without displaying the API key" }));

async function readStdin() { const chunks = []; for await (const chunk of process.stdin) chunks.push(chunk); return Buffer.concat(chunks).toString("utf8"); }
function fail(message) { console.error(JSON.stringify({ success: false, error: message })); process.exit(1); }
