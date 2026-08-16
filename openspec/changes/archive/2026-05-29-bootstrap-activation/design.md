## Context

AiPddClaw 便携版需要在启动时自动配置中转站信息。参考 u-claw 项目的 `bootstrap-xiapan.mjs` 实现，通过 `activation.json` 中的 `activationCode` 调用远程激活接口获取中转站地址和模型信息。

当前状态：
- `activation.json` 已存在于项目根目录，包含 `activationBaseUrl`、`activationCode`、`apiBaseUrl`、`defaultModel` 等字段
- `config-server/public/index.html` 中 AIPDD 的 baseUrl 和 model 是硬编码的
- 启动脚本（Windows-Start.bat / Mac-Start.command）在 gateway 启动前有 bootstrap 阶段的插入点
- 参考实现：`D:\liujh\u-claw-master\u-claw\portable\lib\` 下的 `fingerprint.mjs`、`xiapan-client.mjs`、`bootstrap-xiapan.mjs`

## Goals / Non-Goals

**Goals:**
- 启动时自动读取 activation.json，调用激活接口获取中转站 baseUrl/apiKey/defaultModel
- 将获取到的信息写入 openclaw.json 的 AIPDD provider 配置
- 配置页面的 AIPDD 卡片显示从 openclaw.json 动态读取的地址和模型，而非硬编码值
- 激活失败时优雅降级，使用 activation.json 中的本地配置值

**Non-Goals:**
- 不实现完整的 Xiapan Cloud 余额查询和充值功能
- 不实现设备指纹的 USB/磁盘检测（使用 seed 方式简化实现）
- 不修改 gateway 核心逻辑
- 不实现多 provider 动态配置（仅 AIPDD）

## Decisions

### 1. 复用 u-claw 的 lib 脚本，适配 AiPddClaw 品牌

**选择**: 将 `fingerprint.mjs`、`xiapan-client.mjs`、`bootstrap-xiapan.mjs` 复制到 `lib/` 目录，做最小化品牌适配（UCLAW_ 环境变量前缀改为 AIPDDCLAW_）。

**理由**: 保持与上游 u-claw 的兼容性，减少维护成本。仅修改品牌标识和默认值。

**替代方案**: 从零重写 —— 增加工作量且容易引入 bug。

### 2. 激活接口调用时机：启动脚本中 gateway 启动前

**选择**: 在 Windows-Start.bat 和 Mac-Start.command 中，config-server 启动之后、gateway 启动之前执行 bootstrap 脚本。

**理由**: 这样 openclaw.json 在 gateway 读取前就已包含正确的 AIPDD 配置。config-server 也能读取到更新后的配置。

**替代方案**: 在 config-server 中做激活 —— 增加复杂度，且 gateway 启动时可能读到旧配置。

### 3. 配置页面动态读取方案

**选择**: 在 server.js 新增 `/api/activation-info` 端点，返回 openclaw.json 中 AIPDD provider 的 baseUrl 和 primary model。前端 index.html 的 PROVIDERS 数组中 AIPDD 条目改为从该接口动态获取 base 和 model。

**理由**: 最小改动。只需在前端 AIPDD 条目处增加一个异步加载，其余 provider 保持硬编码。

**替代方案**: 前端直接读取 `/api/config` 整个配置 —— 会暴露 apiKey 等敏感信息。

### 4. 设备指纹策略

**选择**: 简化为仅使用 seed 文件方式（`~/.uclaw/.usb_seed`），不实现 USB/磁盘检测。

**理由**: 当前阶段不需要硬件绑定。激活接口主要依赖 activationCode，fingerprint 仅作为辅助标识。

**替代方案**: 完整移植 USB/磁盘检测 —— PowerShell 调用在某些环境可能失败，增加不稳定性。

## Risks / Trade-offs

- **[网络依赖]** 激活接口不可用时 → 降级使用 activation.json 中的本地默认值（apiBaseUrl + defaultModel）
- **[配置冲突]** 用户手动修改了 AIPDD provider → bootstrap 脚本检测到用户自定义 apiKey（非 sk- 前缀）时不覆盖
- **[启动延迟]** 激活接口调用增加启动时间 → 设置 10 秒超时，超时后静默降级
- **[前端缓存]** 配置页面可能读到旧的 openclaw.json → server.js 每次请求都读文件，无缓存问题
