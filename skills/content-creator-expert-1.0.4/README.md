# 内容创作专家 Skill

面向新媒体创作人员的一站式内容创作工具包，整合AI营销视频生成、PPT制作、公众号排版、素材采集、文档处理等功能，用于制作合法合规的商业营销内容。

## ✨ 功能模块

| 模块 | 功能说明 | 依赖/配置 |
|------|----------|-----------|
| **AI营销视频生成** | 文生/图生视频、首尾帧、专业镜头语言 | Node.js、NEWAPI配置 |
| **PPT制作** | 12套主题、千余版式、可编辑PPTX/PDF导出 | Node.js 20+、Chrome、DASHI_PPT_PROJECT_PATH |
| **公众号排版** | 多套主题，直接粘贴公众号不掉格式 | Python 3 |
| **网页素材采集** | 网页正文、图片整理成本地素材包 | Python 3 |
| **视频学习分析** | 本地视频转录+关键帧分析生成学习笔记 | DashScope API Key（可选） |
| **文档解析** | PDF/图片/Office转Markdown | xparse-cli（免费版可用） |
| **邮件管理** | IMAP读取邮件、下载附件、摘要 | 邮箱IMAP授权码（可选） |
| **短剧剧本评估** | AI短剧专业多维度评分体系 | 无 |
| **发布前自审** | 抖音/小红书/视频号发布前预检、保意修复、被限流复盘 | Python 3 |
| **格式转换** | MD转Word、MD表格转Excel、Word格式刷 | Python 3 |
| **表格编辑** | Excel/CSV读取、编辑、数据清洗 | Python 3 |
| **手写风格演示** | Notability风格手写幻灯片/动画 | Node.js |
| **资料问答** | 本地资料检索、证据绑定回答 | Python 3 |

## 🚀 快速开始

### 1. 安装基础依赖

```bash
# macOS（Homebrew）
brew install node ffmpeg qpdf

# Python依赖
pip3 install imapclient pypdf
```

### 2. 配置环境变量

将以下内容添加到 `~/.zshrc`：

```bash
# ========== 内容创作专家Skill配置 ==========

# AI营销视频生成（使用视频功能时配置）
# export NEWAPI_BASE_URL="你的API服务地址"
# export NEWAPI_API_KEY="你的API密钥"

# PPT制作（使用PPT功能时配置）
export DASHI_PPT_PROJECT_PATH="/path/to/dashi-ppt-skill-main/skills/dashi-ppt/project"

# 视频学习分析（可选）
# export DASHSCOPE_API_KEY="your-api-key"

# 邮件管理（可选）
# export MAIL_IMAP_SERVER="imap.qq.com"
# export MAIL_ADDR="y*********@******"
# export MAIL_AUTH_CODE="your-auth-code"

# Chrome路径（可选）
# export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

执行 `source ~/.zshrc` 生效。

### 3. 环境检查

```bash
bash check-env.sh
```

## 📖 使用方法

直接用自然语言描述需求：

- "帮我生成一个5秒的产品展示视频，科技简约风格"
- "根据这张产品图做个动态展示视频"
- "帮我做一份10页的产品介绍PPT，用商务风主题"
- "把这篇文章排成公众号，用简约主题"
- "采集这个网页的素材保存到本地"
- "帮我评估一下这个短剧剧本"
- "审一下这篇稿子能不能发，会被限流吗"
- "解析这个PDF文档"
- "读取最近7天的商务邮件做个摘要"

## 📂 目录结构

```
content-creator-expert/
├── SKILL.md                    # 主入口与路由
├── README.md                   # 本文件
├── CONFIG.md                   # 详细配置指南
├── check-env.sh                # 环境检查脚本
└── modules/
    ├── seedance/               # AI营销视频生成
    ├── dashi-ppt/              # PPT制作
    ├── gzh-design/             # 公众号排版
    ├── drama-eval/             # 短剧剧本评估
    ├── publish-precheck/       # 发布前自审
    └── z-skills/               # 工具集
```

## 💡 典型营销工作流

### 营销短视频创作
1. 素材采集 → z-web-pack
2. 创意分镜设计
3. AI视频生成 → seedance

### 公众号营销文章
1. 素材收集 → z-web-pack
2. 资料解析 → z-smart-xparse
3. 撰写文章 → gzh-design排版

### 营销方案PPT
1. 资料整理 → z-web-pack、z-smart-xparse
2. 内容大纲撰写
3. PPT制作 → dashi-ppt

## ⚠️ 使用规范

1. **合规使用**：仅限制作合法合规的商业营销内容
2. **知识产权**：仅使用拥有版权或已获授权的素材
3. **内容安全**：不生成政治敏感、色情暴力、虚假宣传等违规内容
4. **按需配置**：不使用的模块无需配置

## 🔧 故障排查

| 问题 | 解决方案 |
|------|----------|
| AI视频生成失败 | 检查NEWAPI_BASE_URL和NEWAPI_API_KEY配置 |
| PPT无法导出 | 检查Chrome安装，或设置CHROME_PATH |
| 邮件登录失败 | 使用IMAP授权码而非登录密码 |
| xparse命令找不到 | 重新运行安装脚本 |
| Node.js版本低 | 使用nvm安装Node.js 20+ |
