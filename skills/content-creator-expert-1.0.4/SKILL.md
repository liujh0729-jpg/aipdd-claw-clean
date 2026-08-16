---
name: content-creator-expert
description: >
  Essential content-creation toolkit for new-media creators: AI marketing video
  generation, PPT deck creation, WeChat official-account article design, web
  asset collection, document parsing, email management, short-drama script
  evaluation, pre-publish compliance self-check, format conversion
  (Word/Excel), document format unification and handwritten-style
  presentations. Built for compliant marketing scenarios: product promotion,
  brand campaigns, and content operations. Trigger words: make a marketing
  video, make a PPT, WeChat article layout, collect web assets, parse
  documents, read email, evaluate a script, pre-publish check, banned-word
  check, md to word, spreadsheet editing, handwritten PPT, etc.
  新媒体创作人员必备的内容创作工具包，整合AI营销视频生成、PPT演示文稿制作、公众号图文排版、网页素材采集、文档解析、邮件管理、短剧剧本评估、发布前风险自审、格式转换（Word/Excel）、文档格式统一、手写风格演示等功能。适用于产品宣传、品牌推广、内容运营等合规营销场景。触发词：生成营销视频、做视频、产品视频、宣传视频、做PPT、PPT制作、演示文稿、公众号排版、公众号文章、采集素材、网页素材、解析文档、PDF转Word、读邮件、剧本评估、能不能发、审稿、查违禁词、敏感词、限流、发布前检查、被处罚、md转word、表格处理、手写PPT、格式刷、营销内容创作。
---

# 内容创作专家 Skill / Content Creator Expert Skill

面向新媒体创作人员的一站式内容创作工具包，覆盖内容生产的完整流程：素材采集→内容创作→排版输出→质量评估。所有功能均用于合法合规的商业营销内容制作。

A one-stop content-creation toolkit for new-media creators covering the full production loop: asset collection → content creation → layout output → quality evaluation. All features are for legal, compliant commercial marketing content.

## 📦 模块概览 / Module Overview

| 模块 Module | 功能 Function | 适用场景 Use Cases |
|------|------|----------|
| **AI营销视频生成 AI Marketing Video** | 文生/图生视频、首尾帧、多镜头分镜，专业镜头语言 · Text/image-to-video, first/last frames, multi-shot storyboards | 产品展示、品牌宣传、活动预告、广告短片 · Product demos, brand campaigns, event teasers, ad spots |
| **PPT制作 PPT Deck** | 12套主题、千余版式，可编辑PPTX/PDF导出 · 12 themes, 1000+ layouts, editable PPTX/PDF export | 工作汇报、方案演示、产品介绍、培训课件 · Reports, proposals, product intros, training |
| **公众号排版 WeChat MP Layout** | 多套主题+自定义主题，直接粘贴至公众号不掉格式 · Multiple themes + custom themes, paste-ready into WeChat MP | 微信公众号文章、图文推送、品牌内容 · WeChat articles, pushes, brand content |
| **网页素材采集 Web Asset Collection** | 网页正文、图片、链接整理成本地素材包 · Gather web text, images, links into local asset packs | 竞品调研、资料收集、内容参考 · Competitor research, reference gathering |
| **视频学习分析 Video Study Analysis** | 本地视频转录+关键帧+多模态分析生成学习笔记 · Local video transcription + keyframes + multimodal notes | 培训视频学习、内容分析整理 · Training videos, content analysis |
| **文档解析 Document Parsing** | PDF/图片/Office文档转Markdown，大文件自动分割 · PDF/image/Office → Markdown with auto-splitting | 资料整理、文档数字化、内容提取 · Document digitization, extraction |
| **邮件管理 Email Management** | IMAP读取邮件、下载附件、摘要整理 · IMAP reading, attachments, summaries | 商务邮件处理、客户沟通整理 · Business email, client comms |
| **短剧剧本评估 Short-Drama Script Eval** | AI短剧专业评估体系，多维度质量评分 · Professional multi-dimension script scoring | 短剧项目评估、剧本质量审核 · Drama project assessment |
| **发布前自审 Pre-Publish Self-Check** | 抖音/小红书/视频号逐平台风险预检、保意修复、被限流复盘 · Per-platform risk pre-check, meaning-preserving fixes, penalty review | 发布前检查、违禁词筛查、被处罚归因 · Pre-publish checks, banned-word scans |
| **格式转换 Format Conversion** | Markdown转Word、Markdown表格转Excel · MD → Word, MD tables → Excel | 文档格式转换、内容输出 · Document conversion |
| **表格编辑 Spreadsheet Editing** | Excel/CSV文件读取、编辑、数据清洗 · Excel/CSV read, edit, clean | 数据处理、报表制作 · Data processing, reports |
| **Word格式刷 Word Format Brush** | 从模板文档提取格式统一应用到目标文档 · Extract template formatting and apply to targets | 文档格式规范化、品牌文档统一 · Document standardization |
| **手写风格演示 Handwritten Presentation** | Notability风格手写HTML幻灯片/动画视频 · Notability-style handwritten HTML slides/animated video | 教学课件、知识分享、趣味演示 · Teaching, sharing, fun demos |
| **资料问答 Grounded Q&A** | 本地资料多维度检索，证据绑定回答 · Multi-dimensional local retrieval with evidence-bound answers | 内部知识库问答、资料查询 · Internal KB Q&A |

## 🚀 快速路由 / Quick Routing

根据用户需求选择对应模块 / Route to modules by user need:

### 1. AI营销视频生成 / AI Marketing Video
当用户需要"生成视频""做个产品视频""宣传视频""广告片""产品展示视频"时 / When the user asks to generate a product/promo/ad video:
- 读取 `modules/seedance/MODULE.md` / Read `modules/seedance/MODULE.md`
- 支持文生视频、图生视频、首尾帧控制 / Text-to-video, image-to-video, first/last-frame control
- 需要配置：`NEWAPI_BASE_URL`、`NEWAPI_API_KEY` / Requires: `NEWAPI_BASE_URL`, `NEWAPI_API_KEY`
- 模块路径：`modules/seedance/`
- ⚠️ 仅限制作合法合规的营销宣传内容，遵守内容安全规范 / Marketing content only; follow content-safety rules

### 2. PPT演示文稿制作 / PPT Deck Creation
当用户需要"PPT""演示文稿""幻灯片""汇报""方案"时 / When the user needs a PPT/deck/proposal:
- 读取 `modules/dashi-ppt/MODULE.md` / Read `modules/dashi-ppt/MODULE.md`
- 需要：Node.js 20+、Chrome浏览器、`DASHI_PPT_PROJECT_PATH`配置 / Requires: Node.js 20+, Chrome, `DASHI_PPT_PROJECT_PATH`
- 模块路径：`modules/dashi-ppt/`

### 3. 公众号图文排版 / WeChat MP Article Layout
当用户需要"公众号排版""微信文章""图文推送"时 / When the user needs WeChat article layout:
- 读取 `modules/gzh-design/MODULE.md` / Read `modules/gzh-design/MODULE.md`
- 支持Markdown/Word/PDF/纯文本输入 / Accepts Markdown/Word/PDF/plain text
- 模块路径：`modules/gzh-design/`

### 4. 网页素材采集 / Web Asset Collection
当用户需要"采集网页""收集素材""网页内容保存到本地"时 / When the user needs to collect web assets:
- 读取 `modules/z-skills/z-web-pack/MODULE.md` / Read `modules/z-skills/z-web-pack/MODULE.md`
- 模块路径：`modules/z-skills/z-web-pack/`
- ⚠️ 仅采集公开可访问的内容，尊重知识产权 / Publicly accessible content only; respect IP

### 5. 视频学习分析 / Video Study Analysis
当用户需要"分析本地视频""视频学习总结""培训视频整理笔记"时 / When the user needs local video analysis:
- 读取 `modules/z-skills/z-video-study-webpage-qwen/MODULE.md` / Read its MODULE.md
- 需要配置：`DASHSCOPE_API_KEY` / Requires `DASHSCOPE_API_KEY`
- 模块路径：`modules/z-skills/z-video-study-webpage-qwen/`
- ⚠️ 仅分析用户拥有版权或已授权的视频内容 / Only analyze videos the user owns or is authorized to use

### 6. 文档解析 / Document Parsing
当用户需要"解析PDF""PDF转Markdown""文档识别""扫描件转文字"时 / When the user needs PDF/Markdown/OCR parsing:
- 读取 `modules/z-skills/z-smart-xparse/MODULE.md` / Read its MODULE.md
- 模块路径：`modules/z-skills/z-smart-xparse/`

### 7. 邮件管理 / Email Management
当用户需要"读邮件""邮件摘要""查收邮件""下载附件"时 / When the user needs to read/summarize email:
- 读取 `modules/z-skills/z-mail-reader/MODULE.md` / Read its MODULE.md
- 需要配置：`MAIL_IMAP_SERVER`、`MAIL_ADDR`、`MAIL_AUTH_CODE` / Requires IMAP env vars
- 模块路径：`modules/z-skills/z-mail-reader/`

### 8. 短剧剧本评估 / Short-Drama Script Evaluation
当用户需要"剧本评分""短剧评估""剧本审核"时 / When the user needs script scoring:
- 读取 `modules/drama-eval/MODULE.md` / Read `modules/drama-eval/MODULE.md`
- 模块路径：`modules/drama-eval/`

### 9. 格式转换与文档处理 / Format Conversion & Document Processing
- **MD转Word**：`modules/z-skills/z-md-to-word/MODULE.md`
- **MD表格转Excel**：`modules/z-skills/z-md-excel/MODULE.md`
- **Excel/CSV编辑**：`modules/z-skills/z-excel-editor/MODULE.md`
- **Word格式统一**：`modules/z-skills/z-docx-format-brush/MODULE.md`

### 10. 创意演示 / Creative Presentations
- **手写风格PPT**：`modules/z-skills/z-wanghong-handwritten-ppt/MODULE.md`
- **手写动画视频**：`modules/z-skills/z-wanghong-handwritten-video/MODULE.md`
- **本地资料问答**：`modules/z-skills/z-grounded-source-qa/MODULE.md`

### 11. 发布前风险自审 / Pre-Publish Risk Self-Check
当用户需要"能不能发""审一下稿子""查违禁词/敏感词""会不会被限流""被平台处罚/删除""发布前检查"时 / When the user asks "can I publish this?", banned-word checks, rate-limit/penalty risk:
- 读取 `modules/publish-precheck/MODULE.md` / Read `modules/publish-precheck/MODULE.md`
- 支持抖音/小红书/微信视频号逐平台预检，给出问题位置、规则依据与可直接替换的保意修复稿 / Per-platform pre-checks (Douyin/XHS/WeChat Channels) with issue locations, rule citations, and meaning-preserving fix drafts
- 用户反馈自动沉淀为个人规则库（黑名单/白名单/语义规则/安全表达），越用越准 / User feedback accumulates into a personal rule base (black/white lists, semantic rules, safe phrasings)
- 模块路径：`modules/publish-precheck/`
- ⚠️ 不提供谐音、拆字、遮挡等绕审手段；审核到发布检查单为止 / No evasion tricks (homophones, character splitting, masking); the check ends at the publish checklist

## ⚙️ 环境配置 / Environment Setup

### 基础依赖 / Base dependencies

```bash
# macOS使用Homebrew安装 / macOS via Homebrew
brew install node ffmpeg qpdf

# Python依赖 / Python dependencies
pip3 install imapclient pypdf
```

### 环境变量配置（按需）/ Environment variables (as needed)

| 环境变量 Env Var | 用途 Purpose | 使用模块 Module |
|----------|------|----------|
| `NEWAPI_BASE_URL` | API服务地址 · API service URL | AI视频生成 · AI video |
| `NEWAPI_API_KEY` | API密钥 · API key | AI视频生成 · AI video |
| `DASHI_PPT_PROJECT_PATH` | PPT模板project目录路径 · PPT template project path | PPT制作 · PPT |
| `DASHSCOPE_API_KEY` | 阿里云DashScope密钥 · Alibaba DashScope key | 视频学习分析（可选）· Video study (optional) |
| `MAIL_IMAP_SERVER` | 邮件IMAP服务器 · Email IMAP server | 邮件管理（可选）· Email (optional) |
| `MAIL_ADDR` | 邮箱地址 · Email address | 邮件管理（可选）· Email (optional) |
| `MAIL_AUTH_CODE` | 邮箱IMAP授权码 · IMAP auth code | 邮件管理（可选）· Email (optional) |
| `XPARSE_APP_ID` | TextIn文档解析AppID · TextIn AppID | 文档解析（可选）· Parsing (optional) |
| `XPARSE_SECRET_CODE` | TextIn文档解析密钥 · TextIn secret | 文档解析（可选）· Parsing (optional) |
| `CHROME_PATH` | Chrome浏览器路径 · Chrome path | PPT导出（可选）· PPT export (optional) |

配置模板（添加到`~/.zshrc`）/ Config template (add to `~/.zshrc`):
```bash
# AI营销视频生成（使用时配置）· AI marketing video (configure when used)
# export NEWAPI_BASE_URL="your-api-service-url"
# export NEWAPI_API_KEY="your-api-key"

# PPT制作（使用时配置）· PPT (configure when used)
export DASHI_PPT_PROJECT_PATH="/path/to/dashi-ppt-skill-main/skills/dashi-ppt/project"

# 视频学习分析（可选）· Video study (optional)
# export DASHSCOPE_API_KEY="your-api-key"

# 邮件管理（可选）· Email (optional)
# export MAIL_IMAP_SERVER="imap.qq.com"
# export MAIL_ADDR="y*********@******"
# export MAIL_AUTH_CODE="your-auth-code"
```

配置完成后执行 `source ~/.zshrc`，然后运行环境检查脚本验证 / After configuring, run `source ~/.zshrc` and verify with the env-check script:
```bash
bash check-env.sh
```

## 📂 目录结构 / Directory Structure

```
content-creator-expert/
├── SKILL.md                    # 本文件 - 主入口 · This file — main entry
├── README.md                   # 使用说明 · Usage guide
├── CONFIG.md                   # 详细配置指南 · Detailed config guide
├── check-env.sh                # 环境检查脚本 · Env-check script
└── modules/
    ├── seedance/               # AI营销视频生成 · AI marketing video
    │   ├── MODULE.md
    │   └── api/
    ├── dashi-ppt/              # PPT制作 · PPT deck
    ├── gzh-design/             # 公众号排版 · WeChat MP layout
    ├── drama-eval/             # 短剧剧本评估 · Short-drama script eval
    │   └── MODULE.md
    ├── publish-precheck/       # 发布前风险自审 · Pre-publish self-check
    │   ├── MODULE.md
    │   ├── scripts/
    │   └── references/
    └── z-skills/               # 工具集 · Toolkit
        ├── z-web-pack/         # 网页素材采集 · Web assets
        ├── z-video-study-webpage-qwen/  # 视频学习分析 · Video study
        ├── z-smart-xparse/     # 文档解析 · Document parsing
        ├── z-mail-reader/      # 邮件管理 · Email
        ├── z-md-to-word/       # MD转Word
        ├── z-md-excel/         # MD转Excel
        ├── z-excel-editor/     # Excel编辑 · Spreadsheet editing
        ├── z-docx-format-brush/ # Word格式刷 · Format brush
        ├── z-wanghong-handwritten-ppt/  # 手写风格PPT · Handwritten PPT
        ├── z-wanghong-handwritten-video/ # 手写动画视频 · Handwritten video
        └── z-grounded-source-qa/         # 资料问答 · Grounded QA
```

## 🎯 典型营销工作流 / Typical Marketing Workflows

### 营销短视频创作 / Marketing short video
1. 素材采集参考 → z-web-pack / Collect reference assets
2. 创意策划与分镜设计 / Creative planning & storyboarding
3. AI视频生成 → seedance / AI video generation
4. （可选）视频内容分析 → z-video-study-webpage-qwen / (Optional) video analysis

### 公众号营销文章 / WeChat MP marketing article
1. 素材收集 → z-web-pack / Gather assets
2. 参考资料解析 → z-smart-xparse / Parse references
3. 撰写Markdown文章 / Write the Markdown article
4. 公众号排版 → gzh-design / Layout for WeChat MP

### 营销方案PPT / Marketing proposal PPT
1. 资料收集整理 → z-web-pack、z-smart-xparse / Collect & organize
2. 内容大纲撰写 / Draft the outline
3. PPT制作 → dashi-ppt / Build the deck
4. 导出PPTX/PDF / Export PPTX/PDF

### 短剧项目评估 / Short-drama project evaluation
1. 提供剧本文件 / Provide the script file
2. 剧本多维度评估 → drama-eval / Multi-dimension evaluation
3. 根据评估意见修改 / Revise per the feedback
4. 复评直至达标 / Re-evaluate until passing

### 内容发布前自审 / Pre-publish self-check
1. 提供待发布稿件（口播稿/文章/图文笔记/字幕）/ Provide the draft (voice-over/article/note/subtitles)
2. 词面预检 + 逐条判定 → publish-precheck / Surface scan + itemized judgment
3. 按需保意修复，复检通过后输出发布检查单 / Apply meaning-preserving fixes; output the publish checklist on pass
4. （被限流/删除时）复盘归因，沉淀个人规则 / (On rate-limit/removal) review & attribute, grow the personal rule base

## ⚠️ 使用规范 / Usage Rules

1. **合规使用 / Compliant use**：所有功能仅限制作合法合规的商业营销内容 · All features are for legal, compliant commercial marketing content only
2. **知识产权 / Intellectual property**：仅使用拥有版权或已获授权的素材，尊重他人知识产权 · Use only owned/licensed assets; respect others' IP
3. **内容安全 / Content safety**：不生成涉及政治敏感、色情暴力、虚假宣传、侵犯隐私等违规内容 · No politically sensitive, pornographic, violent, falsely promotional, or privacy-violating content
4. **按需配置 / Configure on demand**：不使用的模块无需配置对应密钥 · Skip env config for unused modules
5. **结果校验 / Verify results**：各模块执行完成后按要求验证输出结果 · Verify module outputs after execution
6. **路径使用 / Paths**：所有模块路径相对于本SKILL.md所在目录 · All module paths are relative to this SKILL.md's directory

## 🔧 模块路径速查 / Module Path Quick Reference

| 模块 Module | 路径 Path |
|------|------|
| AI营销视频 · AI marketing video | `modules/seedance/` |
| PPT制作 · PPT deck | `modules/dashi-ppt/` |
| 公众号排版 · WeChat MP layout | `modules/gzh-design/` |
| 剧本评估 · Script eval | `modules/drama-eval/` |
| 发布前自审 · Pre-publish self-check | `modules/publish-precheck/` |
| 网页素材采集 · Web assets | `modules/z-skills/z-web-pack/` |
| 视频学习分析 · Video study | `modules/z-skills/z-video-study-webpage-qwen/` |
| 文档解析 · Document parsing | `modules/z-skills/z-smart-xparse/` |
| 邮件管理 · Email | `modules/z-skills/z-mail-reader/` |
| MD转Word | `modules/z-skills/z-md-to-word/` |
| MD转Excel | `modules/z-skills/z-md-excel/` |
| Excel编辑 · Spreadsheet editing | `modules/z-skills/z-excel-editor/` |
| Word格式刷 · Format brush | `modules/z-skills/z-docx-format-brush/` |
| 手写风格PPT · Handwritten PPT | `modules/z-skills/z-wanghong-handwritten-ppt/` |
| 手写动画视频 · Handwritten video | `modules/z-skills/z-wanghong-handwritten-video/` |
| 资料问答 · Grounded QA | `modules/z-skills/z-grounded-source-qa/` |
