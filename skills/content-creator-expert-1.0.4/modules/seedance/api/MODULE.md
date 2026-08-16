---
name: newapi-media
description: "NewAPI媒体生成调用工具，支持视频、图片生成API调用。"
---

# NewAPI 媒体生成调用工具

通过NewAPI兼容接口调用AI视频、图片生成服务。

## 配置

首次使用运行配置向导：
```bash
node scripts/configure.js
```

或手动设置环境变量：
```bash
export NEWAPI_BASE_URL="你的API服务地址"
export NEWAPI_API_KEY="你的API密钥"
```

## 视频生成调用

```bash
node scripts/invoke.js --type video \
  --prompt "视频描述" \
  --model "jimeng-2.0" \
  --duration 5 \
  --ratio "16:9"
```

参数：
- `--type`: 生成类型，video/image
- `--prompt`: 提示词文本
- `--model`: 模型名称
- `--duration`: 视频时长（秒）
- `--ratio`: 画面比例
- `--first-frame`: 首帧图片路径（可选）
- `--last-frame`: 尾帧图片路径（可选）
- `--output`: 输出目录（可选，默认output）
