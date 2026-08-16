# AiPddClaw Portable

A plug-and-play portable AI Agent toolkit. English by default, with Chinese (中文) support throughout.

## Before You Start

1. Register an account at [app.aipdd.work](https://app.aipdd.work)
2. Configure your relay station info on the platform (model, station URL, etc.)
3. Create an Activation Code
4. Paste the code into the `activationCode` field of `activation.json`

## Quick Start

### Windows
Double-click `Windows-Start.bat`

### macOS
Double-click `Mac-Start.command`

On first launch it will automatically:
1. Detect the Node.js runtime
2. Call the activation API to fetch relay station info
3. Open the setup page (browser pops up automatically)

## Setup Flow

The setup page opens in your browser after launch — three steps:

1. **Pick a model** — AIPDD recommended; DeepSeek, Kimi, Qwen, and more are supported
2. **Enter API Key** — click "Get API Key" for AIPDD to register at the relay station
3. **Launch** — configuration complete, start using it

> The setup page and chat are bilingual (English / 中文). The default language is English; use the toggle in the top-right corner of the setup page to switch to 中文. The agent replies in English by default and follows your language when you write in Chinese.

## Directory Structure

```
portable/
├── Windows-Start.bat      # Windows launcher
├── Mac-Start.command       # macOS launcher
├── activation.json         # activation config (station URL, activation code)
├── setup.bat / setup.sh    # first-time Node.js runtime installer
├── lib/
│   ├── fingerprint.mjs          # device fingerprint generation
│   ├── activation-client.mjs    # activation API client
│   └── bootstrap-activation.mjs # auto-config at startup
├── config-server/
│   ├── server.js            # config server (port 18788)
│   └── public/index.html    # setup page
├── app/                     # runtime + OpenClaw core (downloaded separately)
│   ├── core/                # OpenClaw core code + node_modules
│   └── runtime/             # Node.js runtime
└── data/                    # config and data (generated at runtime)
    └── .openclaw/           # OpenClaw config directory
        └── openclaw.json    # main config file
```

> The `app/` and `data/` directories are not part of the repo; prepare them separately.

## Environment Setup

Install the Node.js runtime on first use:

```bash
# Windows
setup.bat

# macOS / Linux
./setup.sh
```

## Activation

After creating an activation code at [app.aipdd.work](https://app.aipdd.work), edit `activation.json`:

```json
{
  "activationCode": "BATCH-XXXXXXXX"
}
```

At startup the activation API is called automatically; the activation code fetches the station URL, API base URL, and default model and writes them into the config. You then enter your API key on the setup page.

## Ports

| Port | Purpose |
|------|---------|
| 18788 | Setup page (browser access) |
| 18789 | OpenClaw Gateway |

## License

MIT

---

# AiPddClaw 便携版

开箱即用的 AI Agent 便携工具，U盘即插即用。默认英文，支持中文（中英双语）。

## 使用前准备

1. 访问 [app.aipdd.work](https://app.aipdd.work) 注册账号
2. 在平台配置中转站信息（选择模型、中转站地址等）
3. 创建激活码（Activation Code）
4. 将激活码填入 `activation.json` 的 `activationCode` 字段

## 快速开始

### Windows
双击运行 `Windows-Start.bat`

### macOS
双击运行 `Mac-Start.command`

首次启动会自动：
1. 检测 Node.js 运行时
2. 调用激活接口获取中转站信息
3. 打开配置页面（浏览器自动弹出）

## 配置流程

启动后浏览器会打开配置页面，三步完成：

1. **选模型** — 推荐 AIPDD，也支持 DeepSeek、Kimi、通义千问等
2. **填 API Key** — 选择 AIPDD 后点击"获取 API Key"跳转中转站注册
3. **启动** — 配置完成，开始使用

> 配置页面与聊天界面均支持中英双语。默认语言为英文，可在配置页面右上角切换到中文。Agent 默认用英文回复，使用中文提问时会自动切换到中文。

## 目录结构

```
portable/
├── Windows-Start.bat      # Windows 启动脚本
├── Mac-Start.command       # macOS 启动脚本
├── activation.json         # 激活配置（中转站地址、激活码）
├── setup.bat / setup.sh    # 首次安装 Node.js 运行时
├── lib/
│   ├── fingerprint.mjs          # 设备指纹生成
│   ├── activation-client.mjs    # 激活接口客户端
│   └── bootstrap-activation.mjs # 启动时自动配置
├── config-server/
│   ├── server.js            # 配置服务器（端口 18788）
│   └── public/index.html    # 配置页面
├── app/                     # 运行时 + OpenClaw 核心（需单独下载）
│   ├── core/                # OpenClaw 核心代码 + node_modules
│   └── runtime/             # Node.js 运行时
└── data/                    # 配置和数据（运行时生成）
    └── .openclaw/           # OpenClaw 配置目录
        └── openclaw.json    # 主配置文件
```

> `app/` 和 `data/` 目录不包含在仓库中，需要单独准备。

## 环境准备

首次使用需安装 Node.js 运行时：

```bash
# Windows
setup.bat

# macOS / Linux
./setup.sh
```

## 激活配置

在 [app.aipdd.work](https://app.aipdd.work) 创建激活码后，编辑 `activation.json`：

```json
{
  "activationCode": "BATCH-XXXXXXXX"
}
```

启动时会自动调用激活接口，通过激活码获取中转站地址（stationUrl）、API 地址（baseUrl）和默认模型（defaultModel）写入配置。用户随后在配置页面自行填写 API Key 即可使用。

## 端口说明

| 端口 | 用途 |
|------|------|
| 18788 | 配置页面（浏览器访问） |
| 18789 | OpenClaw Gateway |

## 许可证

MIT
