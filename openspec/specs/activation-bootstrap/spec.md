# activation-bootstrap Specification

## Purpose
TBD - created by archiving change bootstrap-activation. Update Purpose after archive.
## Requirements
### Requirement: 读取 activation.json 配置
系统 SHALL 在启动时从项目根目录读取 `activation.json`，解析其中的 `activationBaseUrl`、`activationCode`、`apiBaseUrl`、`defaultModel` 字段。

#### Scenario: activation.json 存在且完整
- **WHEN** `activation.json` 存在且包含 `activationBaseUrl` 和 `activationCode`
- **THEN** 系统使用这些值进行激活流程

#### Scenario: activation.json 不存在
- **WHEN** `activation.json` 不存在
- **THEN** 系统跳过激活，使用硬编码的默认值（baseUrl: `https://newapi.jumcp.com/v1`，model: `mimo-v2-omni`）

#### Scenario: activation.json 不完整
- **WHEN** `activation.json` 存在但缺少 `activationBaseUrl` 或 `activationCode`
- **THEN** 系统跳过远程激活，使用文件中的 `apiBaseUrl` 和 `defaultModel`（如有）作为降级值

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

### Requirement: 启动脚本集成
Windows-Start.bat 和 Mac-Start.command SHALL 在 gateway 启动前执行 bootstrap 脚本。

#### Scenario: 正常执行
- **WHEN** 用户运行启动脚本
- **THEN** 脚本先执行 `node lib/bootstrap-activation.mjs <config-path>`，等待完成后再启动 gateway

#### Scenario: bootstrap 脚本失败
- **WHEN** bootstrap 脚本执行出错
- **THEN** 启动脚本记录警告但不中断，继续启动 gateway

