# 配置指南

## 配置项总览

| 配置项 | 用途 | 必须/可选 |
|--------|------|----------|
| NEWAPI_BASE_URL | AI营销视频生成API地址 | 必须（使用视频功能时） |
| NEWAPI_API_KEY | AI营销视频生成API密钥 | 必须（使用视频功能时） |
| DASHI_PPT_PROJECT_PATH | PPT模板目录路径 | 必须（使用PPT时） |
| Node.js 20+ | AI视频、PPT运行环境 | 必须 |
| Python 3 | 工具集脚本运行 | 必须 |
| ffmpeg + qpdf | 视频处理、PDF分割 | 推荐 |
| Chrome/Edge | PPT导出PPTX/PDF | 推荐 |
| xparse-cli | 文档解析 | 推荐 |
| DASHSCOPE_API_KEY | 视频学习分析 | 可选 |
| 邮箱IMAP配置 | 邮件读取 | 可选 |

---

## 1. 基础环境安装

```bash
# macOS Homebrew
brew install node ffmpeg qpdf

# Python依赖
pip3 install imapclient pypdf
```

验证Node.js版本（需要v20+）：
```bash
node --version
```

---

## 2. AI营销视频生成配置

使用视频生成功能前需要配置NewAPI：

```bash
# 添加到 ~/.zshrc
export NEWAPI_BASE_URL="你的API服务地址"
export NEWAPI_API_KEY="你的API密钥"
```

配置后运行初始化：
```bash
node modules/seedance/api/scripts/configure.js
```

---

## 3. PPT制作配置

使用PPT功能前需要配置模板路径：

```bash
# 添加到 ~/.zshrc，指向原始dashi-ppt的project目录
export DASHI_PPT_PROJECT_PATH="/path/to/dashi-ppt-skill-main/skills/dashi-ppt/project"
```

> 由于包大小限制，精简包未内置project运行时目录，请指向原始dashi-ppt-skill-main中的对应目录。

---

## 4. 其他可选配置

### 4.1 视频学习分析（阿里云DashScope）
```bash
# 获取地址：https://dashscope.console.aliyun.com/
export DASHSCOPE_API_KEY="your-api-key"
```

### 4.2 邮件管理（IMAP）
```bash
# QQ邮箱示例
export MAIL_IMAP_SERVER="imap.qq.com"
export MAIL_ADDR="y*********@******"
export MAIL_AUTH_CODE="your-16-digit-auth-code"
```

> 授权码获取：邮箱→设置→账户→开启IMAP服务→生成授权码

### 4.3 文档解析（xparse-cli）
```bash
# 安装xparse-cli
source <(curl -fsSL https://dllf.intsig.net/download/2026/Solution/xparse-cli/install.sh)
```
免费版支持PDF和图片解析，Office格式需要付费API。

---

## 完整配置模板

复制以下内容到 `~/.zshrc`，按需取消注释：

```bash
# ============================================================
# 内容创作专家 Skill - 环境变量配置
# ============================================================

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

# Chrome路径（可选，自动检测失败时设置）
# export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

---

## 环境验证脚本

运行环境检查脚本验证配置：
```bash
bash check-env.sh
```
