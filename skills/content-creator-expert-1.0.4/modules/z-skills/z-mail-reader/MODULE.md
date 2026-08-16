---
name: z-mail-reader
description: >-
  Use when user wants to read emails, check inbox, fetch emails via IMAP,
  download email attachments, extract inline images, or summarize email
  content. Also supports real-time polling for new emails with system
  notifications. Triggers include read emails, check inbox, fetch emails,
  email summary, email attachments, mail listener, IMAP, QQ邮箱, Foxmail,
  读邮件, 查看邮件, 收件箱, 邮件摘要, 邮件总结, 查收邮件, and 监听邮件.
---
> **EN:** Email management: read, summarize and download attachments over IMAP.
>

# z-mail-reader — IMAP 邮件读取与实时监听

## Overview

通过 IMAP 协议连接任意邮箱（默认 QQ 邮箱），读取指定时间范围内的邮件，自动下载附件和内嵌图片到本地，并生成邮件内容摘要。支持 **实时轮询监听**，新邮件到达时自动处理并发送系统通知。

**核心原理：** Python `imaplib` → IMAP 服务器 → 解析邮件 → 保存附件/图片 → Agent 生成摘要

## 前置配置

使用前需设置环境变量（或在调用时通过参数传入）：

```bash
export MAIL_IMAP_SERVER="imap.qq.com"    # IMAP 服务器地址
export MAIL_ADDR="your_email@qq.com"     # 邮箱地址
export MAIL_AUTH_CODE="your_auth_code"   # IMAP 授权码（非登录密码）
```

**QQ 邮箱获取授权码方法：** QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP服务 → 开启 IMAP → 生成授权码

## 存储目录

邮件附件、图片和摘要保存到：
```
{output_dir}/
└── YYYYMMDD_HHMM_邮件主题/
    ├── 附件文件...
    ├── images/           # 正文中的图片
    │   ├── img_001.png
    │   └── ...
    └── sum.md            # 邮件摘要（Agent 生成）
```

## 核心流程

```
1. 确定时间范围（本周/最近N天/自定义）
   ↓
2. 运行 Python 脚本连接 IMAP 获取邮件
   ↓
3. 脚本自动：解析邮件头、提取正文、下载附件、保存正文图片
   ↓
4. 为每封邮件创建独立目录（按时间+主题命名）
   ↓
5. Agent 阅读邮件内容，生成 sum.md 摘要
   ↓
6. 汇总输出邮件列表给用户
```

## 脚本位置

```
scripts/
├── read_emails.py      # IMAP 邮件读取
└── listen_emails.py    # 实时轮询监听
```

## 使用方法

### 读取邮件

```bash
python3 scripts/read_emails.py --email "you@qq.com" --auth-code "YOUR_CODE" --days 7
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--email` | 环境变量 `MAIL_ADDR` | 邮箱地址 |
| `--auth-code` | 环境变量 `MAIL_AUTH_CODE` | IMAP 授权码 |
| `--days` | 7 | 读取最近 N 天 |
| `--since` | - | 起始日期 YYYY-MM-DD |
| `--until` | - | 截止日期 YYYY-MM-DD |
| `--folder` | INBOX | 邮件文件夹 |
| `--output-dir` | ./mails | 输出目录 |
| `--limit` | 100 | 最大邮件数量 |
| `--body-length` | 3000 | 正文截取长度 |

### 实时监听

```bash
# 前台监听（Ctrl+C 停止）
python3 scripts/listen_emails.py --start

# 后台监听
python3 scripts/listen_emails.py --start > /dev/null 2>&1 &

# 查看状态
python3 scripts/listen_emails.py --status

# 停止
python3 scripts/listen_emails.py --stop

# 测试一次
python3 scripts/listen_emails.py --once
```

## 输出格式

脚本输出 JSON 到 stdout（进度信息输出到 stderr）：

```json
{
  "total": 5,
  "emails": [
    {
      "subject": "邮件主题",
      "from": "发件人",
      "date": "2026-06-05 14:30:00",
      "body_preview": "正文前3000字...",
      "attachments": [{"filename": "附件.pdf", "path": "...", "size": 12345}],
      "inline_images": [{"filename": "img_001.png", "path": "...", "size": 67890, "source": "cid"}],
      "output_dir": "/path/to/mails/20260605_1430_邮件主题",
      "has_attachments": true,
      "has_images": true
    }
  ]
}
```

### 图片保存说明

脚本自动保存三类正文图片：

| 类型 | source | 说明 |
|------|--------|------|
| CID 内联图片 | `cid` | 邮件 MIME 中 Content-ID 引用的图片 |
| HTML 外链图片 | `url` | `<img src="https://...">` 自动下载 |
| Base64 嵌入图 | `base64` | `data:image/...` 编码的图片 |

## Agent 工作步骤

### 1. 运行脚本获取邮件

```bash
python3 scripts/read_emails.py --days 7
```

### 2. 为每封邮件生成 sum.md

在每封邮件的 `output_dir` 下创建 `sum.md`，包含：邮件元信息、摘要、附件列表、正文图片引用。

### 3. 汇总报告

向用户输出简洁的邮件列表。

## 依赖

- Python 3.8+
- `imapclient`（监听模式需要）：`pip3 install imapclient`

## 注意事项

1. **授权码安全**：推荐用环境变量，不要在输出中显示完整授权码
2. **附件大小**：超大附件（>50MB）可能被 IMAP 服务器跳过
3. **编码兼容**：脚本自动处理 UTF-8/GBK/GB2312 编码
4. **IMAP 限制**：部分邮箱有频率限制，监听轮询间隔默认30秒
5. **QQ邮箱特殊性**：QQ邮箱的 IMAP IDLE 不推送事件，脚本已内置轮询兜底

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 登录失败 | 检查授权码是否正确，邮箱是否开启了 IMAP |
| 找不到邮件 | 尝试扩大时间范围或检查文件夹名称 |
| 附件下载失败 | 可能是超大附件，检查网络连接 |
| 正文乱码 | 脚本已自动处理常见编码 |
| 监听无反应 | QQ邮箱不支持 IDLE 推送，已用30秒轮询兜底 |
