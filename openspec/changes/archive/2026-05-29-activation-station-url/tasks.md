## 1. 激活客户端修改

- [x] 1.1 修改 `lib/activation-client.mjs`：`activateDevice` 返回值去掉 apiKey，新增 stationUrl 字段
- [x] 1.2 修改 `lib/bootstrap-activation.mjs`：写入 openclaw.json 时不写 apiKey，只写 baseUrl 和 defaultModel；缓存 stationUrl 到临时文件供 config-server 读取

## 2. 配置服务器修改

- [x] 2.1 修改 `config-server/server.js`：`/api/activation-info` 端点返回增加 stationUrl 字段，优先从 bootstrap 缓存文件读取

## 3. 配置页面修改

- [x] 3.1 修改 `config-server/public/index.html`：AIPDD 卡片的"获取 API Key"链接使用 stationUrl，显示中转站域名和默认模型
