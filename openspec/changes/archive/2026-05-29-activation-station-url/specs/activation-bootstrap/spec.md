## MODIFIED Requirements

### Requirement: 调用激活接口获取中转站信息
系统 SHALL 使用 `activationCode` 调用 `{activationBaseUrl}/uclaw/activate` 接口，获取 stationUrl、baseUrl 和 defaultModel。接口不再返回 apiKey。

#### Scenario: 激活成功
- **WHEN** 激活接口返回 HTTP 200 且响应包含 `stationUrl`、`baseUrl`
- **THEN** 系统使用返回的 baseUrl 和 defaultModel 更新 openclaw.json，stationUrl 用于配置页面跳转

#### Scenario: 激活失败
- **WHEN** 激活接口请求超时或返回错误
- **THEN** 系统降级使用 activation.json 中的本地 apiBaseUrl 和 defaultModel，stationUrl 为空

### Requirement: 注入中转站信息到 openclaw.json
系统 SHALL 将获取到的 baseUrl 和 defaultModel 写入 `data/.openclaw/openclaw.json`。不写入 apiKey。

#### Scenario: 正常写入
- **WHEN** 激活成功或使用本地降级值
- **THEN** openclaw.json 中 AIPDD provider 的 baseUrl 和 agents.defaults.model.primary 被更新，apiKey 字段不被 bootstrap 写入
