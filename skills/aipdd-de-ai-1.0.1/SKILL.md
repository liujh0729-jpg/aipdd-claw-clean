---
name: deai
version: 1.0.0
description: >
  Unified router for de-AI workflows. Routes requests to the ai-detector module
  for AI content scoring and to the ai-humanizer module for human-like
  rewriting, and can run the full detect-fix-recheck pipeline. Use when the
  user asks to check AI content, humanize text, remove AI flavor, or run the
  complete de-AI workflow.
  去 AI 工作流统一入口与索引：自动路由到 ai-detector（AI 含量检测）和 ai-humanizer（去 AI 真人化改写）两个子模块，支持检测、改写及串联全流程
user-invocable: true
argument-hint: 模式（检测/改写/全流程）+ 文本内容 / mode (detect/humanize/pipeline) + text
---

# 去 AI 统一入口 / De-AI Unified Entry

## 技能包功能与价值点 / What This Package Does & Why It Matters

### 这个技能包是干什么的 / What it is

「去 AI 技能包」（skills/ 目录）是一套完整的 AI 内容治理能力：**先量化检测内容的 AI 含量，再把 AI 味的内容改写为回归真人的自然表达，最后可复检验证改写效果**。适用于自媒体写作、营销文案、日常内容创作等需要消除 AI 味的场景。

The De-AI skill package is a complete AI-content governance toolkit: **quantify the AI-ness of content, rewrite it into natural human-sounding prose, then re-check to verify the improvement**. Built for self-media writing, marketing copy, and everyday content creation where an "AI flavor" must be removed.

### 核心功能 / Core features

1. **AI 含量检测（ai-detector）/ AI content detection (ai-detector)**
   - 六维检测体系：结构模板化、语言模式与词汇、句式与表达、内容熵值波动、情感与主观性、违禁特征 / Six-dimension detection: templated structure, language patterns & vocabulary, sentence patterns, content entropy variance, emotion & subjectivity, prohibited features
   - 量化评分：输出 AI 含量百分比（0-100%），对照五级评级（人类写作 → 疑似完全 AI 生成）/ Quantitative score: AI percentage (0-100%) mapped to a five-level rating (human-written → likely fully AI-generated)
   - 风险明细：每条风险点附原文证据、问题原因、具体修改建议 / Risk details: each risk cites original evidence, cause, and a concrete fix

2. **去 AI 真人化改写（ai-humanizer）/ Humanizing rewrite (ai-humanizer)**
   - 完整继承经过实战验证的反 AI 方法论（RTF 结构化提示词框架 + 认知模拟机制 + 熵值动态平衡）/ Inherits the battle-tested anti-AI methodology (RTF structured prompt framework + cognitive simulation + entropy balancing)
   - 四大真人化策略：思维过程真实化、表达不完美化、情感波动自然化、视角切换自然化 / Four humanizing strategies: realistic thinking, imperfect expression, natural emotion swings, natural perspective shifts
   - 硬性规则保障：禁用词表、禁止序号、段落结尾无标点、无机构产品植入 / Hard rules: banned-word list, no numbering, no punctuation at paragraph ends, no institutional/product plugs
   - 附参考文风范例，改写风格贴近真实写作 / Includes style samples so rewrites read like real writing

3. **一体化工作流（本文件，统一入口）/ Unified workflow (this file, single entry)**
   - 自动路由三种模式：detect（仅检测）/ humanize（仅改写）/ pipeline（检测 → 改写 → 复检对比）/ Auto-routes three modes: detect / humanize / pipeline (detect → rewrite → recheck comparison)
   - pipeline 模式形成闭环：检测报告 → 逐项修复改写 → 复检前后对比，效果可量化验证 / pipeline closes the loop: report → itemized fixes → before/after comparison with quantifiable results

### 价值点 / Value

| 价值 Value | 说明 Description |
|------|------|
| 检测可量化 Measurable detection | 不再是凭感觉判断"像不像 AI"，而是百分比评分 + 证据引用 + 修改建议 · Not gut-feel "does it sound AI?" but a percentage score + evidence + fix suggestions |
| 改写可验证 Verifiable rewriting | pipeline 模式输出改写前后 AI 含量对比，效果一目了然 · pipeline outputs a before/after AI-content comparison |
| 规则可继承 Shared rules | 检测与改写共用同一套 AI 特征评估体系，检测出的问题即改写的对照清单 · detection and rewriting share one feature system; found issues become the rewrite checklist |
| 调用统一 Unified contract | 外部系统（如 workbuddy）只需按一个统一契约调用，无需了解内部结构 · external systems call one contract without knowing internals |
| 即插即用 Plug & play | 三个模块相互独立，可单独使用也可串联成完整流程 · three independent modules, usable alone or chained |
| 有据可依 Proven basis | 方法论源自经过实战验证的反 AI 检测提示词（姚金刚 V2.0），非凭空设计 · methodology derives from a battle-tested anti-AI prompt set (Yao Jingang V2.0) |

## 定位 / Positioning

本 skill 是去 AI 技能包（skills/ 目录）的统一入口与索引，把两个子模块整合为一条可编程调用的工作流，方便外部系统（如 workbuddy）按统一契约调用。

This skill is the unified entry and index for the De-AI package, integrating the two submodules into one programmatically callable workflow for external systems (e.g. workbuddy).

**子模块索引 / Submodule index**：

| 子模块 Submodule | 文件 File | 职责 Responsibility |
|--------|------|------|
| ai-detector | [ai-detector/detector.md](ai-detector/detector.md) | AI 含量检测，输出评分与风险明细 · AI-content scoring and risk details |
| ai-humanizer | [ai-humanizer/humanizer.md](ai-humanizer/humanizer.md) | 去 AI 真人化改写，输出自然表达 · Humanizing rewrite output |

## 模式路由 / Mode routing

| 模式 Mode | 触发词（用户请求中包含）Trigger words (in user request) | 执行 Execution |
|------|--------------------------|------|
| detect | 检测、AI含量、AI率、查一下AI、是不是AI写的 · check AI, AI content, AI rate | 调用 ai-detector 完整流程 · run the full ai-detector flow |
| humanize | 改写、去AI、去AI味、真人化、自然一点、像人写的 · humanize, rewrite, remove AI flavor | 调用 ai-humanizer 完整流程 · run the full ai-humanizer flow |
| pipeline | 处理一下、优化、完整流程、全流程 · process, optimize, full flow | 串联：检测 → 改写 → 复检对比 · detect → rewrite → recheck |

路由规则（按优先级）/ Routing rules (by priority)：

1. 用户明确说"检测"类词 → detect 模式 / Explicit detection words → detect
2. 用户明确说"改写/去AI"类词 → humanize 模式 / Explicit rewrite/humanize words → humanize
3. 用户说"处理/优化"或未指明模式 → pipeline 模式（默认）/ "process/optimize" or unspecified → pipeline (default)
4. 用户粘贴的是检测报告 + 原文 → 按报告风险点执行 humanize 模式 / Pasted report + source text → humanize per the report's risk points

## 执行规范 / Execution rules

### detect 模式 / detect mode

1. 读取 [ai-detector/detector.md](ai-detector/detector.md) 与 [ai-detector/references/detection-rules.md](ai-detector/references/detection-rules.md)，按其工作流程执行 / Read detector.md and detection-rules.md and follow their workflows
2. 输出标准检测报告（总评分、各维度得分表、风险点明细、修改建议）/ Output the standard report (total score, per-dimension table, risk details, fix suggestions)

### humanize 模式 / humanize mode

1. 读取 [ai-humanizer/humanizer.md](ai-humanizer/humanizer.md) 与 [ai-humanizer/references/humanize-rules.md](ai-humanizer/references/humanize-rules.md)、[ai-humanizer/references/style-sample.md](ai-humanizer/references/style-sample.md)，按其工作流程执行 / Read humanizer.md, humanize-rules.md and style-sample.md and follow their workflows
2. 输出改写终稿，不输出思考过程或解释 / Output only the final rewrite — no reasoning or explanations

### pipeline 模式 / pipeline mode

1. 先按 detect 流程检测原文，得到评分与风险点清单 / Run detect on the source first
2. 将检测报告连同原文交给 humanize 流程改写 / Hand the report + source to humanize
3. 对改写结果再次检测，输出前后 AI 含量对比 / Re-detect the rewrite and output the before/after comparison
4. 按顺序输出：检测报告 → 改写终稿 → 复检对比表 / Output in order: report → rewrite → comparison table

## 统一调用契约 / Unified call contract

### 输入格式 / Input format

```
mode: detect | humanize | pipeline
text: 待处理文本 / text to process
```

- mode 可省略，省略时按上述路由规则自动判断，仍无法判断则默认 pipeline / mode is optional; auto-routed when omitted, defaulting to pipeline
- 多个文本片段用空行分隔 / separate multiple text chunks with a blank line

### 输出格式 / Output format

| 模式 Mode | 输出 Output |
|------|------|
| detect | Markdown 检测报告 · Markdown report |
| humanize | 纯文本改写终稿 · plain-text final rewrite |
| pipeline | 检测报告 + 改写终稿 + 复检对比表 · report + rewrite + comparison table |

### 对比表模板 / Comparison template

```markdown
| 指标 Metric | 改写前 Before | 改写后 After |
|------|--------|--------|
| AI 含量 AI content | XX% | XX% |
| 主要残留风险 Remaining risks | XXX | XXX |
```

## 注意事项 / Notes

- 子模块文件是执行规范的唯一权威来源，执行前必须实际读取，不得凭记忆或摘要执行 / The submodule files are the sole authority for execution rules — always read them before executing, never rely on memory or summaries
- 检测与改写以中文文本为主 / Detection and rewriting are primarily for Chinese text
- 若用户只提供文本未指定模式，自动路由，无需反问 / When only text is given without a mode, auto-route without asking back
