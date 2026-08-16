## MODIFIED Requirements

### Requirement: 服务端提供激活信息接口
config-server SHALL 提供 `GET /api/activation-info` 端点，返回 stationUrl、baseUrl 和 defaultModel。stationUrl 从 bootstrap 缓存文件 activation-cache.json 中读取。

#### Scenario: 激活成功
- **WHEN** bootstrap 激活成功且 activation-cache.json 存在
- **THEN** 接口返回 `{ "stationUrl": "<stationUrl>", "baseUrl": "<baseUrl>", "defaultModel": "<defaultModel>", "available": true }`

#### Scenario: 无 stationUrl
- **WHEN** activation-cache.json 不存在或 stationUrl 为空
- **THEN** 接口返回 `{ "stationUrl": "", "baseUrl": "<默认值>", "defaultModel": "<默认值>", "available": false }`

### Requirement: 配置页面动态加载 AIPDD 信息
配置页面 SHALL 在加载时调用 `/api/activation-info` 接口，将 AIPDD 提供商卡片的地址、模型信息和"获取 API Key"链接替换为接口返回值。

#### Scenario: 接口返回有效数据
- **WHEN** `/api/activation-info` 返回 `available: true` 且 `stationUrl` 非空
- **THEN** AIPDD 卡片的描述文本显示实际的 baseUrl 域名和默认模型，"获取 API Key"链接跳转到 stationUrl

#### Scenario: stationUrl 为空
- **WHEN** stationUrl 为空字符串
- **THEN** AIPDD 卡片的"获取 API Key"链接保持默认地址
