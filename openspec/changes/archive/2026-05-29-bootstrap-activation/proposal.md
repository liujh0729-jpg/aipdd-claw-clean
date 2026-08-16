## Why

当前 AiPddClaw 便携版的配置页面中，AIPDD 提供商的中转站地址和默认模型是硬编码的。需要在启动时通过 `activation.json` 中的 `activationCode` 调用激活接口，获取实际的中转站信息（baseUrl、apiKey、defaultModel），并将其注入到 openclaw.json 配置中，同时更新配置页面的 AIPDD 默认显示。

## What Changes

- 新增 `lib/bootstrap-activation.mjs` 启动脚本：读取 `activation.json`，调用 `{activationBaseUrl}/uclaw/activate` 接口获取中转站信息，写入 `openclaw.json`
- 新增 `lib/fingerprint.mjs`：跨平台设备指纹生成，用于激活绑定
- 新增 `lib/activation-client.mjs`：激活接口客户端，封装 API 调用逻辑
- 修改 `Windows-Start.bat` 和 `Mac-Start.bat`：在启动 gateway 前执行 bootstrap 脚本
- 修改 `config-server/public/index.html`：AIPDD 提供商的地址和默认模型从 `openclaw.json` 中动态读取，而非硬编码
- 修改 `config-server/server.js`：新增 `/api/activation-info` 接口，返回当前激活状态信息

## Capabilities

### New Capabilities
- `activation-bootstrap`: 启动时根据 activationCode 调用激活接口，获取中转站 baseUrl/apiKey/defaultModel 并注入配置
- `dynamic-provider-config`: 配置页面的 AIPDD 提供商信息从本地配置动态读取，而非硬编码

### Modified Capabilities
<!-- 无已存在的 capability 需要修改 -->

## Impact

- 新增 3 个 Node.js ESM 脚本文件（lib/ 目录）
- 修改 2 个启动脚本（Windows-Start.bat, Mac-Start.command）
- 修改配置服务器（server.js）新增 API 端点
- 修改配置页面（index.html）前端逻辑
- 依赖 activation.json 配置文件存在
- 需要网络访问激活接口（activationBaseUrl）
