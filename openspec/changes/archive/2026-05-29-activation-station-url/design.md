## Context

当前 bootstrap-activation.mjs 调用 `/uclaw/activate` 接口后，期望返回 `apiKey`、`baseUrl`、`primaryModel`。但实际上激活接口只返回中转站信息，apiKey 由用户在配置页面自行输入。

## Goals / Non-Goals

**Goals:**
- bootstrap 调用激活接口获取 stationUrl、baseUrl、defaultModel
- 写入 openclaw.json 时只写 baseUrl 和 defaultModel
- 配置页面 AIPDD 卡片使用 stationUrl 作为"获取 API Key"跳转地址
- apiKey 完全由用户在配置页第二步输入

**Non-Goals:**
- 不修改密码保护相关逻辑（后续变更）
- 不修改 gateway 启动逻辑

## Decisions

### 1. stationUrl 存储位置

**选择**: stationUrl 只存在 `/api/activation-info` 的运行时返回中，不写入 openclaw.json。

**理由**: stationUrl 是跳转链接，不是 gateway 运行时需要的配置。openclaw.json 只存 gateway 需要的字段（baseUrl、defaultModel）。stationUrl 每次从 activation-client 的内存缓存中读取。

### 2. bootstrap 不再写入 apiKey

**选择**: bootstrap-activation.mjs 写入 AIPDD provider 时，apiKey 字段留空或不写。

**理由**: 激活接口不再返回 apiKey，apiKey 由用户在配置页面自行输入。

## Risks / Trade-offs

- **[stationUrl 丢失]** config-server 重启后 stationUrl 需要重新从激活接口获取 → bootstrap 在 gateway 启动前已调用过，可将结果缓存到临时文件
