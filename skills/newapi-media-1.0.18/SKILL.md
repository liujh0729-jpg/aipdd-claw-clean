---
name: newapi-media
version: 1.0.0
description: >
  Multimodal media generation and chat via the user-configured NewAPI relay:
  text-to-image, image-to-image, text-to-video, image-to-video, TTS audio and
  AI chat. Use when the user wants to generate images, videos, audio or run
  multi-turn conversations and already has their own NewAPI relay service.
  通过用户配置的 NewAPI 服务地址和密钥调用多模态模型，支持文生图、图生图、文生视频、图生视频、语音合成以及 AI 对话功能。当用户需要生成图片、视频、音频或进行多轮对话，并且已有自建的 NewAPI 中转服务时使用此技能。
---

# NewAPI Media

A multimodal media generation and chat Skill for user-hosted NewAPI relay services. Only call the service address the user configured — never guess addresses, models, or parameters.

面向用户自建 NewAPI 服务的多模态媒体生成与对话 Skill。只调用用户配置的服务地址，不猜测地址、模型或参数。

## Configuration / 配置流程

1. The user must provide the NewAPI service URL and API Key before first use. / 首次使用前需要用户提供 NewAPI 服务地址和 API Key。
2. Never echo the API Key into the conversation, logs, or final reports. / 不要将 API Key 回显到对话、日志或最终报告中。
3. Environment variables are supported: `NEWAPI_BASE_URL` and `NEWAPI_API_KEY`. / 支持通过环境变量配置：NEWAPI_BASE_URL 和 NEWAPI_API_KEY。

Configuration is done by running `scripts/configure.js` via stdin; never pass the key as a command-line argument. 配置通过标准输入调用 scripts/configure.js 脚本完成，不要把密钥放在命令行参数中。

## Call Rules / 调用规则

- Use the model the user explicitly specified. / 用户明确指定模型时必须使用指定模型。
- If no model is specified, ask the user which model to pick first; never silently select a paid model. / 用户没有指定模型时，先询问用户选择哪个模型，不要静默选择收费模型。
- Image-to-image, image-to-video, and audio references require HTTPS URLs. / 图生图、图生视频、音频参考需要使用 HTTPS URL 地址。
- Video and audio generation are async tasks: poll until completion and never claim success before the task finishes. / 视频和音频生成是异步任务，需要轮询等待完成，不能在任务未完成时声称成功。
- Report status, the model used, and the result URL. / 生成结果需要报告状态、使用的模型和结果 URL。
- On upstream failures keep the original error message; do not auto-switch models and retry. / 上游服务失败时保留原始错误信息，不要自动换模型重试。

## Using the Scripts / 使用脚本

Generic invocation format / 通用调用格式：

```bash
node scripts/invoke.js --type image --prompt "prompt" --model "model-name"
node scripts/invoke.js --type video --prompt "prompt" --model "model-name" --duration 5 --ratio "16:9"
node scripts/invoke.js --type audio --input "text content" --model "model-name"
node scripts/invoke.js --type chat --input "chat content" --model "model-name"
```

Optional flags / 可选参数：`--image`, `--audio-url`, `--video-url`, `--size`, `--duration`, `--ratio`, `--poll-seconds`, `--timeout-seconds`.

Scripts output JSON only. Convert the `status`, `url`, and `error` fields into a concise reply for the user (in the language of the conversation).

脚本只输出 JSON 格式结果。将 JSON 中的 status、url、error 字段转换为简洁的回复给用户（使用当前对话语言）。
