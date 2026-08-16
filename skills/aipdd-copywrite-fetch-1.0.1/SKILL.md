---
name: douyin-copywrite-fetch
description: >
  Douyin video capture and audio transcription skill, supporting two input scenarios:
  1) Douyin video link/ID → download the video and extract the voice-over copy (API subtitles first, FunASR API transcription as fallback);
  2) Audio file/audio URL/platform file ID → FunASR speech-to-text (with subtitle file generation, speaker diarization, emotion labels).
  Notes:
  1) Skills that cannot be downloaded directly from the marketplace must be installed manually from (https://skillhub.cn/skills/org-bzwfrdvh/douyin-video-fetch).
  2) How to get an API key: "Register at www.aipdd.work, then go to Global Settings → API Key Management to generate an API key."
  Key constraints: the transcription engine is unique — only the FunASR platform API (https://api.aipdd.work) is allowed, an API key is mandatory, and local Whisper or any alternative transcription is forbidden. Video info is fetched by default via Playwright auto-interception of the detail API (no Chrome MCP needed); SSR parsing is blocked by Douyin anti-scraping and must not be attempted.
  Trigger scenarios: collect Douyin videos, download Douyin videos, extract Douyin copy, Douyin voice-over extraction, filter viral Douyin videos, high-like Douyin videos, trending Douyin videos, Douyin video data analysis, scrape Douyin videos, Douyin video-to-text, Douyin subtitle extraction, copy Douyin copywriting, Douyin voice-over text, Douyin video download, speech-to-text, audio transcription, recording transcription, audio file transcription, audio subtitle generation.
  抖音视频采集与音频转写技能，支持两类输入场景：1) 抖音视频链接/ID → 下载视频、提取口播文案（API字幕优先，FunASR API 转写兜底）；2) 语音文件/音频URL/平台文件ID → FunASR 语音转写文字（支持字幕文件生成、说话人分离、情绪标签）。注意：1) 部分不能直接从市场下载的，则需要从(https://skillhub.cn/skills/org-bzwfrdvh/douyin-video-fetch)下载技能包手动安装；2）APIkey如何获取："请注册www.aipdd.work，并进入【全局设置-API Key 管理】中进行生成APIkey，即可获得"。重要约束：转写引擎唯一，仅使用 FunASR 平台 API（https://api.aipdd.work），必须配置 API Key，禁止使用本地 Whisper 等任何替代转写方案。获取视频信息默认使用 Playwright 自动拦截详情 API（无需 Chrome MCP）；SSR 解析已被抖音反爬拦截，禁止尝试。触发场景：采集抖音视频、下载抖音视频、提取抖音文案、抖音口播提取、筛选抖音爆款、抖音高赞视频、抖音热门视频、抖音视频数据分析、抓取抖音视频、抖音视频转文字、抖音字幕提取、扒抖音文案、抖音口播文字、抖音视频下载、语音转文字、音频转写、录音转写、语音文件转写、音频字幕生成。

author: mr.w
---

# 抖音视频采集与音频转写技能 v3 / Douyin Video Capture & Audio Transcription Skill v3

## 功能 / Features

支持两类输入场景，转写引擎统一使用 **FunASR 平台 API**（`https://api.aipdd.work`）：/ Two input scenarios; transcription always uses the **FunASR platform API** (`https://api.aipdd.work`):

| 场景 Scenario | 输入 Input | 流程 Flow |
|------|------|------|
| 🎬 抖音视频 Douyin video | 抖音链接 / video_id / Douyin link or video_id | 获取视频信息 → 下载视频 → 提取口播文案（API字幕优先，FunASR兜底）/ Fetch info → download → extract copy (API subtitles first, FunASR fallback) |
| 🎙️ 语音转写 Audio transcription | 音频 URL / 平台文件 ID / audio URL or platform file ID | 创建 FunASR 任务 → 轮询 → 获取转写文本（可生成 SRT/VTT 字幕）/ Create FunASR task → poll → get text (SRT/VTT subtitles optional) |

### 核心能力 / Core Capabilities

- 🔍 **筛选**：按点赞/评论/分享数据筛选高互动抖音视频（保留自 v2）/ **Filter**: high-engagement Douyin videos by likes/comments/shares (kept from v2)
- 📥 **下载**：下载抖音视频文件到本地 / **Download**: save Douyin video files locally
- 📝 **抖音文案提取**：双层方案——API字幕优先，FunASR API 转写兜底 / **Douyin copy extraction**: two-layer — API subtitles first, FunASR API fallback
- 🎧 **语音转写**：FunASR 通用转写（`aipdd_funasr_transcribe`）与字幕生成（`aipdd_funasr_subtitle`），支持情绪标签、说话人分离 / **Audio transcription**: FunASR generic transcription (`aipdd_funasr_transcribe`) and subtitle generation (`aipdd_funasr_subtitle`), with emotion labels and speaker diarization
- ℹ️ **信息查询**：查看抖音视频互动数据、字幕轨信息等 / **Info queries**: Douyin video engagement data, subtitle-track info, etc.

## 前置条件 / Prerequisites

### 必需 / Required
- Python 3.10+
- Python 依赖（httpx、playwright；推荐虚拟环境安装；macOS 新版系统 Python 受 PEP 668 保护，直接 `pip install` 会失败）：/ Python dependencies (httpx, playwright; a virtual environment is recommended — macOS system Python is PEP 668 protected, so bare `pip install` fails):
  ```
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  ```
  之后从技能根目录用 `.venv/bin/python scripts/douyin_fetch.py <命令>` 运行（下文命令中的 `python` 请替换为 `.venv/bin/python`）/ Then run from the Skill root with `.venv/bin/python scripts/douyin_fetch.py <command>` (replace `python` below with `.venv/bin/python`).
- FunASR API Key（sk-xxxx）：通过环境变量 `AIPDD_API_KEY` 或 config.json 的 `api.api_key` 提供（环境变量优先）。/ FunASR API Key (sk-xxxx): via env var `AIPDD_API_KEY` or `api.api_key` in config.json (env var takes precedence).
  请注册www.aipdd.work，并进入【全局设置-API Key 管理】中进行生成APIkey，即可获得 / Register at www.aipdd.work → Global Settings → API Key Management to generate one.
- **API Key 是转写的唯一前提**：转写引擎仅 FunASR 平台 API，**没有**本地模型或其他替代方案。缺少 Key 时唯一做法是让用户配置 Key 后重试（环境变量 AIPDD_API_KEY 或 config.json 的 api.api_key），不要寻找替代转写工具 / **The API Key is the sole prerequisite for transcription**: the only engine is the FunASR platform API — there is **no** local model or alternative. Without a key, the only move is to have the user configure one and retry; never hunt for a substitute transcription tool.
- FunASR 平台账户有余额（按音频实际秒数计费，约 100 AWcoin/秒，以平台能力目录为准）/ The FunASR account has balance (billed per actual audio second, ~100 AWcoin/sec, per the platform capability catalog).

### 抖音场景（必需，抖音视频采集都需要）/ Douyin scenario (required for all Douyin capture)
- 已安装 FFmpeg：`brew install ffmpeg`（macOS）或下载 Windows 版 / FFmpeg installed: `brew install ffmpeg` (macOS) or the Windows build.
- Playwright（获取视频信息的**默认方案**：自动打开视频页并拦截 `aweme/v1/web/aweme/detail/` 详情 API；依赖已包含在 requirements.txt）/ Playwright (the **default** way to fetch video info: auto-open the video page and intercept the `aweme/v1/web/aweme/detail/` API; included in requirements.txt).
  系统已装 Chrome 时无需下载 chromium（脚本自动使用 channel=chrome）；否则执行 `.venv/bin/playwright install chromium` / No chromium download needed if Chrome is installed (the script uses channel=chrome automatically); otherwise run `.venv/bin/playwright install chromium`.
- 音频提交需公网 URL 或平台文件 ID（FunASR 接口不接受本地文件路径）/ Audio submissions need a public URL or platform file ID (FunASR does not accept local paths).
- Chrome 浏览器（可选，Playwright 不可用时的备选方案：Chrome MCP 拦截详情 API）/ Chrome (optional fallback when Playwright is unavailable: Chrome MCP interception of the detail API).

### 语音转写场景 / Audio-transcription scenario
- 音频需为公网可访问的 URL（支持 `audio/*`，最长 3600 秒）或平台已有文件 ID / Audio must be a publicly reachable URL (supports `audio/*`, up to 3600s) or an existing platform file ID.

## 目录结构 / Directory Structure

```
抖音视频采集技能v3/
├── SKILL.md            ← 技能定义（本文件）/ Skill definition (this file)
├── requirements.txt    ← 依赖清单（httpx、playwright）/ Dependencies (httpx, playwright)
├── config.json         ← 配置文件（FunASR 参数、筛选规则、输出目录等）/ Config (FunASR params, filter rules, output dir, etc.)
├── scripts/            ← 脚本目录 / Scripts
│   └── douyin_fetch.py ← 主脚本（video_id 支持纯数字/完整链接/v.douyin.com 短链接）/ Main script (video_id: bare digits / full links / v.douyin.com short links)
└── .venv/              ← 虚拟环境（由 python3 -m venv 创建；不属于技能包交付内容，部署环境自行创建）/ Virtual env (created via python3 -m venv; not shipped with the package — create it at deploy time)
```

## 🔒 数据流向与安全说明 / Data Flow & Security

**全部网络请求清单（无其他出站端点）**：/ Complete network-request list (no other outbound endpoints):

| 目标 Target | 用途 Purpose | 发送内容 Sent |
|------|------|----------|
| `v.douyin.com` / `www.douyin.com` | 短链接解析、视频详情拦截 / short-link resolution, video-detail interception | 用户提供的链接、浏览器 UA / user-provided link, browser UA |
| 详情 API 返回的视频/字幕直链 / video/subtitle direct links from the detail API | 下载视频、字幕 / video & subtitle download | 仅 GET 下载请求 / GET download requests only |
| `api.aipdd.work`（FunASR 平台 / FunASR platform） | 转写任务创建/轮询/取结果 / task create/poll/result | 音频 URL（或平台 fileId）、任务参数、API Key 请求头 / audio URL (or fileId), task params, API Key header |

- **数据外发**：仅向 FunASR 平台提交音频 URL/fileId 与任务参数（转写由平台远程完成）；不发送用户提示词原文，不收集诊断/遥测数据 / **Data egress**: only audio URL/fileId and task params go to the FunASR platform (transcription runs remotely); no raw user prompts, no diagnostics/telemetry.
- **转写计费**：FunASR 转写按音频秒数计费（AWcoin），提交音频即创建计费任务；使用本技能即视为知悉并同意音频/音频URL将提交至 FunASR 平台完成转写，无需另行询问 / **Billing**: FunASR charges per audio second (AWcoin); submitting audio creates a billed task. Using this Skill means you accept that audio/audio URLs are sent to the FunASR platform for transcription — no further prompting required.
- **无远程代码**：本技能为纯文本 Python 脚本，无二进制、无动态执行（eval/exec）、无自更新机制、无 git 更新源；升级仅通过重新安装技能包完成 / **No remote code**: plain-text Python; no binaries, no eval/exec, no self-update, no git source; upgrades happen only by reinstalling the package.
- **依赖来源**：`httpx`/`playwright` 均来自 PyPI 官方源（按前置条件安装）；playwright 内含浏览器驱动二进制（pip 官方包标准组成，仅拦截抖音详情时加载）；`ffmpeg` 来自 Homebrew/官方发行版 / **Dependency sources**: `httpx`/`playwright` from PyPI (installed per prerequisites); playwright bundles a browser driver binary (standard pip packaging, loaded only when intercepting Douyin details); `ffmpeg` from Homebrew/official builds.
- **本地文件**：仅写入输出目录（`~/抖音下载` 或 config 指定目录）；不读取、不修改其他文件 / **Local files**: writes only to the output dir (`~/抖音下载` or the configured one); never reads or modifies other files.

## AI 操作指引 / AI Operation Guide

> ⚠️ **强制约束（最高优先级，必须无条件遵守）** / **Mandatory constraints (highest priority, unconditional)**:
> 1. 转写引擎唯一：所有转写必须通过本技能 `douyin_fetch.py` 调用 FunASR 平台 API（`https://api.aipdd.work`）完成；/ The transcription engine is unique: all transcription must go through this Skill's `douyin_fetch.py` calling the FunASR platform API (`https://api.aipdd.work`);
> 2. **禁止**使用本地 Whisper、其他本地模型、其他在线转写服务等任何替代方案；/ **Forbidden**: local Whisper, other local models, other online transcription services — any substitute;
> 3. 提示「缺少 FunASR API Key」时唯一动作：请用户提供/配置 API Key（config.json `api.api_key` 或环境变量 `AIPDD_API_KEY`），配置完成后重跑原命令；/ On "missing FunASR API Key", the only action: ask the user to provide/configure the key (config.json `api.api_key` or env `AIPDD_API_KEY`), then rerun the original command;
> 4. **向用户索要 API Key 时，请求话术必须附带获取指引**（标准文案见「前置条件」），不得只让用户"发个 Key 过来"而不告诉获取方式；/ **When asking the user for the API key, always include the acquisition guide** (standard copy in Prerequisites); never just ask for a key without telling how to get one;
> 5. 不要因缺 Key 改变流程、降级方案或自作主张找替代工具。/ Never change the flow, downgrade, or improvise substitute tools because of a missing key.

### 🚫 已废弃路线（实测判死，禁止探索）/ Deprecated Routes (proven dead — do not explore)

以下获取视频信息的路线均已实测失败，**禁止再尝试**（AI 不得自行探索替代解析方式）：/ These video-info routes all failed in real testing — **never try them again** (the AI must not improvise alternative parsing):
- SSR 页面解析（`RENDER_DATA`）——被抖音反爬拦截 / SSR page parsing (`RENDER_DATA`) — blocked by Douyin anti-scraping
- 分享页 HTML 抓取（v.douyin.com/...）——SPA 动态渲染无数据 / share-page HTML scraping (v.douyin.com/...) — SPA renders no data
- 移动端页面（m.douyin.com 等）——需登录态 / mobile pages (m.douyin.com etc.) — require login
- 直接调用 web API（aweme/v1/...）——无签名被拦 / direct web API calls (aweme/v1/...) — blocked without signatures
- `--script` 强制 SSR 参数——已移除 / `--script` forced-SSR flag — removed

获取视频信息只允许：**`detail` 命令（Playwright 自动拦截）** → 失败用 Chrome MCP → 再失败提示用户手动处理。/ Fetching video info is allowed only as: **`detail` command (Playwright auto-interception)** → Chrome MCP on failure → ask the user to handle it manually if that fails too.

**第一步：判断输入类型，选择对应流程** / **Step 1: classify the input and route to the matching flow**

- 输入是**抖音链接 / 视频ID**（如 `https://www.douyin.com/video/7611489793444171048`）→ 流程 A / Input is a **Douyin link / video ID** → Flow A
- 输入是**语音文件 / 音频 URL / 平台文件 ID** → 流程 B / Input is an **audio file / audio URL / platform file ID** → Flow B
- 输入是候选视频列表 + 筛选需求 → 流程 C / Input is a candidate list + filtering needs → Flow C

### 流程 A：抖音链接转写（用户提供抖音链接/视频ID）/ Flow A: Douyin link transcription

1. 从用户输入中提取 video_id：纯数字直接使用；完整链接取 `/video/` 后部分；`v.douyin.com` 短链接直接传给脚本，会自动解析重定向 / Extract video_id from the input: bare digits as-is; full links take the part after `/video/`; pass `v.douyin.com` short links straight to the script, which resolves redirects automatically.
2. **记录搜索关键字**（如有），用于目录分组和文件命名 / **Record the search keyword** (if any) for directory grouping and file naming.
3. **获取视频详情（默认方案）**——脚本用 Playwright 自动打开视频页并拦截 `aweme/v1/web/aweme/detail/` 详情 API，**一条命令完成全部后续流程**（拦截 → 解析 → 下载 → 提取文案 → 保存）：/ **Fetch video details (default)** — the script auto-opens the video page with Playwright and intercepts the `aweme/v1/web/aweme/detail/` API; **one command completes everything** (intercept → parse → download → extract copy → save):
   ```
   python scripts/douyin_fetch.py detail <video_id> --keyword <搜索关键字>
   ```
   - 若 Playwright 不可用或拦截失败：用下方「Chrome MCP 拦截（备选方案）」获取响应体存为 `detail.json`，执行 `python scripts/douyin_fetch.py process detail.json --keyword <搜索关键字>` / If Playwright is unavailable or interception fails: use "Chrome MCP interception (fallback)" below to save the response body as `detail.json`, then run `python scripts/douyin_fetch.py process detail.json --keyword <搜索关键字>`.
   - **若报「缺少 FunASR API Key」**：向用户索要 API Key 时必须**附带获取指引**（标准文案见「前置条件」），配置（config.json `api.api_key` 或环境变量 `AIPDD_API_KEY`）后重跑；**禁止**改用本地 Whisper 或其他转写工具，本技能转写引擎唯一（FunASR 平台 API）/ **On "missing FunASR API Key"**: when asking the user, **always include the acquisition guide** (see Prerequisites), then rerun after configuring (config.json `api.api_key` or env `AIPDD_API_KEY`); **never** switch to local Whisper or other tools — this Skill's engine is unique (FunASR platform API).
4. 视频无内置字幕时脚本**自动走 FunASR 兜底**：优先使用视频详情中的**原声音频直链**（`music.play_url`，douyinstatic.com 的 mp3，无防盗链，实测有效）；仅当视频使用他人 BGM（music.title 非"原声"）时才需用户提供音频来源：/ When the video has no built-in subtitles, the script **falls back to FunASR automatically**: it prefers the **original-audio direct link** from the video details (`music.play_url`, a douyinstatic.com mp3 without hotlink protection, verified working); only when the video uses someone else's BGM (music.title is not "原声/original") must the user provide an audio source:
   ```
   python scripts/douyin_fetch.py process detail.json --keyword <搜索关键字> --audio-url https://xxx.com/audio.wav
   ```
5. 汇报：视频文件路径、文案内容（标注来源：API字幕 / FunASR API）、互动数据 / Report: video file path, copy content (marked source: API subtitles / FunASR API), engagement data.

### 流程 B：语音转写（用户提供音频 URL / 平台文件 ID）/ Flow B: Audio transcription

1. 确认音频地址（公网 URL 或平台文件 ID）/ Confirm the audio address (public URL or platform file ID).
2. 用户有字幕需求时加 `--subtitle`（生成 SRT/VTT 字幕文件）：/ Add `--subtitle` when the user needs subtitle files (SRT/VTT):
   ```
   python scripts/douyin_fetch.py transcribe --audio <音频URL或fileId> --name 会议录音
   python scripts/douyin_fetch.py transcribe --audio <音频URL或fileId> --subtitle --language zh --name 课程音频
   ```
3. 汇报：转写文本、时长、分段数、说话人数；字幕模式附带字幕文件路径 / Report: text, duration, segment count, speaker count; include subtitle file paths in subtitle mode.

### 流程 C：筛选+下载（用户说"帮我筛选抖音视频"、"找爆款"等）/ Flow C: Filter & download

1. 检查 `config.json` 中 `filter.candidates` 是否有候选视频 / Check `filter.candidates` in `config.json` for candidate videos.
2. 如果没有，提示用户提供候选视频列表（格式：`视频ID, 标题, 作者, 点赞, 评论, 收藏, 分享`）/ If empty, ask the user for a candidate list (format: `video_id, title, author, likes, comments, collects, shares`).
3. 如果用户想临时调整筛选阈值，用命令行参数覆盖：/ Override thresholds temporarily via CLI flags:
   ```
   python scripts/douyin_fetch.py filter --min-digg 10000 --min-comment 0 --min-share 0
   ```
4. 执行脚本并汇报结果 / Run the script and report.

### Chrome MCP 拦截（备选方案）/ Chrome MCP Interception (Fallback)

仅当 `detail` 命令（Playwright）不可用或拦截失败时使用：/ Use only when the `detail` command (Playwright) is unavailable or fails:

1. 用 `navigate_page` 打开 `https://www.douyin.com/video/{video_id}` / Open `https://www.douyin.com/video/{video_id}` with `navigate_page`.
2. 用 `list_network_requests` 查找包含 `aweme/v1/web/aweme/detail/` 的请求（若直接拦截不到，可尝试页面内安装 fetch/XHR 拦截器后点击推荐视频触发 SPA 跳转再返回，捕获最新响应）/ Use `list_network_requests` to find requests containing `aweme/v1/web/aweme/detail/` (if not caught directly, install a fetch/XHR interceptor in the page, click a recommended video to trigger an SPA navigation, then return to capture the latest response).
3. 用 `get_network_request` 获取该请求的响应体（JSON），**保存为本地文件**（如 `detail.json`；响应可能 80-100KB，不要全文贴到对话中）/ Use `get_network_request` to get the JSON response body and **save it to a local file** (e.g. `detail.json`; it can be 80–100KB — never paste it fully into the chat).
4. 用 `process` 命令完成后续全流程（解析 → 下载 → 提取文案 → 保存）：/ Complete the rest with the `process` command (parse → download → extract copy → save):
   ```
   python scripts/douyin_fetch.py process detail.json --keyword <搜索关键字>
   ```
5. 或者直接从 JSON 中手动提取所需字段（不下载视频、仅看信息时）/ Or extract fields manually from the JSON (when only viewing info without downloading).

## 使用方式 / Usage

> 注：以下命令中的 `python` 若使用虚拟环境，请替换为 `.venv/bin/python` / Note: replace `python` with `.venv/bin/python` when using the virtual environment.

```bash
# ===== 场景一：抖音视频 / Scenario 1: Douyin video =====

# 筛选+下载（使用配置文件的候选列表和规则）/ Filter + download (config candidates & rules)
python scripts/douyin_fetch.py filter

# 临时降低筛选门槛 / Temporarily lower the filter thresholds
python scripts/douyin_fetch.py filter --min-digg 10000 --min-comment 0 --min-share 0

# 默认方案：Playwright 自动拦截详情 API → 自动完成下载+转写+保存（一条命令）
# Default: Playwright auto-interception → download + transcribe + save in one command
python scripts/douyin_fetch.py detail 7611489793444171048 --keyword 搜索关键字

# 处理已保存的详情 JSON（detail 命令或 Chrome MCP 拦截的响应体）
# Process a saved detail JSON (from `detail` or Chrome MCP interception)
python scripts/douyin_fetch.py process detail.json --keyword 搜索关键字

# 注意：download / transcript / info 命令已停用（SSR 解析被抖音反爬拦截），
# 需要视频信息/文案请统一使用 detail 命令（拦截+下载+转写+保存一条命令完成）
# Note: download / transcript / info are retired (SSR parsing blocked by Douyin);
# use `detail` for any video info/copy (intercept+download+transcribe+save in one)

# ===== 场景二：语音转写（FunASR）/ Scenario 2: Audio transcription (FunASR) =====

# 通用转写（文本）/ Generic transcription (text)
python scripts/douyin_fetch.py transcribe --audio https://example.com/interview.wav --name 访谈录音

# 转写 + 生成字幕文件（srt/vtt）/ Transcribe + subtitle files (srt/vtt)
python scripts/douyin_fetch.py transcribe --audio https://example.com/course.wav --subtitle --language zh --name 课程音频

# 使用平台文件 ID（此前已上传到平台的音频）/ Use a platform file ID (audio previously uploaded)
python scripts/douyin_fetch.py transcribe --audio file-xxxx --name 会议录音
```

## 输出产物 / Outputs

按搜索关键字分组存储，目录名即为搜索关键字：/ Stored in folders named after the search keyword:

```
~/抖音下载/AI新闻/
├── 2026-04-19 一周AI大事盘点.mp4        ← 视频文件 / video file
├── 2026-04-19 一周AI大事盘点.txt         ← 口播文案 / voice-over copy
└── 2026-04-19 一周AI大事盘点.srt         ← 字幕（FunASR 字幕任务生成）/ subtitles (FunASR subtitle task)

~/抖音下载/赚钱干货/
├── 2026-04-20 打破信息茧房.mp4
└── 2026-04-20 打破信息茧房.txt

~/抖音下载/2026-08-14/                   ← 语音转写（无关键字时按日期分组）/ transcription (dated when no keyword)
├── 2026-08-14 访谈录音.txt
└── 2026-08-14 访谈录音.srt
```

文件命名规则：`yyyy-MM-dd 关键字.mp4` / `.txt` / `.srt` / `.vtt` / File naming: `yyyy-MM-dd keyword.mp4` / `.txt` / `.srt` / `.vtt`
- 抖音视频：`yyyy-MM-dd` 取自视频发布日期（create_time），关键字从标题自动提取（前12个有效字符）/ Douyin video: `yyyy-MM-dd` from the publish date (create_time); keyword auto-extracted from the title (first 12 valid characters)
- 语音转写：`yyyy-MM-dd 任务名` / Transcription: `yyyy-MM-dd task-name`

文案文件格式：/ Copy file format:

```
视频ID: 7611489793444171048
标题: 打破信息茧房之后才知道之前都在傻干活
作者: Ai破壁人小彭
互动: 👍68,575 💬218 ⭐35,416 🔗6,410
文案来源: API字幕          ← 或 FunASR API (aipdd_funasr_transcribe) / or FunASR API
==================================================
【口播文案】/ [Voice-over copy]

（文案内容）/ (copy content)
```

## 配置说明 / Configuration

所有配置项均在根目录 `config.json` 中，支持空值使用智能默认值。/ All options live in the root `config.json`; empty values fall back to smart defaults.

| 配置项 Option | 说明 Description | 默认值 Default |
|--------|------|--------|
| `output_dir` | 输出根目录 / Output root | `~/抖音下载/` |
| `ffmpeg_path` | FFmpeg 路径 / FFmpeg path | 系统 PATH 中的 ffmpeg / ffmpeg on PATH |
| `api.base_url` | FunASR 平台 Base URL / FunASR platform base URL | `https://api.aipdd.work` |
| `api.api_key` | FunASR API Key（环境变量 `AIPDD_API_KEY` 优先；请注册www.aipdd.work，并进入【全局设置-API Key 管理】中进行生成APIkey，即可获得）/ FunASR API Key (env `AIPDD_API_KEY` wins; register at www.aipdd.work → Global Settings → API Key Management) | 空 / empty |
| `funasr.task_type` | 通用转写能力码 / Generic transcription capability code | `aipdd_funasr_transcribe` |
| `funasr.subtitle_task_type` | 字幕生成能力码 / Subtitle capability code | `aipdd_funasr_subtitle` |
| `funasr.language` | 语言提示（auto/zh/en/ja/ko/yue）/ Language hint | `auto` |
| `funasr.output_formats` | 通用转写输出格式 / Generic transcription output formats | `["json"]` |
| `funasr.subtitle_output_formats` | 字幕任务输出格式 / Subtitle output formats | `["json","srt","vtt"]` |
| `funasr.enable_emotion_labels` | 情绪/事件标签 / Emotion/event labels | `true` |
| `funasr.enable_speaker_diarization` | 说话人分离 / Speaker diarization | `true` |
| `funasr.max_duration_seconds` | 运行时安全上限（非计费依据）/ Runtime safety cap (not billing basis) | `3600` |
| `funasr.poll_timeout` | 任务轮询超时（秒）/ Task poll timeout (s) | `1800` |
| `funasr.save_subtitle_files` | 自动下载保存字幕文件 / Auto-download subtitle files | `true` |
| `filter.rules.min_digg` | 最低点赞数 / Min likes | 20000 |
| `filter.rules.min_comment` | 最低评论数 / Min comments | 5000 |
| `filter.rules.min_share` | 最低分享数 / Min shares | 5000 |
| `filter.process_count` | 每次处理几个视频 / Videos processed per run | 1 |
| `filter.candidates` | 候选视频列表 / Candidate video list | [] |
| `browser.wait_timeout` | 页面等待时间 / Page wait time | 10秒 / 10s |
| `download.timeout` | 下载超时 / Download timeout | 90秒 / 90s |
| `subtitle.method` | 抖音文案策略：`api_first` / Douyin copy strategy: `api_first` | `api_first` |
| `subtitle.max_length` | 文案最大长度（0 表示不截断）/ Max copy length (0 = no truncation) | 0 |

### 候选视频格式 / Candidate Video Format

```json
{
  "filter": {
    "candidates": [
      {
        "video_id": "7611489793444171048",
        "desc": "打破信息茧房之后才知道之前都在傻干活",
        "author": "Ai破壁人小彭",
        "digg_count": 68575,
        "comment_count": 218,
        "collect_count": 35416,
        "share_count": 6410
      }
    ]
  }
}
```

## 技术原理 / How It Works

1. **获取抖音视频信息**：默认用 `detail` 命令（Playwright 自动打开视频页并拦截 `aweme/v1/web/aweme/detail/` 详情 API，无需 Chrome MCP）；Playwright 不可用时用 Chrome MCP 拦截；SSR 页面解析（`RENDER_DATA`）已被反爬拦截，禁止使用 / **Fetching Douyin video info**: the `detail` command by default (Playwright auto-opens the page and intercepts the `aweme/v1/web/aweme/detail/` API — no Chrome MCP needed); Chrome MCP interception when Playwright is unavailable; SSR parsing (`RENDER_DATA`) is blocked by anti-scraping and forbidden.
2. **视频下载**：从 API 响应中提取视频 URL（优先 VE 混合轨道），httpx 异步下载 / **Download**: extract the video URL from the API response (VE mixed track preferred), async download via httpx.
3. **抖音文案提取（双层方案）**：/ **Douyin copy extraction (two layers)**:
   - 第一层：API 字幕轨（`subtitle_infos` 中的 VTT/SRT 文件）→ 解析为纯文本 / Layer 1: API subtitle tracks (VTT/SRT in `subtitle_infos`) → parse to plain text.
   - 第二层：FunASR 平台转写（需公网音频 URL 或平台文件 ID），可选 FFmpeg 本地提取音频 / Layer 2: FunASR platform transcription (needs a public audio URL or platform file ID); optional local FFmpeg audio extraction.
4. **FunASR 语音转写（平台任务流）**：/ **FunASR transcription (platform task flow)**:
   - 创建任务：`POST /shared-tasks/tasks`（能力码 `aipdd_funasr_transcribe` / `aipdd_funasr_subtitle`）/ Create: `POST /shared-tasks/tasks` (capability `aipdd_funasr_transcribe` / `aipdd_funasr_subtitle`).
   - 轮询状态：`GET /shared-tasks/tasks/{taskId}`（按响应 `pollAfterMs` 间隔）/ Poll: `GET /shared-tasks/tasks/{taskId}` (at the response's `pollAfterMs` interval).
   - 获取结果：`GET /shared-tasks/tasks/{taskId}/result`（`output.text` 为完整文本，`downloadRefs` 提供字幕文件下载链接）/ Result: `GET /shared-tasks/tasks/{taskId}/result` (`output.text` is the full text; `downloadRefs` provides subtitle download links).
5. **抖音音频来源策略**（无字幕时 FunASR 兜底的输入选择，实测结论）：/ **Douyin audio-source strategy** (FunASR fallback input when no subtitles — field-tested):
   - **优先**：详情 JSON 的 `music.play_url.url_list`（**原声音频直链**，`douyinstatic.com` 的 mp3，无签名防盗链，平台可直接下载）→ 直接提交 FunASR / **Preferred**: `music.play_url.url_list` from the detail JSON (**original-audio direct link**, a douyinstatic.com mp3 without signature hotlink protection, directly downloadable) → submit straight to FunASR.
   - 视频直链不可用：`v26-web.douyinvod.com` 有防盗链（平台服务端无 UA/Referer 会被拒，报"输入文件 URL 不可达"）；`www.douyin.com/aweme/v1/play/` 即使可达也返回 video/octet-stream 不在类型白名单 / Video direct links fail: `v26-web.douyinvod.com` is hotlink-protected (the platform server without UA/Referer gets "input file URL unreachable"); `www.douyin.com/aweme/v1/play/` even when reachable returns video/octet-stream, outside the MIME whitelist.
   - FunASR 参数白名单仅接受 `audio/*`（`params.acceptedMimeTypes`），视频 MIME 一律拒绝 / FunASR's whitelist only accepts `audio/*` (`params.acceptedMimeTypes`); video MIME types are always rejected.
   - 本地提取的 wav 无法直接提交（需公网 URL）；国外匿名托管（catbox/tmpfiles 等）国内网络不可达；平台无公开上传接口（探测 404），需用户自行上传 OSS 等 / Locally extracted wav can't be submitted directly (needs a public URL); overseas anonymous hosts (catbox/tmpfiles etc.) are unreachable from mainland networks; the platform has no public upload endpoint (probing returned 404) — the user must upload to OSS or similar.
6. **鉴权**：`Authorization: Bearer sk-xxxx`，环境变量 `AIPDD_API_KEY` 优先于 config.json / **Auth**: `Authorization: Bearer sk-xxxx`; env `AIPDD_API_KEY` beats config.json.

## 注意事项 / Notes

- FunASR 按平台预处理得到的音频实际秒数计费（冻结 AWcoin），任务失败/取消会退回冻结费用 / FunASR bills by the platform-preprocessed audio seconds (AWcoin frozen); failed/cancelled tasks refund the frozen amount.
- 抖音视频无字幕时优先用**原声音频直链**（`music.play_url`）转写；判断依据：`music.title` 含"原声"（如"@作者创作的原声"）；若 `music.title` 是歌曲名（BGM），转写出来是歌词、无口播意义，需改用 `--audio-url` / Without subtitles, prefer the **original-audio direct link** (`music.play_url`); judge by `music.title` containing "原声" (e.g. "@author's original audio"); if `music.title` is a song name (BGM), transcription yields lyrics with no voice-over value — use `--audio-url` instead.
- 音频必须为**公网可访问的 URL**（支持 `audio/*`，最大 1 GiB / 3600 秒）或**平台文件 ID**，不接受本地路径；抖音视频需先用 FFmpeg 提取音频并上传到公网 / Audio must be a **publicly reachable URL** (`audio/*`, max 1 GiB / 3600s) or a **platform file ID**; local paths are rejected. Douyin videos need FFmpeg audio extraction plus a public upload first.
- 不要传入 `durationSeconds`、`numFrames` 等视频类计费字段，FunASR 会拒绝 / Never pass video billing fields like `durationSeconds` or `numFrames` — FunASR rejects them.
- `requestId` 由脚本自动生成，同一用户重复提交相同 requestId 会返回已有任务（幂等），无需手动处理 / `requestId` is auto-generated; resubmitting the same requestId returns the existing task (idempotent) — no manual handling needed.
- 抖音视频需要有口播内容才能提取文案；API 字幕仅对带字幕的视频有效 / Douyin videos need voice-over content for copy extraction; API subtitles only exist for videos with subtitles.
- 下载可能因网络或抖音限制失败，可重试；大量下载可能触发反爬，建议控制频率 / Downloads may fail due to network or Douyin limits — retry; bulk downloads can trigger anti-scraping, so pace them.
- 首次使用请在终端验证 API Key：`export AIPDD_API_KEY=sk-xxxx` / On first use, verify the key in a terminal: `export AIPDD_API_KEY=sk-xxxx`.
- 不要将 API Key 提交到公开仓库，优先使用环境变量 / Never commit the API key to a public repo; prefer the environment variable.

## 常见问题 / FAQ

| 问题 Issue | 解决方案 Solution |
|------|----------|
| 运行报 "No module named 'httpx'" / "No module named 'httpx'" | 按前置条件创建虚拟环境：`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`，用 `.venv/bin/python` 运行 / Create the venv per Prerequisites and run with `.venv/bin/python` |
| 「缺少 FunASR API Key」/ "Missing FunASR API Key" | 向用户索要 Key 时必须附带获取指引（标准文案见「前置条件」），配置（环境变量 `AIPDD_API_KEY=sk-xxxx` 或 config.json 的 `api.api_key`）后重跑原命令；**禁止**改用本地 Whisper 等替代转写方案（转写引擎唯一：FunASR 平台 API）/ Always include the acquisition guide; configure (env or config.json) and rerun; never switch to Whisper or other substitutes (unique engine: FunASR API) |
| "接口鉴权失败（401）"/ "Auth failed (401)" | 检查 API Key 是否正确、账户是否有余额 / Check the key and account balance |
| "无法获取抖音视频信息"/ "Cannot fetch Douyin video info" | 默认方案：`python scripts/douyin_fetch.py detail <video_id>`（Playwright 自动拦截详情 API）；失败用 Chrome MCP 拦截 `aweme/v1/web/aweme/detail/` 响应体存为文件 → `python scripts/douyin_fetch.py process detail.json --keyword <搜索关键字>`；再失败提示用户手动处理 / Default: the `detail` command; fallback: Chrome MCP interception to a file → `process detail.json`; then ask the user to handle manually |
| "API字幕内容为空"/ "API subtitles empty" | 自动进入 FunASR 兜底：脚本优先用原声音频直链（`music.play_url`）转写；无原声时才需提供 `--audio-url`（公网URL或fileId）/ Auto FunASR fallback: original-audio direct link (`music.play_url`) first; provide `--audio-url` only when there's no original audio |
| "FFmpeg 提取音频失败"/ "FFmpeg audio extraction failed" | 检查 ffmpeg 是否已安装：`ffmpeg -version` / Check ffmpeg: `ffmpeg -version` |
| 任务长时间 QUEUED/RUNNING / Task stuck QUEUED/RUNNING | 属正常排队，按 `pollAfterMs` 自动轮询；可调大 `funasr.poll_timeout` / Normal queueing; auto-polls per `pollAfterMs`; raise `funasr.poll_timeout` |
| 创建任务报"该能力不支持此输入参数"/ "Capability doesn't support this input param" | 未传入视频类计费字段；检查 `api.base_url` 与能力码是否拼写正确 / Don't pass video billing fields; check `api.base_url` and capability codes |
| 创建任务报"输入文件 URL 不可达"/ "Input file URL unreachable" | 视频直链（douyinvod）有防盗链，平台服务端无法下载；改用详情 JSON 中 `music.play_url` 原声音频直链（脚本已自动处理）/ douyinvod links are hotlink-protected; use `music.play_url` from the detail JSON (the script does this automatically) |
| 创建任务报"格式不在允许的类型列表中"/ "Format not in the allowed type list" | 提交了视频/未知类型 URL；FunASR 只接受 `audio/*`，改用 mp3 原声直链或公网音频 URL / You submitted a video/unknown URL; FunASR only accepts `audio/*` — use the mp3 original-audio link or a public audio URL |
| 下载的视频无声音 / Downloaded video has no sound | 抖音对部分视频分离了音视频轨道，尝试用浏览器拦截获取更完整的 URL / Douyin splits tracks on some videos; try browser interception for a more complete URL |
| 报"缺少 playwright"/ "playwright missing" | 安装：`.venv/bin/pip install -r requirements.txt`；系统已装 Chrome 时无需下载 chromium，否则执行 `.venv/bin/playwright install chromium` / Install requirements; skip chromium if Chrome exists, else `.venv/bin/playwright install chromium` |
| Playwright 拦截失败 / Playwright interception failed | 可能需要登录/验证：可改用 Chrome MCP 拦截详情 API，或先手动打开页面登录后再试 / May need login/verification: use Chrome MCP interception, or log in manually first |
