# dynamic-provider-config Specification

## Purpose
TBD - created by archiving change bootstrap-activation. Update Purpose after archive.
## Requirements
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

### Requirement: 构建配置时使用动态值
保存配置时（`buildConfig` 函数），AIPDD 的 baseUrl SHALL 使用页面上显示的实际值而非硬编码值。

#### Scenario: 用户选择 AIPDD 并保存
- **WHEN** 用户选择 AIPDD 提供商并点击保存
- **THEN** 写入 openclaw.json 的 baseUrl 和 model 使用从 `/api/activation-info` 获取的实际值

