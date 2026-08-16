## ADDED Requirements

### Requirement: 读取 activation.json 配置
系统 SHALL 在启动时从项目根目录读取 `activation.json`，解析其中的 `activationBaseUrl`、`activationCode`、`apiBaseUrl`、`defaultModel` 字段。

#### Scenario: activation.json 存在且完整
- **WHEN** `activation.json` 存在且包含 `activationBaseUrl` 和 `activationCode`
- **THEN** 系统使用这些值进行激活流程

#### Scenario: activation.json 不存在
- **WHEN** `activation.json` 不存在
- **THEN** 系统跳过激活，使用硬编码的默认值（baseUrl: `https://newapi.jumcp.com/v1`，model: `deepseek-v4-pro`）

#### Scenario: activation.json 不完整
- **WHEN** `activation.json` 存在但缺少 `activationBaseUrl` 或 `activationCode`
- **THEN** 系统跳过远程激活，使用文件中的 `apiBaseUrl` 和 `defaultModel`（如有）作为降级值

### Requirement: 调用激活接口获取中转站信息
系统 SHALL 使用 `activationCode` 和设备指纹调用 `{activationBaseUrl}/uclaw/activate` 接口，获取 apiKey、baseUrl 和 primaryModel。

#### Scenario: 激活成功
- **WHEN** 激活接口返回 HTTP 200 且响应包含 `apiKey`、`baseUrl`
- **THEN** 系统使用返回的 apiKey、baseUrl、primaryModel 更新 openclaw.json 中的 AIPDD provider

#### Scenario: 激活失败（网络超时）
- **WHEN** 激活接口请求超过 10 秒未响应
- **THEN** 系统降级使用 activation.json 中的 apiBaseUrl 和 defaultModel，记录警告日志

#### Scenario: 激活失败（接口错误）
- **WHEN** 激活接口返回非 200 状态码或响应中包含错误信息
- **THEN** 系统降级使用 activation.json 中的 apiBaseUrl 和 defaultModel，记录警告日志

### Requirement: 注入中转站信息到 openclaw.json
系统 SHALL 将获取到的 AIPDD provider 信息写入 `data/.openclaw/openclaw.json` 的 `models.providers.AIPDD` 和 `agents.defaults.model.primary` 字段。

#### Scenario: 首次写入（无现有配置）
- **WHEN** openclaw.json 中不存在 AIPDD provider
- **THEN** 系统创建完整的 AIPDD provider 配置，包含 baseUrl、apiKey、models 数组

#### Scenario: 更新现有配置（用户未自定义）
- **WHEN** openclaw.json 中 AIPDD provider 的 apiKey 以 `sk-` 开头（系统生成的）
- **THEN** 系统更新 baseUrl 和 apiKey 为激活返回的值

#### Scenario: 保留用户自定义配置
- **WHEN** openclaw.json 中 AIPDD provider 的 apiKey 不以 `sk-` 开头（用户手动设置的）
- **THEN** 系统不覆盖 apiKey，仅更新 baseUrl 和 agents.defaults

### Requirement: 启动脚本集成
Windows-Start.bat 和 Mac-Start.command SHALL 在 gateway 启动前执行 bootstrap 脚本。

#### Scenario: 正常执行
- **WHEN** 用户运行启动脚本
- **THEN** 脚本先执行 `node lib/bootstrap-activation.mjs <config-path>`，等待完成后再启动 gateway

#### Scenario: bootstrap 脚本失败
- **WHEN** bootstrap 脚本执行出错
- **THEN** 启动脚本记录警告但不中断，继续启动 gateway
