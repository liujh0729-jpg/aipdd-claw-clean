---
name: video-publisher
description: |
  A safe video-publishing Skill for Codex and Claude Code. It takes local videos and operates real creator pages on Xiaohongshu, Douyin, Bilibili, and WeChat Channels via Ego Lite — handling uploads, titles & tags, original-content declarations, optional covers, and pre-publish checks — then stops before the final publish button for human review. Use for first-time setup, multi-platform draft preparation, upload-interruption recovery, draft verification, and publishing workflow extensions; trigger on "publish video", "upload to Douyin/Bilibili/XHS/WeChat Channels", "prepare multi-platform video drafts".
  面向 Codex 与 Claude Code 的安全视频发布 Skill。接收本地视频，通过 Ego Lite 操作小红书、抖音、哔哩哔哩和微信视频号的真实创作者页面，完成上传、标题与标签、原创声明、可选封面及发布前检查，并停在最终发布按钮前供人工复核。适用于首次配置、多平台草稿准备、上传中断恢复、草稿核验和发布流程扩展；用户提到"发布视频""上传到抖音/B站/小红书/视频号""准备多平台视频草稿"时应使用。
---

# Video Publisher 视频发布助手 / Video Publishing Assistant

Video Publisher 是一个面向 Codex / Claude Code 的视频发布 Skill。给它一个本地视频，它会通过 Ego Lite 操作真实创作者页面，为已配置的平台完成视频上传、标题与标签填写、原创声明、可选封面上传和发布前检查，最后把每个平台保留在可人工复核的状态。

Video Publisher is a video-publishing Skill for Codex / Claude Code. Give it a local video, and it drives real creator pages via Ego Lite to upload, fill titles and tags, set original-content declarations, attach optional covers, and run pre-publish checks — leaving each platform in a state ready for human review.

> 核心原则：默认只把草稿准备到"可以发布"，绝不把"准备草稿"理解为"允许发布"。
> Core principle: prepare drafts only up to "ready to publish" — never interpret "prepare a draft" as "authorized to publish".

## 能力范围 / Capabilities

支持以下创作者平台：/ Supports these creator platforms:

- 小红书（`xiaohongshu`）
- 抖音（`douyin`）
- 哔哩哔哩 / B站（`bilibili`）
- 微信视频号（`wechat_channels`）

本 Skill 可以：/ This Skill can:

- 接收并校验本地 MP4、M4V、MOV 视频；/ Accept and validate local MP4, M4V, MOV videos;
- 根据用户确认的内容包填写各平台标题、正文、话题或标签；/ Fill in each platform's title, body, topics or tags from a user-confirmed content package;
- 在用户具有真实原创权利时设置原创或自制声明；/ Set original/self-made declarations only when the user holds genuine originality rights;
- 按需上传用户已经准备好的 3:4、4:3 封面；/ Upload user-provided 3:4 or 4:3 covers on demand;
- 并行处理平台检查与视频上传，串行执行页面修改；/ Run platform checks and video uploads in parallel, while serializing page mutations;
- 恢复中断任务、识别错误草稿、保留可验证的任务状态；/ Resume interrupted tasks, spot wrong drafts, and keep verifiable task state;
- 对每个平台执行独立发布前核验，并停在最终发布按钮前。/ Run independent pre-publish verification per platform and stop before the final publish button.

本 Skill 不会：/ This Skill will NOT:

- 生成、剪辑、转码或自动裁短视频；/ Generate, edit, transcode or auto-crop videos;
- 生成或编辑封面图片；/ Generate or edit cover images;
- 保存账号密码、Cookie 或令牌；/ Store passwords, cookies or tokens;
- 在没有真实权利确认时勾选原创声明；/ Check originality declarations without genuine rights confirmation;
- 因为用户说"上传"或"准备草稿"就点击最终发布按钮。/ Click the final publish button just because the user said "upload" or "prepare a draft".

## 运行环境 / Runtime Environment

正式使用前先阅读 [`references/environment.md`](references/environment.md)。最低要求如下：/ Read [`references/environment.md`](references/environment.md) first. Minimum requirements:

1. **宿主 Agent**：Codex 或 Claude Code，能够读取本地文件并执行 Node.js / Shell 命令。/ **Host agent**: Codex or Claude Code, able to read local files and run Node.js / Shell commands.
2. **Node.js**：建议 Node.js 20 LTS 或更高版本；代码只使用 Node.js 内置模块，无需执行 `npm install`。/ **Node.js**: 20 LTS or newer recommended; only built-in modules are used — no `npm install` needed.
3. **操作系统**：推荐 macOS 或 Linux；需要 Bash。Windows 建议使用 WSL2，并确认 Ego Lite 能访问同一套文件路径。/ **OS**: macOS or Linux recommended; Bash required. On Windows use WSL2 and make sure Ego Lite can reach the same file paths.
4. **Ego Lite**：必须已安装并能调用 `ego-browser`，且真实浏览器进程可用。/ **Ego Lite**: installed, `ego-browser` callable, and a real browser process available.
5. **账号与登录态**：用户至少拥有一个受支持平台的创作者账号，并已在 Ego Lite 管理的真实浏览器中完成登录。/ **Accounts & login**: the user owns at least one supported creator account, logged in inside the real browser managed by Ego Lite.
6. **本地文件访问**：视频和封面必须是 Agent 与 Ego Lite 都能读取的绝对路径。/ **Local file access**: videos and covers must be absolute paths readable by both the Agent and Ego Lite.
7. **网络**：当前网络必须能正常访问所选平台的创作者中心；风控、验证码和账号认证需要用户本人处理。/ **Network**: the creator center of the chosen platform must be reachable; risk-control, CAPTCHAs and account verification are handled by the user.
8. **磁盘空间**：为源视频、浏览器缓存和任务状态保留足够空间；大视频建议至少保留源文件大小两倍以上的可用空间。/ **Disk space**: keep room for source videos, browser cache and task state; for large videos keep at least 2× the source size free.

不需要 `ffmpeg` 或 `ffprobe`。MP4/M4V/MOV 时长会直接从 ISO BMFF 元数据读取。/ No `ffmpeg` or `ffprobe` needed — MP4/M4V/MOV durations are read directly from ISO BMFF metadata.

## 每次调用的固定入口 / Fixed Entry Point

在检查视频、创建内容包或打开浏览器之前，先在 Skill 根目录运行：/ Before checking videos, creating content packages, or opening a browser, run from the Skill root:

```bash
node scripts/config.mjs status
```

若返回 `onboardingRequired: true`，必须先完成首次配置，不得打开创作者页面。/ If it returns `onboardingRequired: true`, complete first-time setup before opening any creator page.

个人配置保存在：/ Personal config is stored at:

```text
$VIDEO_PUBLISHER_CONFIG（若设置 / if set）
$XDG_CONFIG_HOME/video-publisher/config.json
$HOME/.config/video-publisher/config.json
```

个人配置不得写入可分享的 Skill 目录。完整配置规则见 [`references/configuration.md`](references/configuration.md)。/ Personal config must never be written into the shareable Skill directory. Full config rules: [`references/configuration.md`](references/configuration.md).

## 首次配置流程 / First-Time Setup

首次使用时按以下顺序询问，避免一次抛出过多问题：/ On first use, ask in this order to avoid overwhelming the user:

1. 用户实际拥有并可登录哪些平台，至少选择一个；不得默认四个平台全有。/ Which platforms the user actually owns and can log into — at least one; never assume all four.
2. 未明确指定平台时，默认处理哪些已拥有的平台。/ Which owned platforms to process by default when none is specified.
3. 默认本地视频目录。/ Default local video directory.
4. 常用文案风格和重复使用的标签偏好。/ Common copywriting style and recurring tag preferences.
5. 仅在已配置抖音时询问默认抖音话题；仅在已配置 B站时询问允许保留的自动标签。/ Ask about default Douyin topics only if Douyin is configured; ask about auto-tags to keep only if Bilibili is configured.
6. 是否能确认"所有待处理视频均为原创"；没有明确确认时使用 `ask_each_run`。/ Whether "all pending videos are original" can be confirmed; use `ask_each_run` without explicit confirmation.
7. 建议检查并发数与上传并发数均为 4，封面默认使用平台自动封面。/ Suggest 4 for both check and upload concurrency; default covers to the platform's auto cover.
8. 用中文汇总，得到确认后写入配置并执行校验。/ Summarize, then write the config and validate after user confirmation.

示例：/ Example:

```bash
node scripts/config.mjs onboard \
  --source-dir "/绝对路径/视频目录" \
  --available-platform xiaohongshu \
  --available-platform douyin \
  --platform xiaohongshu \
  --platform douyin \
  --originality-policy ask_each_run

node scripts/config.mjs validate
```

只有在 `validate` 成功且 `onboardingRequired` 为 `false` 时才能继续。/ Continue only when `validate` passes and `onboardingRequired` is `false`.

## 安全边界（必须遵守）/ Safety Boundaries (Mandatory)

### 1. 默认禁止最终发布 / Final Publishing Forbidden by Default

除非用户在**当前这一次运行**中明确要求立即发布，否则不得点击以下最终控件：/ Unless the user explicitly asks to publish immediately in **this run**, never click these final controls:

- `发布` / `Publish`
- `发布笔记` / `Publish Note`
- `发表` / `Post`
- `立即投稿` / `Submit Now`

上传完成、草稿准备完成、用户以前授权过发布，都不能代替本轮明确授权。生产运行器会为这些控件安装页面级阻止保护；进入 `READY` 前必须确认：/ Completed uploads, prepared drafts, or past authorization never replace this run's explicit consent. Production runners install page-level guards on these controls; before entering `READY`, confirm:

```text
guardArmed: true
blockedAttempts: 0
finalPublishClicked: false
```

即使用户明确授权发布，也应先完成全部发布前检查，并优先让用户人工复核；不要绕过现有保护机制自行点击。/ Even with explicit authorization, finish all pre-publish checks first and prefer human review — never bypass the existing protections to click on your own.

### 2. 原创声明必须真实 / Originality Declarations Must Be Truthful

勾选 `原创`、`自制` 或同类声明前，必须满足以下任一条件：/ Before checking `Original`, `Self-made` or similar declarations, at least one of these must hold:

- 配置中的 `declarations.originalityPolicy` 为 `all_videos_original`；/ `declarations.originalityPolicy` is `all_videos_original`;
- 用户明确确认当前视频拥有原创权利，并在本轮传入 `--confirm-original-rights`。/ The user explicitly confirms originality rights for this video and passes `--confirm-original-rights` this run.

不得根据文件名、视频内容或账号习惯自行推断。原创授权与最终发布授权是两件独立的事。/ Never infer from file names, video content, or account habits. Originality authorization and publish authorization are separate.

### 3. 遇到人工接管立即停止 / Stop Immediately on Human Takeover

若 Ego Lite 表示用户已接管任务空间，立即停止所有浏览器操作。只有用户明确说"继续"后，才可重新接管已记录的同一任务空间；不得另开任务空间绕过。/ If Ego Lite reports the user has taken over the task space, stop all browser operations immediately. Only resume the same recorded task space after the user explicitly says "continue"; never open another task space to bypass this.

### 4. 成功必须由页面状态证明 / Success Must Be Proven by Page State

"执行了点击""调用上传成功""出现预览卡片"都不是成功。每个字段、标签、原创声明、设置和封面都必须由新的页面检查确认。最终每个平台只能是：/ "A click was executed", "upload call succeeded", or "a preview card appeared" are not success. Every field, tag, declaration, setting and cover must be confirmed by a fresh page check. Each platform may end only as:

- `ready`：所有必需条件均由最新页面证据验证；/ all required conditions verified by the latest page evidence;
- 带明确类型的阻塞状态：确实需要用户操作或稍后重试。/ a blocked state with an explicit type: genuinely needing user action or a later retry.

## 视频与内容包受理 / Video & Content-Package Intake

处理前确认：/ Before processing, confirm:

- 源视频的精确绝对路径；/ the exact absolute path of the source video;
- 目标平台必须属于配置中的 `availablePlatforms`；/ target platforms are within configured `availablePlatforms`;
- 标题、正文、标签或话题；/ title, body, tags or topics;
- 当前视频的原创权利状态；/ originality-rights status of the current video;
- 是否使用用户提供的现有封面；/ whether to use the user's existing cover;
- 是否只准备草稿并留待人工复核（默认是）。/ whether to only prepare drafts for human review (default: yes).

若路径不存在，不得猜测或换用相似文件。应停止浏览器操作，并列出默认视频目录中的相近候选，让用户确认。/ If the path does not exist, never guess or substitute similar files. Stop browser operations and list similar candidates from the default video directory for the user to confirm.

平台默认内容习惯：/ Platform content defaults:

```text
小红书：短标题 + 真实话题实体；默认不写长正文。
Xiaohongshu: short title + real topic entities; no long body by default.
抖音：标题/正文 + 1～5 个内容包指定的话题实体。
Douyin: title/body + 1–5 topic entities from the content package.
B站：标题 + 简介 + 标签标签块 + 自制声明。
Bilibili: title + description + tag block + self-made declaration.
视频号：描述以标题开头并包含普通 #标签；短标题默认留空。
WeChat Channels: description starts with the title and includes plain #tags; short title left empty by default.
```

受理与内容包格式详见 [`references/intake-workflow.md`](references/intake-workflow.md)。/ Intake & content-package format: [`references/intake-workflow.md`](references/intake-workflow.md).

## 封面规则 / Cover Rules

默认使用平台自动封面。只有用户提供现有封面并明确启用 `cover.uploadCustomCover: true` 时，才允许上传：/ Platform auto covers by default. Upload a custom cover only when the user provides one and explicitly enables `cover.uploadCustomCover: true`:

```text
小红书：3:4
抖音：3:4 和 4:3
B站：4:3
视频号：3:4 和 4:3
```

推荐尺寸：3:4 使用 1080×1440；4:3 使用 1440×1080。每张封面都要验证文件存在、比例正确，并在平台主页面重新确认已接受的封面结果。详见 [`references/cover-workflow.md`](references/cover-workflow.md)。/ Recommended sizes: 1080×1440 for 3:4; 1440×1080 for 4:3. Verify each cover's existence and aspect ratio, and re-confirm the accepted result on the platform page. See [`references/cover-workflow.md`](references/cover-workflow.md).

## 发布前校验 / Pre-Publish Validation

打开浏览器前，对每个目标平台执行：/ Before opening a browser, run for each target platform:

```bash
node scripts/check-package.mjs <平台标识/platform-id> /绝对路径/package.json
```

校验内容包括视频路径、标题限制、平台必填字段、抖音话题、封面路径与比例、媒体格式及时长。/ Checks cover video path, title limits, platform-required fields, Douyin topics, cover path & aspect ratio, media format and duration.

抖音真实验证边界为 900 秒，并允许最多 0.1 秒的容器元数据舍入误差。超过边界时不得自动裁剪或转码，应将抖音标记为 `PLATFORM_REJECTED_ASSET`，其他校验通过的平台仍可继续。/ Douyin's real validation limit is 900 seconds with up to 0.1s of container-metadata rounding tolerance. Beyond it, never auto-crop or transcode: mark Douyin as `PLATFORM_REJECTED_ASSET` while other validated platforms may continue.

## 标准执行流程 / Standard Execution Flow

1. 读取配置，必要时完成首次配置。/ Read config; complete first-time setup if needed.
2. 确认精确源视频及字幕版本。/ Confirm the exact source video and subtitle version.
3. 根据用户要求与配置默认值拟定内容包。/ Draft the content package from user requirements and config defaults.
4. 让用户确认标题、标签、平台、原创权利和封面意图。/ Have the user confirm titles, tags, platforms, originality rights and cover intent.
5. 对每个平台执行本地校验。/ Run local validation per platform.
6. 使用生产编排器运行任务。/ Run the task with the production orchestrator.
7. 并行检查各平台，并在需要时处理 B站旧草稿。/ Check platforms in parallel; handle Bilibili stale drafts when needed.
8. 并行上传缺失视频，等待所有上传完全结束。/ Upload missing videos in parallel; wait for all uploads to fully finish.
9. 通过单一页面操作队列依次修复文案、话题、声明、设置和封面。/ Serialize page mutations through a single queue to fix copy, topics, declarations, settings and covers.
10. 并行执行独立最终核验。/ Run independent final verification in parallel.
11. 保留所有任务空间，停在最终发布按钮前供人工复核。/ Keep all task spaces and stop before the final publish button for human review.

生产命令：/ Production command:

```bash
scripts/run-safe-platforms.sh <package.json> [任务后缀/job-suffix] [平台.../platforms...]
```

只读检查：/ Read-only inspection:

```bash
scripts/run-safe-platforms.sh <package.json> [任务后缀/job-suffix] [平台.../platforms...] --inspect-only
```

具体命令和退出码见 [`references/scripts.md`](references/scripts.md)。/ Commands and exit codes: [`references/scripts.md`](references/scripts.md).

## 并发、状态与恢复 / Concurrency, State & Recovery

生产流程只允许一个编排器控制真实创作者账号。一个任务内部按资源类型调度：/ Only one orchestrator may control real creator accounts in production. Within a task, schedule by resource type:

```text
只读检查：并行，默认最多 4
Read-only checks: parallel, up to 4 by default
视频上传与平台处理等待：并行，默认最多 4
Video upload & platform-processing waits: parallel, up to 4 by default
文案、话题、声明、设置、封面：严格串行，只允许 1
Copy, topics, declarations, settings, covers: strictly serial, exactly 1
最终核验：并行，默认最多 4
Final verification: parallel, up to 4 by default
```

上传阶段是硬屏障：所有上传运行器退出前，不得开始页面修改。平台出现上传进度、百分比、处理中或"取消上传"等提示时，不能把预览卡片视为上传完成。/ The upload phase is a hard barrier: no page mutations before all upload runners exit. When the platform shows progress, percentages, "processing" or "cancel upload", a preview card is not proof of completion.

任务状态默认保存在 `~/.video-publisher/v2-jobs/`。中断后使用相同 `--job-id` 和相同内容包恢复；不得手工删除状态来"重新开始"。任务会核对内容指纹、任务空间编号和稳定名称，防止进入其他视频的页面。/ Task state lives in `~/.video-publisher/v2-jobs/` by default. Resume after interruption with the same `--job-id` and content package; never delete state to "restart". Tasks verify content fingerprints, task-space IDs and stable names to avoid landing on another video's page.

若任一平台返回 `INPUT_CHANNEL_BROKEN`，说明 Ego Lite 共享输入通道已断开。本轮应等待已启动任务结束，跳过所有后续上传和页面修改，只做最终只读核验；Ego Lite 恢复后再用同一任务命令续跑。/ If any platform returns `INPUT_CHANNEL_BROKEN`, Ego Lite's shared input channel is down. Finish already-started tasks, skip all further uploads and page mutations, and run only final read-only verification; resume with the same task command after Ego Lite recovers.

## B站旧草稿处理 / Bilibili Stale-Draft Handling

出现"继续编辑"时，不能直接当作空白上传页：/ When "continue editing" appears, never treat it as a blank upload page:

1. 打开"继续编辑"。/ Open "continue editing".
2. 若恢复草稿的文件名或标题与当前内容包一致，复用该草稿。/ If the recovered draft's file name or title matches the current content package, reuse it.
3. 若属于其他视频，先"存草稿"，返回干净上传页并确认旧编辑器已关闭。/ If it belongs to another video, save it as a draft first, return to a clean upload page, and confirm the old editor is closed.
4. 只有确认页面干净后，才上传目标视频。/ Upload the target video only after the page is confirmed clean.

必须区分"页面里已有某个视频"和"页面里已有当前目标视频"。/ Always distinguish "a video exists on the page" from "the current target video exists on the page".

## 阻塞状态 / Blocked States

保留并向用户说明明确阻塞码，不得用笼统的"未就绪"掩盖原因：/ Keep and explain explicit block codes instead of a vague "not ready":

```text
AUTH_REQUIRED              需要用户登录 / user login required
USER_CONTROL               用户正在控制任务空间 / user is controlling the task space
FOREIGN_DRAFT               页面中是其他视频草稿 / the page holds another video's draft
UPLOAD_NOT_STARTED          上传未真正开始 / upload never really started
UPLOAD_STALLED              上传长时间无进展 / upload stalled with no progress
RISK_CONTROL                平台风控或验证码 / platform risk-control or CAPTCHA
SELECTOR_DRIFT              页面结构变化，现有流程无法可靠定位 / page structure changed; current flow can't locate reliably
STATE_AMBIGUOUS             页面状态无法安全判定 / page state can't be safely determined
INPUT_CHANNEL_BROKEN        Ego Lite 输入通道中断 / Ego Lite input channel broken
PLATFORM_REJECTED_ASSET     视频不满足平台限制 / video violates platform limits
ACTION_FAILED               页面动作执行失败且未通过验证 / page action failed verification
```

只有登录、验证码、风控或明确人工接管需要用户立即介入。其他情况应优先保持任务状态，方便安全恢复。/ Only login, CAPTCHA, risk-control, or explicit human takeover need immediate user attention. Otherwise preserve task state for safe recovery.

## 自定义发布流程 / Customizing Publish Workflows

用户要求新增、删除、调整某个平台步骤时，先阅读 [`references/customizing-workflows.md`](references/customizing-workflows.md)。任何扩展都必须遵循：/ When the user wants to add, remove, or adjust a platform step, read [`references/customizing-workflows.md`](references/customizing-workflows.md) first. Every extension must follow:

```text
inspect（读取当前真实状态 / read the current real state）
→ action（只执行必要动作 / perform only necessary actions）
→ verify（独立验证结果 / verify results independently）
```

扩展必须幂等：目标状态已经满足时不得重复点击。个人账号数据、Cookie、固定坐标、绝对个人路径和任意浏览器脚本不得写入可分享 Skill。/ Extensions must be idempotent: never click again when the target state already holds. Personal account data, cookies, fixed coordinates, absolute personal paths, and arbitrary browser scripts must never be written into the shareable Skill.

## 浏览器与平台开发规则 / Browser & Platform Development Rules

- 所有真实创作者页面操作必须使用 `ego-browser`，不得回退到其他浏览器控制方式。/ All real creator-page operations must use `ego-browser`; never fall back to other browser-control methods.
- 每个平台使用一个持久任务空间；生产浏览器控制不得委托给子 Agent。/ One persistent task space per platform; production browser control must not be delegated to sub-agents.
- 上传、修改、核验期间不要关闭任务空间，默认留给用户复核。/ Keep task spaces open during upload, mutation and verification; leave them for user review by default.
- 只有维护运行器返回明确阻塞后，才允许用手写 Ego 脚本做范围受限的诊断。/ Only after a maintenance runner returns an explicit block may handwritten Ego scripts be used for scoped diagnostics.
- 修改平台适配器前，先读 [`references/platform-common.md`](references/platform-common.md)、[`references/ego-browser-workflow.md`](references/ego-browser-workflow.md) 和对应平台说明。/ Before modifying platform adapters, read [`references/platform-common.md`](references/platform-common.md), [`references/ego-browser-workflow.md`](references/ego-browser-workflow.md), and the platform-specific docs.
- 平台页面行为的验收必须来自真实登录页面；单元测试只能验证编排、模型与解析逻辑。/ Acceptance of platform page behavior must come from real logged-in pages; unit tests only verify orchestration, model and parsing logic.

## 维护与验收 / Maintenance & Acceptance

本地静态检查与测试：/ Local static checks and tests:

```bash
node --check scripts/v2/publisher.mjs
node --check scripts/v2/run-platform.mjs
for file in scripts/v2/platforms/*.mjs scripts/v2/ego/*.mjs scripts/v2/lib/*.mjs; do node --check "$file"; done
node --test scripts/tests/*.test.mjs scripts/v2/tests/*.test.mjs
```

修改真实页面适配器后，还必须：/ After modifying real-page adapters, also:

1. 在真实登录页面验证初始状态、动作与结果；/ verify initial state, actions, and results on a real logged-in page;
2. 再次运行并确认不会重复修改；/ run again and confirm no repeated mutations;
3. 验证中断恢复；/ verify interruption recovery;
4. 运行完整目标平台编排，确认共享浏览器和并发调度无冲突；/ run the full target-platform orchestration and confirm no shared-browser or concurrency conflicts;
5. 确认所有平台均为 `READY`，保护已启用、阻止次数为 0、最终发布未点击。/ confirm every platform is `READY`, guards armed, zero blocked attempts, final publish unclicked.

## 参考资料 / References

按需读取，不要一次加载全部文档：/ Read on demand; don't load every document at once:

- [`references/environment.md`](references/environment.md)：运行环境、依赖和安装前检查。/ Runtime environment, dependencies, pre-install checks.
- [`references/configuration.md`](references/configuration.md)：个人配置、首次引导、优先级和隐私边界。/ Personal config, onboarding, precedence, privacy boundaries.
- [`references/intake-workflow.md`](references/intake-workflow.md)：视频受理、内容分析和内容包确认。/ Video intake, content analysis, content-package confirmation.
- [`references/cover-workflow.md`](references/cover-workflow.md)：现有封面映射、上传与结果凭据。/ Existing-cover mapping, upload, result credentials.
- [`references/ego-browser-workflow.md`](references/ego-browser-workflow.md)：Ego Lite 任务空间、文件上传和故障恢复。/ Ego Lite task spaces, file uploads, failure recovery.
- [`references/platform-common.md`](references/platform-common.md)：共享安全门、阶段、证据和阻塞模型。/ Shared safety gates, phases, evidence, blocking model.
- [`references/scripts.md`](references/scripts.md)：生产、校验、诊断和测试命令。/ Production, validation, diagnostics, test commands.
- [`references/customizing-workflows.md`](references/customizing-workflows.md)：发布步骤扩展规范。/ Publish-step extension rules.
- `references/platform-*.md`：各平台适配规则。/ Platform-specific adapter rules.

默认视频目录来自个人配置，也可以用 `VIDEO_PUBLISHER_SOURCE_DIR` 临时覆盖。当前请求中的明确选择优先于内容包字段，内容包字段优先于个人配置，但平台必须已在 `availablePlatforms` 中声明。/ The default video directory comes from personal config and can be overridden per-run with `VIDEO_PUBLISHER_SOURCE_DIR`. Explicit choices in the current request beat content-package fields, which beat personal config — but every platform must be declared in `availablePlatforms`.
