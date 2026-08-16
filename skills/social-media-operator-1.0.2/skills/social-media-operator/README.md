# Social Media Operator

社交媒体内容与运营一体化 Skill，统一覆盖小红书、微信公众号、抖音与私域场景。

## 目录约定

```text
skills/social-media-operator/
├── SKILL.md                         # 唯一入口：能力、流程、安全规则
├── README.md                        # 安装与维护说明
├── references/
│   ├── platform-playbook.md         # 平台策略与内容模板
│   ├── xhs-publishing.md            # 小红书发布、互动、浏览 SOP
│   ├── wechat-monitoring.md         # 公众号监控设计
│   └── voice-and-safety.md          # 语气、人设与安全边界
├── templates/
│   ├── xhs-note.md                  # 发布正文
│   └── xhs-card.md                  # 卡片渲染输入
└── tools/                           # 后续迁移后的唯一脚本入口
```

## 维护原则

1. 只把 `SKILL.md` 作为 Agent 入口，避免四份技能同时命中造成冲突。
2. 平台共性策略放 `platform-playbook.md`；操作细节放对应 reference，不在主文档重复。
3. 小红书渲染只保留一个实现版本，默认使用 V2；素材、脚本和文档按功能归档。
4. 不把 Cookie、账号数据、生成图片或运行日志放进技能包。
5. 发布、回复和抓取都采用“先检查、再执行、可停可回滚”的流程。

## 示例请求

- “把这份资料写成小红书笔记并生成 5 张卡片。”
- “为公众号做一个四周选题日历。”
- “检查最近评论，先不要回复。”
- “根据这组数据找出下一轮 A/B 测试。”
