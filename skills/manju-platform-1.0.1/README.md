> **EN:** Standalone OpenClaw skill; copy the whole directory into OpenClaw's workspace/skills to use.
>
# manju-platform

独立的 OpenClaw Skill。复制整个目录到 OpenClaw 的 `workspace/skills` 下即可使用。

需要用户提供漫剧平台 CLI 的实际命令格式。默认脚本按以下 JSON CLI 协议调用：

```text
manju-cli --operation <operation> --input-file <json-file> --project-dir <project-dir>
```

如果实际 CLI 参数不同，请修改 `config.json` 中的 `cli` 和 `cliArgs`。不要把真实 API Key 写入 Skill 仓库。
