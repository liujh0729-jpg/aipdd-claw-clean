## 1. 基础库文件

- [x] 1.1 创建 `lib/fingerprint.mjs`：从 u-claw 复制并适配品牌标识，简化为仅支持 seed 方式生成设备指纹
- [x] 1.2 创建 `lib/activation-client.mjs`：从 u-claw 的 `xiapan-client.mjs` 复制并适配，提供 `getActivationConfig()`、`activateDevice()`、`normalizeApiBaseUrl()` 函数
- [x] 1.3 创建 `lib/bootstrap-activation.mjs`：从 u-claw 的 `bootstrap-xiapan.mjs` 复制并适配，编排完整 bootstrap 流程（读取 activation.json → 调用激活接口 → 写入 openclaw.json）

## 2. 启动脚本集成

- [x] 2.1 修改 `Windows-Start.bat`：在 gateway 启动前插入 `node lib/bootstrap-activation.mjs` 调用，失败时不中断启动
- [x] 2.2 修改 `Mac-Start.command`：同上，在 gateway 启动前插入 bootstrap 调用

## 3. 配置服务器扩展

- [x] 3.1 修改 `config-server/server.js`：新增 `GET /api/activation-info` 端点，从 openclaw.json 读取 AIPDD provider 的 baseUrl 和 defaultModel（不含 apiKey）
- [x] 3.2 添加降级逻辑：openclaw.json 不存在或无 AIPDD 配置时返回硬编码默认值

## 4. 配置页面动态化

- [x] 4.1 修改 `config-server/public/index.html`：页面加载时调用 `/api/activation-info`，将 AIPDD 卡片的 baseUrl 和 model 替换为接口返回值
- [x] 4.2 修改 `buildConfig` 函数：AIPDD 分支使用动态获取的 baseUrl 和 model 而非硬编码值
- [x] 4.3 修改 AIPDD 卡片描述：显示实际的中转站域名而非固定文本

## 5. 验证

- [x] 5.1 端到端测试：删除 openclaw.json，运行 Windows-Start.bat，验证 bootstrap 脚本正确写入 AIPDD 配置
- [x] 5.2 页面测试：打开配置页面，验证 AIPDD 卡片显示从接口获取的地址和模型
- [x] 5.3 降级测试：断开网络或修改 activationBaseUrl 为无效地址，验证降级到本地默认值
