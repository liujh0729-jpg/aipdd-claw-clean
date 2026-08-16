## ADDED Requirements

### Requirement: 服务端提供激活信息接口
config-server SHALL 提供 `GET /api/activation-info` 端点，返回 openclaw.json 中 AIPDD provider 的非敏感信息。

#### Scenario: 配置存在
- **WHEN** openclaw.json 中存在 `models.providers.AIPDD`
- **THEN** 接口返回 `{ "baseUrl": "<provider baseUrl>", "defaultModel": "<primary model id>", "available": true }`

#### Scenario: 配置不存在
- **WHEN** openclaw.json 中不存在 AIPDD provider
- **THEN** 接口返回 `{ "baseUrl": "https://newapi.jumcp.com/v1", "defaultModel": "deepseek-v4-pro", "available": false }`

#### Scenario: 配置读取失败
- **WHEN** openclaw.json 文件不存在或解析失败
- **THEN** 接口返回默认值，`available` 为 false

### Requirement: 配置页面动态加载 AIPDD 信息
配置页面 SHALL 在加载时调用 `/api/activation-info` 接口，将 AIPDD 提供商卡片的地址和模型信息替换为接口返回值。

#### Scenario: 接口返回有效数据
- **WHEN** `/api/activation-info` 返回 `available: true`
- **THEN** AIPDD 卡片的描述文本显示实际的 baseUrl 域名，选中后的默认模型使用接口返回的 defaultModel

#### Scenario: 接口不可用
- **WHEN** `/api/activation-info` 请求失败或超时
- **THEN** AIPDD 卡片保持硬编码的默认值（baseUrl: `https://newapi.jumcp.com/v1`，model: `deepseek-v4-pro`）

### Requirement: 构建配置时使用动态值
保存配置时（`buildConfig` 函数），AIPDD 的 baseUrl SHALL 使用页面上显示的实际值而非硬编码值。

#### Scenario: 用户选择 AIPDD 并保存
- **WHEN** 用户选择 AIPDD 提供商并点击保存
- **THEN** 写入 openclaw.json 的 baseUrl 和 model 使用从 `/api/activation-info` 获取的实际值
