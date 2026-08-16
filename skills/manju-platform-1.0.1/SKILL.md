---
name: manju-platform
description: "Produce scripts, storyboards, character & prop assets, first frames, audio and storyboard videos through the DramaClaw REST API. Use for manhua-drama production, story visualization, script storyboarding, character three-views, prop images, key frames, voice-over and video generation tasks. The user must provide the DramaClaw server address, username and password before first use; the session is saved after first login. 通过漫剧平台（DramaClaw）REST API 完成故事转剧本、剧本转分镜、角色与道具资产、首帧、音频和分镜视频生成。适用于漫剧制作、故事可视化、剧本分镜、角色三视图、道具图、首帧、配音和视频生成任务。使用前需要用户提供 DramaClaw 服务器地址、账号和密码；首次登录后会话会被保存。"
---
# 漫剧平台 Skill / Manju (DramaClaw) Platform Skill

通过 DramaClaw 线上 API 完成漫剧工作流。调用脚本 / Run the manhua-drama workflow through the DramaClaw API. Invocation:

```bash
node {baseDir}/scripts/invoke.mjs --command <command> [options]
```

配置保存在当前 OpenClaw 状态目录下，不会写回 Skill 安装目录。/ Config is stored in the current OpenClaw state directory — never written back into the Skill install directory.

## 绝对规则 / Absolute Rules

- 不保存用户明文密码到日志、回复或项目文件。/ Never store plaintext passwords in logs, replies, or project files.
- 登录成功后只保存会话 Cookie，不保存密码。/ After login, save only the session cookie — never the password.
- 没有默认平台地址。首次使用必须向用户询问平台地址、账号和密码，不能使用预设地址。/ There is no default platform address. On first use you MUST ask the user for the address, username and password; never use a preset address.
- 不输出完整 `st_session` Cookie，只输出脱敏前缀和后缀。/ Never output the full `st_session` cookie — only a masked prefix and suffix.
- 每次操作前检查登录状态；未登录时先引导登录。/ Check login state before every operation; guide the user through login when signed out.
- 用户未提供项目名和集数时，必须先询问，不能猜测。/ When project name or episode number is missing, ask first — never guess.
- 生成类任务通常是异步提交后返回任务状态，不等待直到完成；用户明确要求等待时再轮询。/ Generation tasks are async: submit and return task status without waiting; poll only when the user explicitly asks to wait.
- 只调用公开 API，不直接访问数据库、文件系统或后台服务。/ Only call public APIs — never access databases, the file system, or backend services directly.

## 首次配置 / First-Time Setup

如果用户要求做漫剧、生成剧本、生成视频或任何与漫剧平台相关的任务，先执行 / If the user asks for anything manhua-drama related (generate script, video, etc.), run:

```bash
node {baseDir}/scripts/invoke.mjs --command config
```

如果返回 `configured: false` 或 `required` 不为空，向用户收集 / If it returns `configured: false` or a non-empty `required`, collect from the user:

1. DramaClaw 平台地址（必须由用户提供，没有默认值）/ DramaClaw platform address (user-provided, no default)
2. 账号（用户名）/ Username
3. 密码 / Password

然后执行 / Then run:

```bash
node {baseDir}/scripts/invoke.mjs --command login --username "<username>" --password "<password>" --api-base "<platform-address>"
```

不要把密码写进聊天回复。登录成功后，仅在结果中显示用户名和脱敏 Cookie。/ Never put the password in a chat reply. After login, show only the username and the masked cookie.

登录完成后可验证 / Verify the login with:

```bash
node {baseDir}/scripts/invoke.mjs --command me
```

若返回 401 或未登录，重新引导登录。/ On 401 or not-logged-in, guide re-login.

## 支持的命令 / Supported Commands

### 1. 故事生成剧本 / Story → Script

当用户要求把故事转为剧本时 / When the user asks to turn a story into a script:

1. 确认项目名、集数、故事文本或故事文件路径。/ Confirm project name, episode number, and the story text or file path.
2. 执行 / Run:

```bash
node {baseDir}/scripts/invoke.mjs --command generate-script --project "<project>" --episode "<episode>" --story-text "<story-text>"
```

如果故事在文件里，使用 `--story-file <路径>`。/ If the story is in a file, use `--story-file <path>`.

### 2. 剧本生成分镜、角色说明、道具说明、场景列表、脚本、草图 / Script → Storyboard, Characters, Props, Scenes, Scripts, Sketches

当用户要求基于剧本生成分镜或资产拆解时 / When the user asks to generate storyboards or asset breakdowns from a script:

1. 确认项目名和集数。/ Confirm project name and episode.
2. 先规划场景 / Plan scenes first:

```bash
node {baseDir}/scripts/invoke.mjs --command plan-scenes --project "<project>" --episode "<episode>"
```

3. 再规划道具 / Then plan props:

```bash
node {baseDir}/scripts/invoke.mjs --command plan-props --project "<project>" --episode "<episode>"
```

4. 查看流程状态 / Check pipeline status:

```bash
node {baseDir}/scripts/invoke.mjs --command pipeline-status --project "<project>" --episode "<episode>"
```

返回的内容中通常包含 / The response typically includes:

- 分镜/场景结构 / Storyboard/scene structure
- 角色说明 / Character specs
- 道具说明 / Prop specs
- 场景列表 / Scene list
- 脚本结构 / Script structure
- 草图生成状态 / Sketch generation status

如果用户明确要求生成角色图、道具图、首帧或草图，再进入对应命令。/ Only run the corresponding generation commands when the user explicitly asks for character images, prop images, first frames or sketches.

### 3. 角色说明生成人物三视图、五官垫图、服装图 / Character Specs → Three-Views, Face Ref, Costume Images

当用户要求根据角色说明生成角色资产时 / When the user asks to generate character assets from specs:

1. 确认项目名、集数、角色名或角色 ID。/ Confirm project, episode, and character name or ID.
2. 告诉用户当前通过 DramaClaw API 生成角色相关图像，接口为项目内资产生成接口。/ Tell the user character images are generated via the DramaClaw API's in-project asset generation endpoints.
3. 先执行 `pipeline-status` 查看角色资产状态。/ Run `pipeline-status` first to check asset status.
4. 如果角色资产尚未生成，调用对应角色生成接口；当前通用接口为 / If not generated yet, call the character generation endpoint; the generic one is:

```bash
node {baseDir}/scripts/invoke.mjs --command pipeline-status --project "<project>" --episode "<episode>"
```

若后端返回了角色头像、三视图或一致性图生成入口，再继续发起生成。/ If the backend exposes avatar/three-view/consistency-image generation entries, proceed with generation.

注意：当前 Skill 默认不猜测私有接口路径；如果后端没有明确角色生成任务接口，就先告诉用户可用状态，等待补充文档后再扩展。/ Note: this Skill never guesses private API paths; if the backend has no explicit character-generation endpoint, report the available state and wait for documentation before extending.

### 4. 道具说明生成道具图 / Prop Specs → Prop Images

当用户要求生成道具图时 / When the user asks for prop images:

1. 确认项目名、集数和道具名。/ Confirm project, episode, and prop name.
2. 先查看 `pipeline-status`。/ Check `pipeline-status` first.
3. 如果后端支持道具图生成任务，提交生成任务并返回任务状态。/ If the backend supports prop generation, submit and return the task status.
4. 不支持时明确说明当前接口范围。/ If unsupported, state the current endpoint scope clearly.

### 5. 生成首帧 / Generate First Frames

当用户要求生成首帧时 / When the user asks for first frames:

1. 确认项目名、集数和场景名/场景 ID。/ Confirm project, episode, and scene name/ID.
2. 先查看 `pipeline-status`。/ Check `pipeline-status` first.
3. 如果后端支持首帧生成，提交首帧任务。/ If supported, submit the first-frame task.
4. 返回任务状态，不阻塞等待全部完成。/ Return the task status without blocking until completion.

### 6. 生成音频 / Generate Audio

当用户要求生成配音或音频时 / When the user asks for voice-over or audio:

1. 确认项目名和集数。/ Confirm project and episode.
2. 执行 / Run:

```bash
node {baseDir}/scripts/invoke.mjs --command generate-audio --project "<project>" --episode "<episode>"
```

3. 返回任务状态。/ Return the task status.

### 7. 输入场景、角色、道具和参考图/参考音频生成分镜视频 / Inputs → Storyboard Video

当用户要求生成完整分镜视频时 / When the user asks for a full storyboard video:

1. 确认项目名、集数、场景范围。/ Confirm project, episode, and scene range.
2. 确认是否已具备 / Confirm what's ready:
   - 剧本 / Script
   - 分镜 / Storyboard
   - 角色资产 / Character assets
   - 道具资产 / Prop assets
   - 首帧/草图 / First frames/sketches
   - 音频 / Audio
3. 如缺少关键步骤，先建议补齐对应阶段。/ If key stages are missing, suggest completing them first.
4. 当前 Skill 通过 DramaClaw 项目流程推进视频生成，不直接调用外部模型。/ This Skill drives video generation through the DramaClaw project pipeline — no direct external-model calls.
5. 查看 `pipeline-status` 判断当前阶段。/ Use `pipeline-status` to determine the current stage.
6. 触发视频生成任务并返回任务状态。/ Trigger the video-generation task and return its status.

## 项目与任务状态 / Project & Task Status

任何阶段都可以使用 / At any stage you can use:

```bash
node {baseDir}/scripts/invoke.mjs --command pipeline-status --project "<project>" --episode "<episode>"
```

查看当前进度。/ To check current progress.

列出项目 / List projects:

```bash
node {baseDir}/scripts/invoke.mjs --command projects
```

## 错误处理 / Error Handling

- 401：会话失效，重新引导登录。/ Session expired — guide re-login.
- 403：权限不足，提示检查账号权限。/ Insufficient permissions — ask the user to check account access.
- 404：项目或集数不存在，让用户确认名称。/ Project or episode not found — have the user confirm the names.
- 5xx：服务端错误，建议稍后重试或联系管理员。/ Server error — suggest retrying later or contacting the admin.
- 网络错误：检查平台地址和网络。/ Network error — check the platform address and connectivity.

## 配置位置 / Configuration Location

配置与会话保存在 / Config and session are stored at:

```text
$OPENCLAW_STATE_DIR/skills/manju-platform/
```

若未设置 `OPENCLAW_STATE_DIR`，默认使用 / If `OPENCLAW_STATE_DIR` is unset, the default is:

```text
$USERPROFILE/.openclaw/state/skills/manju-platform/
```

包括 / Containing:

- `config.json`：平台地址、用户名 / platform address, username
- `session.json`：登录会话 Cookie / login session cookie

登出 / Log out:

```bash
node {baseDir}/scripts/invoke.mjs --command logout
```

仅清除当前保存的会话，不删除服务端数据。/ Only clears the saved session — never deletes server-side data.
