## Why

当前 bootstrap-activation 流程假设激活接口返回 apiKey，但实际上激活接口只返回中转站信息（stationUrl、baseUrl、defaultModel），apiKey 由用户在配置页面自行输入。需要调整流程以匹配实际接口。

## What Changes

- 修改 `lib/activation-client.mjs`：接口返回字段改为 stationUrl、baseUrl、defaultModel，不再返回 apiKey
- 修改 `lib/bootstrap-activation.mjs`：写入 openclaw.json 时只写 baseUrl 和 defaultModel，不写 apiKey
- 修改 `config-server/server.js`：`/api/activation-info` 端点返回增加 stationUrl 字段
- 修改 `config-server/public/index.html`：AIPDD 卡片的"获取 API Key"链接使用 stationUrl

## Capabilities

### New Capabilities

（无新增 capability）

### Modified Capabilities

- `activation-bootstrap`: 接口返回字段变更，不再包含 apiKey，新增 stationUrl
- `dynamic-provider-config`: 配置页面 AIPDD 卡片的跳转链接改为动态 stationUrl

## Impact

- 修改 4 个文件
- 激活接口交互变更：不再期望返回 apiKey
- 用户在配置页第二步自行输入 apiKey
