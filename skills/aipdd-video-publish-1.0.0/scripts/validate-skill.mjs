#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const requiredFiles = [
  "SKILL.md",
  "README.md",
  "agents/openai.yaml",
  "references/environment.md",
  "references/configuration.md",
  "references/scripts.md",
  "scripts/config.mjs",
  "scripts/check-package.mjs",
  "scripts/run-safe-platforms.sh",
  "scripts/v2/publisher.mjs",
];
const errors = [];
const warnings = [];

for (const relativePath of requiredFiles) {
  const target = path.join(skillRoot, relativePath);
  if (!fs.existsSync(target) || !fs.statSync(target).isFile()) {
    errors.push(`缺少必要文件：${relativePath}`);
  }
}

const skillPath = path.join(skillRoot, "SKILL.md");
if (fs.existsSync(skillPath)) {
  const source = fs.readFileSync(skillPath, "utf8");
  const frontmatter = source.match(/^---\n([\s\S]*?)\n---\n/);
  if (!frontmatter) {
    errors.push("SKILL.md 缺少 YAML frontmatter");
  } else {
    if (!/^name:\s*video-publisher\s*$/m.test(frontmatter[1])) {
      errors.push("SKILL.md 的 name 必须是 video-publisher");
    }
    const description = frontmatter[1].match(/^description:\s*(.+)$/m)?.[1]?.trim();
    if (!description) errors.push("SKILL.md 缺少 description");
    else {
      if (!description.includes("Ego Lite")) warnings.push("description 建议明确提到 Ego Lite");
      if (!/Codex|Claude Code/.test(description)) warnings.push("description 建议明确适用的宿主 Agent");
      if (!/发布|上传|草稿/.test(description)) warnings.push("description 建议包含清晰的触发场景");
    }
  }
  if (!source.includes("最终发布")) warnings.push("主说明建议明确最终发布安全边界");
  if (!source.includes("references/environment.md")) warnings.push("主说明建议链接运行环境文档");
}

function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolutePath = path.join(directory, entry.name);
    const relativePath = path.relative(skillRoot, absolutePath);
    if (entry.name === "__MACOSX" || entry.name.startsWith("._")) {
      warnings.push(`发现 macOS 压缩包元数据，分享前应移除：${relativePath}`);
    }
    if (entry.isDirectory()) walk(absolutePath);
  }
}
walk(skillRoot);

const result = {
  ok: errors.length === 0,
  skillRoot,
  errors,
  warnings,
};
console.log(JSON.stringify(result, null, 2));
process.exitCode = errors.length ? 1 : 0;
