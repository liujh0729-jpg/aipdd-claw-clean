> **EN:** WorkBuddy integration guide: install as a directory-type skill; WorkBuddy reads the root SKILL.md and calls scripts/ commands per its flow.
>
# WorkBuddy 集成指南

本项目可以作为目录型 Skill 安装到 WorkBuddy。WorkBuddy 读取根目录 `SKILL.md` 判断触发场景，并按其中流程调用 `scripts/` 下的命令。

## 安装

1. 将整个仓库复制或克隆到 WorkBuddy 的 Skills 目录，目录名建议使用 `post-to-xhs`。
2. 在该目录安装依赖：

```bash
python -m pip install -r requirements.txt
```

3. 确保执行环境已安装 Google Chrome 或 Chromium。
4. 重载 WorkBuddy 的 Skills，确认可以识别 `post-to-xhs`。

不要只复制 `SKILL.md`；运行时还需要 `scripts/`、`requirements.txt` 和 `config/`。

## 目录与工作区约定

WorkBuddy 执行 Skill 时，当前目录可能是用户项目而不是 Skill 安装目录。因此调用方应先取得 `SKILL.md` 所在目录 `SKILL_DIR`，再以绝对路径执行脚本：

```bash
python "$SKILL_DIR/scripts/cdp_publish.py" check-login
```

标题、正文、下载素材、CSV 等任务文件应放在 WorkBuddy 当前任务的可写工作区，再通过绝对路径传给脚本；不要把临时文件写入 Skill 安装目录。

## 首次登录

有图形界面的本机环境可直接打开登录页：

```bash
python "$SKILL_DIR/scripts/cdp_publish.py" login
```

需要让远程用户扫码时，可获取二维码数据：

```bash
python "$SKILL_DIR/scripts/cdp_publish.py" get-login-qrcode
```

返回中的 `qrcode_data_url` 可供支持图片展示的 WorkBuddy 客户端显示。二维码过期后重新执行命令，不要缓存二维码。

## 典型调用

检查登录：

```bash
python "$SKILL_DIR/scripts/cdp_publish.py" check-login
```

搜索笔记：

```bash
python "$SKILL_DIR/scripts/cdp_publish.py" search-feeds --keyword "春招"
```

预览图文，等待人工确认：

```bash
python "$SKILL_DIR/scripts/publish_pipeline.py" --preview \
  --title-file "/absolute/workspace/title.txt" \
  --content-file "/absolute/workspace/content.txt" \
  --image-urls "https://example.com/1.jpg"
```

用户确认后发布：

```bash
python "$SKILL_DIR/scripts/publish_pipeline.py" --headless \
  --title-file "/absolute/workspace/title.txt" \
  --content-file "/absolute/workspace/content.txt" \
  --image-urls "https://example.com/1.jpg"
```

## 远程 CDP

如果 WorkBuddy 所在环境没有本机 Chrome，可以连接用户明确提供的远程 Chrome：

```bash
python "$SKILL_DIR/scripts/cdp_publish.py" \
  --host 10.0.0.12 --port 9222 check-login
```

远程调试端口具有较高权限，只应在可信网络中使用，不应直接暴露到公网。

## 行为约束

- 发布前必须展示最终标题、正文和媒体并取得用户明确确认。
- “打开浏览器、检查登录、获取二维码”不能触发发布。
- 图文必须有图片，视频必须有视频，二者不能混合。
- 优先解析命令的 JSON 输出，失败信息应原样反馈，不得把填充完成当作发布成功。
- 登录资料和 Cookie 位于本机 Chrome Profile；不要上传、输出或提交这些数据。
