> **EN:** Runtime environment & pre-install checklist for Video Publisher: host agent, Node.js, OS, Ego Lite, accounts, local file access, network and disk-space requirements.
>
# 运行环境与安装检查

Video Publisher 是由 Codex / Claude Code 调用的本地 Skill，不是独立的桌面应用，也不是网页服务。它需要 Agent 能够执行本地命令，并通过 Ego Lite 操作真实浏览器中的创作者页面。

## 最低环境

| 项目 | 要求 | 检查方式 |
|---|---|---|
| Agent | Codex 或 Claude Code | 确认当前 Skill 能被加载 |
| Node.js | 20 LTS 或更高版本 | `node --version` |
| Shell | Bash；Windows 使用 WSL2 | `bash --version` |
| 浏览器控制 | Ego Lite 与 `ego-browser` 可用 | `command -v ego-browser` |
| 登录态 | 至少一个已配置平台的创作者账号 | 在 Ego Lite 浏览器中打开对应创作者中心 |
| 文件权限 | Agent 与 Ego Lite 均可读视频/封面 | `test -r "/绝对路径/视频.mp4"` |
| 网络 | 能访问所选平台创作者中心 | 打开对应平台页面确认 |
| 磁盘 | 源视频大小至少 2 倍的可用空间更稳妥 | `df -h` |

## 依赖分析

- **Node.js 内置模块**：脚本使用 `fs`、`path`、子进程和测试模块，不需要第三方 npm 包。
- **Ego Lite**：真实页面自动化的必要依赖。Skill 不应使用 Chrome DevTools、Playwright、Selenium 或其他替代控制器绕过 Ego Lite。
- **媒体工具**：不要求 `ffmpeg` / `ffprobe`；时长检查由脚本读取 ISO BMFF 元数据完成。
- **登录、Cookie、验证码**：不由 Skill 配置或持久化。由用户在 Ego Lite 管理的浏览器中完成。
- **系统权限**：需要对源文件有读取权限，对个人配置目录和任务状态目录有写权限。

## 建议的安装前检查

在 `video-publisher` 目录执行：

```bash
node --version
bash --version
command -v ego-browser
node scripts/config.mjs status
```

若 `ego-browser` 不存在或无法启动，不要开始上传；先安装或修复 Ego Lite。若平台要求重新登录、验证码或二次认证，应停下并让用户在真实浏览器中完成。

## 路径规则

- 视频和封面使用绝对路径；不要依赖当前工作目录猜测文件。
- 文件名含空格、中文、逗号或尾随空格时，不要自行重命名，使用正确的 shell 引号。
- 不要把视频、封面、Cookie、配置和任务状态复制进共享 Skill 目录。
- 配置默认位置为 `~/.config/video-publisher/`，运行状态默认位置为 `~/.video-publisher/v2-jobs/`。

## 可选环境变量

```text
VIDEO_PUBLISHER_CONFIG       覆盖个人配置文件路径
VIDEO_PUBLISHER_SOURCE_DIR   临时覆盖默认视频目录
XDG_CONFIG_HOME              自定义用户配置根目录
```

这些变量只改变本地路径或默认目录，不应保存密码、Cookie、令牌或最终发布授权。

## 失败时的处理

- `AUTH_REQUIRED`：让用户登录对应创作者平台。
- `RISK_CONTROL`：让用户处理验证码或风控，不要无限重试。
- `USER_CONTROL`：等待用户明确说继续。
- `INPUT_CHANNEL_BROKEN`：重启 Ego Lite 后，用同一 `--job-id` 继续。
- `PLATFORM_REJECTED_ASSET`：按平台提示准备合规副本；不自动裁剪、转码或替换原文件。
- `SELECTOR_DRIFT`：保留任务状态，先做只读诊断，不要盲目点击。
