# Video Publisher Skill

> **EN:** Video Publisher is a video-publishing Skill for Codex / Claude Code. It takes local videos, drives real creator pages via Ego Lite to prepare publishable drafts on Xiaohongshu, Douyin, Bilibili and WeChat Channels, and by default stops before the final publish button for human review.
>
> 中文说明见下。

Video Publisher 是一个面向 Codex / Claude Code 的视频发布 Skill。它接收本地视频，通过 Ego Lite 操作真实创作者页面，为小红书、抖音、B站和微信视频号准备可发布草稿，并默认停在最终发布按钮前供人工复核。

## 适用场景

- 把一个本地视频同步准备到多个创作者平台；
- 自动填写标题、正文、标签或平台话题；
- 在权利真实确认后填写原创 / 自制声明；
- 上传用户已准备好的竖版、横版封面；
- 从上传中断、浏览器重启或旧草稿状态中恢复；
- 检查每个平台是否已达到可人工发布状态。

## 安装

将整个 `video-publisher` 目录放入 Codex 或 Claude Code 支持的 Skills 目录，保持以下结构：

```text
video-publisher/
├── SKILL.md
├── README.md
├── agents/
├── references/
└── scripts/
```

不要把压缩包生成的 `__MACOSX` 或 `._*` 文件一起安装。

## 使用前准备

1. 安装 Node.js 20 LTS 或更高版本。
2. 安装并启动 Ego Lite，确保 `ego-browser` 命令可用。
3. 在 Ego Lite 管理的真实浏览器中登录至少一个创作者平台。
4. 准备本地视频绝对路径；如需自定义封面，同时准备 3:4 / 4:3 图片。
5. 首次调用时按引导配置已拥有平台、默认平台、视频目录和原创策略。

详细环境要求见 [`references/environment.md`](references/environment.md)。

## 快速自检

在 Skill 目录运行：

```bash
node scripts/validate-skill.mjs
node scripts/config.mjs status
node --test scripts/tests/*.test.mjs scripts/v2/tests/*.test.mjs
```

`validate-skill.mjs` 只检查 Skill 包结构和关键元数据，不会打开浏览器或操作创作者页面。

## 安全说明

- “上传视频”“准备草稿”不等于授权最终发布。
- 默认不点击最终发布按钮，所有平台会保留在人工复核状态。
- 原创 / 自制声明必须来自已配置的真实策略或当前视频的明确确认。
- Cookie、账号密码、令牌、视频路径和发布授权不会写进共享 Skill 包。
- 验证码、账号风控和重新登录必须由用户本人处理。

## 文档入口

- [`SKILL.md`](SKILL.md)：Agent 的主执行说明。
- [`references/environment.md`](references/environment.md)：环境与依赖。
- [`references/configuration.md`](references/configuration.md)：首次配置与个人默认值。
- [`references/intake-workflow.md`](references/intake-workflow.md)：视频受理和内容包。
- [`references/scripts.md`](references/scripts.md)：命令说明。
- [`references/customizing-workflows.md`](references/customizing-workflows.md)：扩展平台流程。
