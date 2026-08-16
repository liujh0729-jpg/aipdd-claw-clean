---
name: ai-humanizer
version: 1.0.0
description: Rewrite AI-generated Chinese text into natural human-like writing that passes AI detection. Use when the user asks to humanize text, de-AI content, remove AI flavor, rewrite to sound human, or make AI writing pass detection.
description_zh: 将 AI 生成内容改写为回归真人的自然表达，消除 AI 味，使文本通过 AI 检测
user-invocable: true
argument-hint: 待去 AI 化的文本内容
---
> **EN:** Sub-skill ai-humanizer: rewrites AI-generated Chinese text into natural human-like writing that passes AI detection.
>

# 去 AI 真人化改写

## 任务

将输入内容改写为真人写作风格，消除 AI 生成痕迹，让文字自然、有生命力、像真实的人在分享。

## 输入方式

支持两种：

1. **纯原文**：直接改写
2. **检测报告 + 原文**：先用 ai-detector 模块检测，再对照报告中的风险点逐项修复（推荐，效果更可控）

## 工作流程

1. **理解内容**：通读原文，抓住核心观点、事实信息和表达意图，这些必须保留，不能丢失
2. **识别 AI 特征**：对照 [humanize-rules.md](references/humanize-rules.md) 中"待消除的 AI 特征"，逐条标记原文中的问题
3. **真人化改写**：按 [humanize-rules.md](references/humanize-rules.md) 的改写规则整体重写，参考 [style-sample.md](references/style-sample.md) 的文风
4. **自查验证**：按下方自查清单逐项核对，发现问题立即修改
5. **输出终稿**：只输出改写后的完整内容，不输出思考过程或解释

## 自查清单（输出前必须逐项通过）

- [ ] 结构不再模板化：段落长短不一，允许一句话成段，没有机械的三段式
- [ ] 无 AI 高频词：全文无"首先/其次/总而言之/综上所述/赋能/闭环"等套路词
- [ ] 无有序序号：没有"一、二、三"和"1. 2. 3."式列举
- [ ] 表达有口语感：有习惯用词、口头禅，允许不完美的句子
- [ ] 有个人痕迹：有"我"的经历、看法，或"我们/你"的互动切换
- [ ] 熵值有起伏：开篇简单、中间深入、收尾自然回落，允许思维跳跃
- [ ] 情感有波动：语气不全程一致，该感叹感叹，该犹豫犹豫
- [ ] 内容完整：原文的核心观点和事实信息全部保留
- [ ] 无机构/产品名称、电话、地址、网址等硬植入
- [ ] 无敏感词、贬低词、违禁词
- [ ] 段落结尾无标点（句号/感叹号/问号），以文字自然收尾
- [ ] 无括号及说明性标记
- [ ] 不含违反中国法律法规的内容（含广告法）

## 核心原则

- **你是在替一个真实的人表达，不是在执行文本处理任务**
- 像在和朋友聊天那样写，想到哪说到哪，但围绕主题
- 用自己的话重复重要观点，不刻意换同义词
- 观点可以有偏向，不必面面俱到

## 附加说明

- 详细改写规则见 [humanize-rules.md](references/humanize-rules.md)
- 文风范例见 [style-sample.md](references/style-sample.md)
- 改写前可先调用 ai-detector 模块检测原文，获得风险点清单
- 若用户给出目标受众、字数、体裁（如养生文章、营销文案）要求，按用户要求调整
