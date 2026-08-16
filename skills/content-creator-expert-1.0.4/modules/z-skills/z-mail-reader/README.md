# z-mail-reader

> AI Agent 邮件读取 Skill — 通过 IMAP 协议读取邮箱邮件，自动保存附件、内嵌图片，生成内容摘要。

## 功能

- **邮件读取**：通过 IMAP 连接任意邮箱，按时间范围批量拉取邮件
- **附件下载**：自动保存邮件附件到本地
- **图片提取**：保存正文中的 CID 内联图、HTML 外链图、Base64 嵌入图
- **内容摘要**：输出结构化 JSON，方便 Agent 生成 `sum.md` 摘要
- **实时监听**：30 秒轮询检测新邮件，自动处理 + macOS 系统通知
- **编码兼容**：自动处理 UTF-8 / GBK / GB2312 等编码

## 安装

### 1. 复制 Skill 到项目

将 `z-mail-reader` 目录复制到你的 Agent Skill 目录：

```bash
# 示例：复制到项目的 .agent/skills/ 目录
cp -r z-mail-reader /path/to/your-project/.agent/skills/z-mail-reader
```

### 2. 安装依赖

```bash
pip3 install imapclient   # 监听模式需要
```

### 3. 配置邮箱凭证

设置环境变量（推荐写入 `.env` 或 shell 配置）：

```bash
export MAIL_ADDR="your_email@qq.com"
export MAIL_AUTH_CODE="your_imap_auth_code"
export MAIL_IMAP_SERVER="imap.qq.com"   # 默认值，其他邮箱请修改
```

**QQ 邮箱授权码获取：** 设置 → 账户 → POP3/IMAP/SMTP服务 → 开启 → 生成授权码

**其他邮箱 IMAP 地址参考：**

| 邮箱 | IMAP 服务器 |
|------|------------|
| QQ 邮箱 | imap.qq.com |
| 163 邮箱 | imap.163.com |
| Gmail | imap.gmail.com |
| Outlook | imap-mail.outlook.com |

### 4. 注册触发词（AGENTS.md）

在你的 `AGENTS.md` 触发词表中添加：

```markdown
| 读邮件 / 查看邮件 / 本周邮件 / 邮件摘要 / 监听邮件 | `z-mail-reader` |
```

## Agent 使用指南

本 Skill 专为 AI Agent 设计，以下是 Agent 的标准工作流程：

### 读取邮件

```bash
python3 scripts/read_emails.py --days 7 --output-dir ./mails
```

脚本输出 JSON 到 stdout，Agent 解析后为每封邮件生成 `sum.md`。

### 实时监听

```bash
# 启动后台监听
python3 scripts/listen_emails.py --start > /dev/null 2>&1 &

# 查看状态
python3 scripts/listen_emails.py --status

# 停止
python3 scripts/listen_emails.py --stop
```

### 输出目录结构

```
mails/
└── 20260607_1430_邮件主题/
    ├── 附件.pdf                    # 邮件附件
    ├── images/                     # 正文图片
    │   ├── img_001.png             # CID 内联图
    │   └── img_002.jpg             # HTML 外链图
    └── sum.md                      # Agent 生成的摘要
```

### JSON 输出示例

```json
{
  "total": 3,
  "emails": [
    {
      "subject": "项目进度汇报",
      "from": "张三 <zhang@example.com>",
      "date": "2026-06-07 14:30:00",
      "body_preview": "本周完成了...",
      "attachments": [{"filename": "报告.pdf", "path": "...", "size": 12345}],
      "inline_images": [{"filename": "img_001.png", "path": "...", "size": 67890, "source": "cid"}],
      "output_dir": "./mails/20260607_1430_项目进度汇报",
      "has_attachments": true,
      "has_images": true
    }
  ]
}
```

## 参数一览

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--email` | `$MAIL_ADDR` | 邮箱地址 |
| `--auth-code` | `$MAIL_AUTH_CODE` | IMAP 授权码 |
| `--days` | 7 | 最近 N 天 |
| `--since` / `--until` | - | 日期范围 YYYY-MM-DD |
| `--folder` | INBOX | IMAP 文件夹 |
| `--output-dir` | ./mails | 输出目录 |
| `--body-length` | 3000 | 正文截取字符数 |

## 注意事项

- 凭证推荐使用环境变量，避免硬编码
- QQ 邮箱 IMAP IDLE 不推送事件，已用 30 秒轮询兜底
- 超大附件 (>50MB) 可能被 IMAP 服务器跳过
- 监听模式下 PID 和日志保存在 `.runtime/` 目录

## License

MIT
