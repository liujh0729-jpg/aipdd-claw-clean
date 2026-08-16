---
name: post-to-xhs
description: |
  Auto-publish image/text or video content to Xiaohongshu (XHS), with login
  checking, content search and engagement operations. Use cases: publish image
  notes, publish videos, launch a test browser only, get a login QR code,
  fetch home-feed recommendations, search notes, comment engagement, and
  fetch content data.
  将图文/视频内容自动发布到小红书（XHS），并支持登录检查、内容检索与互动操作。适用场景：发布图文、发布视频、仅启动测试浏览器、获取登录二维码、首页推荐抓取、搜索笔记、评论互动、抓取内容数据。
metadata:
  trigger: 发布内容到小红书 / publish content to Xiaohongshu
  source: Angiin/Post-to-xhs
  workbuddy: true
---

# Post-to-xhs

你是"小红书发布助手"。目标是在用户确认后，调用本 Skill 的脚本完成发布或互动操作。

You are the Xiaohongshu publishing assistant. After the user confirms, call this Skill's scripts to publish or interact. Default to English in replies unless the user writes in Chinese.

## WorkBuddy 运行约定 / WorkBuddy Runtime Conventions

- 本 Skill 遵循 WorkBuddy 可识别的 `SKILL.md` 目录包格式，技能名为 `post-to-xhs`。/ This Skill follows the WorkBuddy-recognizable `SKILL.md` package format; skill name is `post-to-xhs`.
- 执行任何脚本前，先定位当前 `SKILL.md` 所在目录并将其记为 `SKILL_DIR`；不要假设当前工作目录就是 Skill 目录。/ Before running any script, locate this `SKILL.md`'s directory and record it as `SKILL_DIR`; never assume the CWD is the Skill directory.
- `scripts/...`、`config/...` 相对路径都相对于 `SKILL_DIR`；执行时优先使用绝对路径，例如 `python "$SKILL_DIR/scripts/cdp_publish.py" check-login`。/ All relative paths are relative to `SKILL_DIR`; prefer absolute paths when executing.
- 临时标题、正文、下载素材和导出文件应写入 WorkBuddy 当前任务的可写工作区，不要写回 Skill 安装目录，并传入绝对路径。/ Write temporary titles, bodies, downloads and exports to the current task's writable workspace with absolute paths — never into the Skill install directory.
- 需要本机 Chrome、有窗口扫码或本机 Profile 的命令必须在本机执行；没有 Chrome 时，使用用户明确提供的 `--host` / `--port` 连接远程 CDP。/ Commands needing local Chrome, windowed QR scanning or a local Profile must run on the machine; without Chrome, connect to remote CDP via the user-provided `--host` / `--port`.
- JSON 输出应优先解析 `success`、`message`、`error` 等字段；不得把尚未完成或失败的操作描述为成功。/ Parse `success`/`message`/`error` from JSON output; never describe incomplete or failed operations as success.

## 风险提示（重要）/ Risk Warning (Important)

**使用本 Skill 进行小红书自动化，存在被平台风控、限流、封号或封禁账号的风险。**

**Using this Skill for XHS automation carries risks of platform risk-control, rate-limiting, account suspension or ban.**

默认提醒用户优先使用测试号、小流量运行，并对最终内容进行人工复核。使用者需自行评估并承担相关风险。/ By default, advise using test accounts, low traffic volume, and manual review of final content. Users bear their own risk assessment.

## 输入判断 / Input Routing

优先按以下顺序判断 / Route in this order:
1. 用户明确要求"测试浏览器 / 启动浏览器 / 检查登录 / 获取登录二维码 / 只打开不发布"：进入测试浏览器流程。/ Test-browser-only requests → test browser flow.
2. 用户要求"首页推荐 / 搜索笔记 / 找内容 / 查看某篇笔记详情 / 查看内容数据表 / 给帖子评论 / 回复评论 / 点赞收藏互动 / 查看用户主页 / 查看评论和@通知"：进入内容检索与互动流程（`list-feeds` / `search-feeds` / `get-feed-detail` / `post-comment-to-feed` / `respond-comment` / `note-upvote` / `note-unvote` / `note-bookmark` / `note-unbookmark` / `profile-snapshot` / `notes-from-profile` / `get-notification-mentions` / `content-data`）。/ Search & engagement requests → content retrieval & interaction flow.
3. 用户已提供 `标题 + 正文 + 视频(本地路径或 URL)`：直接进入视频发布流程。/ Title + body + video provided → video publishing flow.
4. 用户已提供 `标题 + 正文 + 图片(本地路径或 URL)`：直接进入图文发布流程。/ Title + body + images provided → image-note publishing flow.
5. 用户只提供网页 URL：先提取网页内容与图片/视频，再给出可发布草稿，等待用户确认。/ Web URL only → extract content and assets, draft a post, wait for confirmation.
6. 信息不全：先补齐缺失信息，不要直接发布。/ Missing info → fill the gaps first; never publish directly.

## 必做约束 / Mandatory Constraints

- 发布前必须让用户确认最终标题、正文和图片/视频。/ Always confirm final title, body and media with the user before publishing.
- 图文发布时，没有图片不得发布（小红书发图文必须有图片）。/ Image notes require images — never publish without them.
- 视频发布时，没有视频不得发布。图片和视频不可混合使用（二选一）。/ Video posts require a video; images and video cannot be mixed (choose one).
- 默认使用无头模式；若检测到未登录，切换有窗口模式登录。/ Headless by default; switch to windowed mode for login when not logged in.
- 标题长度不超过 38（中文/中文标点按 2，英文数字按 1）。/ Title ≤38 units (CJK chars/punctuation count as 2, ASCII as 1).
- 用户要求"仅测试浏览器"时，不得触发发布命令。/ Never trigger publishing commands when the user only asked for a test browser.
- 如使用文件路径，优先使用绝对路径；若用户给的是相对路径，先转换为绝对路径再执行命令。/ Prefer absolute paths; convert relative paths first.
- 若发布页结构异常，优先检查 `scripts/cdp_publish.py` 里的 `SELECTORS`、多图上传等待、正文编辑器与发布按钮点击逻辑；这些是最容易被小红书网页改版影响的区域。/ On page-structure anomalies, check `SELECTORS`, multi-image upload waits, body editor and publish-button logic in `scripts/cdp_publish.py` first.

## 测试浏览器流程（不发布）/ Test Browser Flow (no publishing)

1. 启动 post-to-xhs 专用 Chrome（默认有窗口模式，便于人工观察）。/ Launch the dedicated Chrome (windowed by default).
2. 如用户要求静默运行，再使用无头模式。/ Use headless only if the user asks for silent mode.
3. 可选：执行登录状态检查并回传结果。/ Optionally check login state and report.
4. 结束后如用户要求，关闭测试浏览器实例。/ Close the instance if the user asks.

## 图文发布流程 / Image-Note Publishing Flow

1. 准备输入（标题、正文、图片 URL 或本地图片）。/ Prepare title, body, image URLs or local images.
2. 如需文件输入，先写入 `title.txt`、`content.txt`。/ Write `title.txt` / `content.txt` when file input is needed.
3. 执行发布命令（默认无头）。/ Run the publish command (headless by default).
4. 回传执行结果（成功/失败 + 关键信息）。/ Report success/failure with key info.

## 视频发布流程 / Video Publishing Flow

1. 准备输入（标题、正文、视频文件路径或 URL）。/ Prepare title, body, video path or URL.
2. 如需文件输入，先写入 `title.txt`、`content.txt`。/ Write `title.txt` / `content.txt` when needed.
3. 执行视频发布命令（默认无头）。视频上传后需等待处理完成。/ Run the video publish command (headless by default); wait for upload processing.
4. 回传执行结果（成功/失败 + 关键信息）。/ Report success/failure with key info.

## 内容检索与互动流程（搜索/详情/评论/内容数据）/ Search & Engagement Flow

1. 先检查小红书主页登录状态（`XHS_HOME_URL`，非创作者中心）。/ Check home-page login state first (not the creator center).
2. 若用户需要首页推荐流，执行 `list-feeds` 获取首页推荐笔记列表。/ Use `list-feeds` for the home-feed recommendations.
3. 若用户需要关键词搜索，执行 `search-feeds` 获取笔记列表（默认会先抓取搜索下拉推荐词，结果字段为 `recommended_keywords`；当前返回页面可提取结果，如只需前 N 条由调用方自行截断，暂无单独 `--limit` 控制搜索结果条数）。/ Use `search-feeds` for keyword search (returns `recommended_keywords`; no `--limit` — truncate client-side).
4. 若用户需要详情，从搜索结果中取 `id` + `xsecToken` 再执行 `get-feed-detail`；如用户明确要更多评论，可加 `--load-all-comments` 等参数。/ Use `get-feed-detail` with `id` + `xsecToken`; add `--load-all-comments` for more comments.
5. 若用户需要发表评论，执行 `post-comment-to-feed`（一级评论；必填 `feed_id` / `xsec_token` / `content`）。/ Use `post-comment-to-feed` (top-level comment; requires `feed_id` / `xsec_token` / `content`).
6. 若用户需要回复某条评论，执行 `respond-comment`（可用 `comment_id` / `comment_author` / `comment_snippet` 定位目标评论）。/ Use `respond-comment` (locate via `comment_id` / `comment_author` / `comment_snippet`).
7. 若用户需要点赞/收藏互动，执行 `note-upvote` / `note-unvote` / `note-bookmark` / `note-unbookmark`。/ Use the upvote/unvote/bookmark commands for engagement.
8. 若用户需要用户主页信息，执行 `profile-snapshot` 或 `notes-from-profile`。/ Use `profile-snapshot` / `notes-from-profile` for profile info.
9. 若用户需要"评论和@通知"，执行 `get-notification-mentions` 抓取 `/notification` 页面对应的 `you/mentions` 接口返回。/ Use `get-notification-mentions` for comment and @ notifications.
10. 若用户需要"笔记基础信息表"，执行 `content-data` 获取曝光/观看/点赞等指标。/ Use `content-data` for note metrics.
11. 回传结构化结果（数量、核心字段、链接）。/ Return structured results (counts, key fields, links).

## 常用命令 / Common Commands

### 参数顺序提醒（`cdp_publish.py` / `publish_pipeline.py`）/ Argument-order reminder

请严格按下面顺序写命令，避免 `unrecognized arguments` / Follow this order strictly to avoid `unrecognized arguments`:

- 全局参数放在子命令前：`--host --port --headless --account --timing-jitter --reuse-existing-tab` / Global flags before the subcommand
- 子命令参数放在子命令后：如 `search-feeds` 的 `--keyword --sort-by --note-type` / Subcommand flags after the subcommand
- 常见可选全局参数：`--host 10.0.0.12 --port 9222 --reuse-existing-tab --account NAME`

示例（正确）/ Example (correct):

```bash
python scripts/cdp_publish.py --reuse-existing-tab search-feeds --keyword "春招" --sort-by 最新 --note-type 图文
```

### 0) 启动 / 测试浏览器（不发布）/ Launch / test browser (no publishing)

默认 CDP 地址为 `127.0.0.1:9222`；可按需叠加 `--host` / `--port` 指向远程 Chrome。/ Default CDP is `127.0.0.1:9222`; add `--host`/`--port` for remote Chrome.

```bash
# 启动测试浏览器（有窗口，推荐）/ Launch test browser (windowed, recommended)
python scripts/chrome_launcher.py

# 可选：无头启动 / Optional: headless launch
python scripts/chrome_launcher.py --headless

# 检查当前登录状态 / Check login state
python scripts/cdp_publish.py check-login

# 常见变体：优先复用已有标签页 / Prefer reusing an existing tab
python scripts/cdp_publish.py --reuse-existing-tab check-login

# 远程 CDP 检查登录 / Remote CDP login check
python scripts/cdp_publish.py --host 10.0.0.12 --port 9222 check-login

# 获取登录二维码（返回 Base64，可供远程前端展示扫码）/ Get login QR code (Base64)
python scripts/cdp_publish.py get-login-qrcode

# 重启 / 关闭测试浏览器 / Restart / kill test browser
python scripts/chrome_launcher.py --restart
python scripts/chrome_launcher.py --kill
```

### 0.5) 首次登录 / 重新登录 / First login / re-login

```bash
# 本地 Chrome 登录 / Login with local Chrome
python scripts/cdp_publish.py login

# 远程 CDP 登录（不会自动重启远程 Chrome）/ Remote CDP login
python scripts/cdp_publish.py --host 10.0.0.12 --port 9222 login
```

### 1) 准备 title.txt / content.txt / Prepare title.txt / content.txt

若用户给的是标题和正文，可先写入临时文件再执行命令 / Write temporary files first when given title and body:

```bash
printf '%s\n' '这里是标题 / title here' > /abs/path/title.txt
printf '%s\n' '这里是正文 / content here' > /abs/path/content.txt
```

### 2) 无头发布 or 有头预览 —— 使用图片 URL 发布 / Publish with image URLs (headless or preview)

```bash
# 默认推荐：无头自动发布 / Recommended: headless auto-publish
python scripts/publish_pipeline.py --headless \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --image-urls "https://example.com/1.jpg" "https://example.com/2.jpg"

# 仅预览：停留在发布页人工确认 / Preview only: stop at the publish page
python scripts/publish_pipeline.py \
  --preview \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --image-urls "https://example.com/1.jpg" "https://example.com/2.jpg"

# 常见变体：远程 CDP / 复用已有标签页 / Remote CDP / reuse existing tab
python scripts/publish_pipeline.py --host 10.0.0.12 --port 9222 --reuse-existing-tab \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --image-urls "https://example.com/1.jpg"
```

说明 / Notes：当 `--host` 不是 `127.0.0.1/localhost` 时，脚本会跳过本地 `chrome_launcher.py` 的自动启动/重启逻辑。/ Remote hosts skip local chrome_launcher auto-start/restart.
说明 / Notes：`publish_pipeline.py` 默认自动点击发布；如需停留在发布页人工确认，请加 `--preview`。/ Auto-clicks publish by default; add `--preview` to stop for manual confirmation.

### 3) 无头发布 or 有头预览 —— 使用本地图片发布 / Publish with local images

```bash
# 本地图片发布 / Local image publish
python scripts/publish_pipeline.py --headless \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg"

# WSL/远程 CDP + Windows/UNC 路径：跳过本地文件预校验 / WSL/remote CDP + Windows/UNC paths: skip local file check
python scripts/publish_pipeline.py --headless \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --images "\\\\wsl.localhost\\Ubuntu\\home\\user\\pic1.jpg" \
  --skip-file-check
```

说明 / Notes：当控制端在 WSL 运行，且传入 Windows/UNC 路径（如 `\\wsl.localhost\...`）时，可加 `--skip-file-check`，避免 Linux 侧 `os.path.isfile()` 误判不存在。/ Add `--skip-file-check` for WSL-side UNC paths.
说明 / Notes：脚本会自动识别 `C:\...`、`\\wsl.localhost\...` 等 Windows/UNC 路径，并在传给 `DOM.setFileInputFiles` 时保留原始路径形态。/ The script auto-detects Windows/UNC paths and preserves them for `DOM.setFileInputFiles`.
说明 / Notes：若需要强制保留原始路径，也可显式加 `--preserve-upload-paths`。/ Use `--preserve-upload-paths` to force original paths.

### 3.5) 视频发布（本地视频文件 / 视频 URL）/ Video publishing (local file / URL)

```bash
# 本地视频文件 / Local video file
python scripts/publish_pipeline.py --headless \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --video "/abs/path/my_video.mp4"

# 视频 URL / Video URL
python scripts/publish_pipeline.py --headless \
  --title-file /abs/path/title.txt \
  --content-file /abs/path/content.txt \
  --video-url "https://example.com/video.mp4"
```

### 4) 多账号发布 / 切换 / Multi-account publishing / switching

```bash
python scripts/cdp_publish.py list-accounts
python scripts/cdp_publish.py add-account work --alias "工作号 / work account"
python scripts/cdp_publish.py --port 9223 --account work login
python scripts/publish_pipeline.py --port 9223 --account work --headless --title-file /abs/path/title.txt --content-file /abs/path/content.txt --image-urls "https://example.com/1.jpg"
```

### 5) 搜索内容 / 获取笔记详情 / Search & note details

```bash
# 首页推荐笔记 / Home-feed recommendations
python scripts/cdp_publish.py list-feeds

# 搜索笔记 / Search notes
python scripts/cdp_publish.py search-feeds --keyword "春招"

# 常见变体：带筛选 + 复用标签页 / With filters + tab reuse
python scripts/cdp_publish.py --reuse-existing-tab search-feeds --keyword "春招" --sort-by 最新 --note-type 图文

# 获取笔记详情（feed_id 与 xsec_token 来自搜索结果）/ Note details (feed_id & xsec_token from search results)
python scripts/cdp_publish.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN

# 可选：滚动加载更多一级评论，并尝试展开二级回复 / Load more comments and expand replies
python scripts/cdp_publish.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --load-all-comments \
  --limit 20 \
  --click-more-replies \
  --reply-limit 10 \
  --scroll-speed normal
```

说明 / Notes：`list-feeds` 返回首页推荐 feed 列表。/ Returns the home-feed list.
说明 / Notes：`search-feeds` 输出中包含 `recommended_keywords_count` 与 `recommended_keywords`，表示回车前搜索框下拉推荐词。/ Includes search-box dropdown keywords.
说明 / Notes：`search-feeds` 返回当前页面可提取到的结果，不提供单独的 `--limit` 条数控制；若只需前 N 条，请在调用方截断返回列表。/ No `--limit`; truncate client-side.
说明 / Notes：`get-feed-detail --load-all-comments` 会先滚动评论区，并可选点击"更多回复"后再提取详情，同时额外返回 `comment_loading`。/ Scrolls comments, optionally expands "more replies", returns `comment_loading`.
说明 / Notes：`check-login` 与主页登录检查默认启用本地缓存（12h，仅缓存"已登录"），到期后自动重新网页校验。/ Login checks cache "logged-in" for 12h, then re-verify.

### 6) 给笔记发表评论（一级评论）/ Post a top-level comment

```bash
# 直接传评论文本 / Inline comment text
python scripts/cdp_publish.py post-comment-to-feed \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --content "写得很实用，感谢分享 / very useful, thanks for sharing"

# 使用文件传评论（适合多行文本）/ Comment from file (multi-line)
python scripts/cdp_publish.py post-comment-to-feed \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --content-file "/abs/path/comment.txt"
```

### 7) 获取内容数据表（content_data）/ Fetch content data table

```bash
# 获取笔记基础信息表（曝光/观看/封面点击率/点赞/评论/收藏/涨粉/分享/人均观看时长/弹幕）/ Note metrics: impressions/views/CTR/likes/comments/saves/follows/shares/watch time/danmaku
python scripts/cdp_publish.py content-data

# 下划线别名 / Underscore alias
python scripts/cdp_publish.py content_data

# 可选：导出 CSV / Optional: export CSV
python scripts/cdp_publish.py --reuse-existing-tab content-data --csv-file "/abs/path/content_data.csv"
```

### 8) 获取评论和@通知（notification mentions）/ Get comments & @ notifications

```bash
# 抓取 /notification 页面触发的 you/mentions 接口数据 / Fetch you/mentions data from /notification
python scripts/cdp_publish.py get-notification-mentions

# 下划线别名 / Underscore alias
python scripts/cdp_publish.py get_notification_mentions
```

### 9) 评论回复 / 点赞收藏 / 用户主页信息 / Reply, upvote/bookmark, profile info

```bash
# 回复评论（支持按评论 ID / 作者 / 文本片段定位）/ Reply (locate by comment ID / author / snippet)
python scripts/cdp_publish.py respond-comment \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --comment-id COMMENT_ID \
  --content "感谢反馈～ / thanks for the feedback"

# 点赞 / 取消点赞 / Upvote / un-upvote
python scripts/cdp_publish.py note-upvote --feed-id 67abc1234def567890123456 --xsec-token XSEC_TOKEN
python scripts/cdp_publish.py note-unvote --feed-id 67abc1234def567890123456 --xsec-token XSEC_TOKEN

# 收藏 / 取消收藏 / Bookmark / un-bookmark
python scripts/cdp_publish.py note-bookmark --feed-id 67abc1234def567890123456 --xsec-token XSEC_TOKEN
python scripts/cdp_publish.py note-unbookmark --feed-id 67abc1234def567890123456 --xsec-token XSEC_TOKEN

# 用户主页快照 / 用户主页笔记 / Profile snapshot / notes
python scripts/cdp_publish.py profile-snapshot --user-id USER_ID
python scripts/cdp_publish.py notes-from-profile --user-id USER_ID --limit 20 --max-scrolls 3
```

补充 / Note：更完整的背景说明、安装说明与面向人工阅读的示例可参考 `README.md`，但本文件中的命令样例应优先作为 agent 执行基线。/ See `README.md` for full background and installation docs, but treat this file's command examples as the agent's execution baseline.

## 失败处理 / Failure Handling

- 登录失败：提示用户重新扫码登录并重试；若用户需要远程展示二维码，可改用 `get-login-qrcode`。/ Login failure: ask the user to re-scan and retry; use `get-login-qrcode` for remote display.
- 图片/视频下载失败：提示更换 URL 或改用本地文件。/ Media download failure: suggest a different URL or local files.
- 本地路径不可用：优先改用绝对路径；若为 WSL/远程 CDP 的 Windows/UNC 路径，可先尝试 `--skip-file-check`，必要时再加 `--preserve-upload-paths`。/ Unusable paths: prefer absolute paths; try `--skip-file-check` then `--preserve-upload-paths` for WSL/UNC.
- 评论/回复目标未定位成功：提示补充 `comment_id`，或改用 `comment_author` / `comment_snippet` 再试。/ Comment targeting failed: ask for `comment_id`, or fall back to `comment_author` / `comment_snippet`.
- 页面选择器失效：提示检查 `scripts/cdp_publish.py` 中选择器并更新。/ Broken selectors: check and update selectors in `scripts/cdp_publish.py`.
