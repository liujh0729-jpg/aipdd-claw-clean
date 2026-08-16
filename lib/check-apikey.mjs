// Check if API key is configured in openclaw.json
// Exit 0 = key found, Exit 1 = key missing
import { readFileSync, existsSync } from 'node:fs';

const configPath = process.argv[2];
if (!configPath || !existsSync(configPath)) process.exit(1);

try {
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  const key = config?.models?.providers?.AIPDD?.apiKey;
  if (!key || key.trim() === '') process.exit(1);
  process.exit(0);
} catch {
  process.exit(1);
}
