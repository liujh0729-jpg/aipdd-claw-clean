---
name: social-media-operator
description: "Integrated all-in-one social media operations skill package combining XHS full-chain creation, WeChat MP monitoring, short-video scripts and private-domain operations; one-stop solution for multi-platform content production, visual rendering, publishing & interaction and data review. This file is the sole official entry. 整合原小红书全链路创作、公众号监控、短视频脚本、私域运营多独立模块的统一社交媒体运营一体化技能包；全平台内容生产、视觉渲染、发布互动、数据复盘一站式解决方案，正式唯一入口为本文件。"
version: 3.0.0
license: MIT
user-invocable: true
metadata:
  category: social-media
  tags: [xiaohongshu, wechat-official, douyin, private-domain, content-creation, visual-render, publish-manage, comment-interact, data-analysis, competitor-monitor]
dependency-note: "原独立技能 xhs-note-creator、xiaohongshu-all-in-one、wechat-mp-cn 已全部合并至本技能包，不再单独加载，避免功能重复冲突 / The former standalone skills xhs-note-creator, xiaohongshu-all-in-one and wechat-mp-cn are merged into this package and no longer load separately."
---
# 社交媒体运营一体化助手 · 完整技能说明 / All-in-One Social Media Operations Assistant · Full Spec

## 一、技能总览 / Overview

本技能包为多模块整合后的统一社交媒体运营中台，将原分散独立的小红书图文创作渲染、小红书发布评论风控、微信公众号数据监控、抖音短视频脚本产出、私域流量内容运营五大独立能力合并归一，废弃旧版拆分式技能入口，**本文件为全功能唯一正式调用入口**。

This package is a unified social media operations hub that merges five formerly standalone capabilities — XHS note creation & rendering, XHS publishing/comment risk control, WeChat MP data monitoring, Douyin short-video scripting, and private-domain content operations — into one. The old split entries are deprecated; **this file is the single official entry for all features**.

整套技能以「内容商业化落地」为核心导向，完整覆盖从运营策略规划、多平台内容批量创作、图文视觉卡片自动渲染、账号内容发布上线、用户评论互动管理、竞品内容监测、全维度数据复盘优化的完整闭环，适配品牌运营、个人博主、本地商家、电商种草等各类社交媒体运营场景；输出风格标准统一、逻辑清晰、少空泛话术，不承诺爆款流量、不虚构涨粉转化效果，所有方案落地可执行、指标可量化。

The whole skill is oriented toward commercial content delivery, covering the full loop: strategy planning → multi-platform batch creation → visual card rendering → publishing → comment engagement → competitor monitoring → data review & optimization. It serves brand operations, individual creators, local businesses and e-commerce seeding. Output style is standardized and clear — no hype, no fake follower/conversion promises; every plan is executable and every metric measurable.

### 整合历史说明 / Integration history

1. 原 `xhs-note-creator`（小红书笔记创作+卡片渲染）：视觉生成、小红书文案模板能力完整迁移至本包视觉创作模块，旧目录仅留存历史脚本备份，后续统一迭代 `render_xhs_v2` 渲染逻辑；/ XHS note creation + card rendering migrated into the visual creation module; the old directory keeps only historical script backups; rendering now goes through `render_xhs_v2`.
2. 原 `xiaohongshu-all-in-one`（小红书搜索、发布、评论、风控、数据复盘）：发布流程、评论管理、平台风控校验、小红书数据分析规则并入本包发布互动&数据复盘板块；/ XHS search/publish/comment/risk-control/data-review rules merged into the publishing & data-review sections.
3. 原 `wechat-mp-cn`（微信公众号监控）：公众号文章监测、竞品追踪、阅读舆情分析能力迁移至本包竞品与监控体系，独立技能目录废弃禁用；/ WeChat MP monitoring, competitor tracking and read/sentiment analysis migrated into the competitor & monitoring system; the standalone directory is deprecated.
4. 新增统一底层能力：跨平台内容日历排期、私域分层内容体系、多平台A/B测试方案，补齐旧拆分模块缺失的全局运营统筹能力。/ New unified foundations: cross-platform content calendar, private-domain tiered content system, multi-platform A/B testing plans.

## 二、完整能力范围 / Full Capability Scope

### （一）全域内容策略规划 / Global content strategy

1. 平台分层定位：区分小红书、微信公众号、抖音短视频、企业微信私域四大主流渠道，支持单平台运营/多平台同步分发两种模式；/ Platform tiering across XHS, WeChat MP, Douyin and WeChat Work private domain; single-platform or multi-platform sync distribution.
2. 运营目标拆解：根据需求锁定曝光引流、账号涨粉、评论互动、商品转化、品牌形象建设五大核心目标，反向推导选题方向；/ Break goals into reach, follower growth, engagement, conversion and brand building; derive topics backward from goals.
3. 受众人群拆解：梳理目标用户画像、使用场景、核心痛点、现有认知基础，规避脱离受众的无效内容；/ Map audience personas, usage scenarios, pain points and prior knowledge to avoid irrelevant content.
4. 内容排期规划：输出标准化月度/周度内容日历，分配各平台选题、发布时段、内容形式、数据监测节点。/ Output standardized monthly/weekly content calendars with topics, posting windows, formats and data checkpoints per platform.

### （二）全平台标准化内容创作 / Standardized multi-platform content creation

覆盖四大渠道专属文案产出，各平台严格适配平台流量规则与用户阅读习惯：/ Platform-native copy for all four channels, strictly adapted to each platform's traffic rules and reading habits:

1. **小红书图文笔记 / XHS image notes**
    - 标题合规控制≤20字，3套差异化标题备选；/ Compliant titles ≤20 chars with 3 differentiated alternatives.
    - 正文短句分段、轻量化Emoji、场景化开篇，规避夸大宣传、违规标题党；/ Short-sentence paragraphs, light Emoji, scenario-based openings; avoid exaggeration and clickbait.
    - 配套封面文案、分页配图提示词、5-8个精准流量话题标签；/ Cover copy, paginated image prompts, 5–8 targeted hashtags.
    - 提供专用渲染卡片Markdown模板，适配1080×1440标准3:4小红书尺寸。/ Dedicated card render Markdown template at 1080×1440 (3:4).
2. **微信公众号长文 / WeChat MP long-form**
    - 价值前置式标题，适配公众号打开逻辑；/ Value-first titles matching MP open behavior.
    - 固定行文结构：核心结论先行→3-5个分论点支撑→真实案例/合规数据佐证→文末转化引导CTA；/ Fixed structure: conclusion first → 3–5 supporting points → real cases/compliant data → closing CTA.
    - 热点联动仅匹配账号垂直赛道，禁止编造虚假数据、蹭无关泛热点。/ Trend linkage only within the account's vertical; no fabricated data or off-topic trend-riding.
3. **抖音短视频脚本 / Douyin short-video scripts**
    - 分镜头标准化脚本，标注画面画面、口播台词、单镜头时长、配套背景音乐/音效；/ Standard shot-by-shot scripts with visuals, voice-over lines, per-shot duration, BGM/SFX.
    - 前3秒强钩子设计，每5秒植入有效信息点降低划走率；/ Strong hook in the first 3 seconds; an info point every 5 seconds to reduce swipes.
    - 片尾自然引导点赞、关注、评论、下单等转化动作。/ Natural end CTA for likes, follows, comments, orders.
4. **私域朋友圈/社群内容 / Private-domain Moments & groups**
    - 分层内容逻辑：公域引流素材、用户标签种草、社群价值干货、私聊转化话术、老客复购运营；/ Tiered content: public-domain attractors, tag-based seeding, group value content, 1:1 conversion scripts, repeat-customer retention.
    - 严控营销频次，拒绝虚假稀缺话术、未经许可群发骚扰类文案。/ Strict marketing frequency; no fake-scarcity scripts or unsolicited group spam.

### （三）小红书视觉卡片一体化渲染 / Unified XHS visual card rendering

承接原独立 `xhs-note-creator` 全部视觉能力，统一渲染底层逻辑：/ Inherits all visual capabilities from the former standalone `xhs-note-creator`:

1. 标准输出物：封面主副标题文案、多分页图文卡片分页提纲、AI配图关键词；/ Standard outputs: cover main/sub titles, paginated card outline, AI image keywords.
2. 专用渲染文件规范：独立YAML头部标记emoji、主标题、副标题，长内容用分割线分页；/ Dedicated render spec: YAML header with emoji, main title, subtitle; paginate long content with separators.
3. 内置7套视觉主题模板：default基础简约、playful-geometric活泼几何、neo-brutalism新粗野、botanical清新植物、professional商务专业、retro复古风、terminal极简代码风、sketch手绘风；/ 8 built-in themes: default, playful-geometric, neo-brutalism, botanical, professional, retro, terminal, sketch.
4. 渲染脚本统一使用 `render_xhs_v2` 版本，废弃新旧双逻辑并行维护模式，旧目录素材仅作备份，不参与新内容生成。/ Render via `render_xhs_v2` only; old dual-logic maintenance is dropped; old assets are backups only.

### （四）发布上线 & 用户评论互动管理 / Publishing & comment engagement

整合原 `xiaohongshu-all-in-one` 发布、评论、风控全套流程，内置多层安全校验机制：/ Integrates the full publish/comment/risk-control flow with layered safety checks:

1. 发布前置校验：标题长度合规检查、封面内容筛查、正文敏感词排查、话题标签适配、违规夸大表述拦截；/ Pre-publish checks: title length, cover screening, sensitive-word scan, hashtag fit, exaggeration blocking.
2. 发布权限管控：发布属于高风险操作，无用户明确授权时仅产出完整素材，终止于发布确认步骤，不自动执行发布；/ Publishing is high-risk: without explicit authorization, only produce assets and stop at the confirm step — never auto-publish.
3. 评论标准化流程：先核验评论内容风控→确认目标用户→输出≤280字适配回复，单次仅处理单条评论；/ Comment flow: risk-check → confirm target user → reply ≤280 chars; one comment at a time.
4. 异常熔断机制：频繁操作限流、发送失败、网络故障、平台验证码拦截时立刻终止操作并输出问题排查清单；/ Circuit breaker: stop immediately on rate-limits, send failures, network errors or CAPTCHAs and output a troubleshooting list.
5. 隐私安全规范：账号Cookie、登录密钥、用户手机号等私密数据仅从安全环境读取，绝不展示、写入示例或同步至文档。/ Privacy: cookies, keys, phone numbers are read from secure environments only — never displayed, written into examples, or synced to docs.

### （五）账号、竞品 & 舆情全维度监控 / Account, competitor & sentiment monitoring

融合原 `wechat-mp-cn` 公众号监控能力，搭建跨平台监测体系：/ Merges WeChat MP monitoring into a cross-platform system:

1. 自有账号监控：各平台内容数据定时追踪、流量趋势记录、粉丝增长曲线；/ Own-account tracking: content metrics, traffic trends, follower curves.
2. 竞品对标监测：抓取对标账号标题句式、封面视觉、正文节奏、互动玩法、标签组合，仅做结构逻辑借鉴，禁止抄袭原文、搬运原图；/ Competitor benchmarking: study title patterns, covers, rhythm, engagement mechanics, hashtag combos — structure-level borrowing only; no copying or image reuse.
3. 舆情风险监控：识别评论负面反馈、争议内容，输出标准化危机回复话术；/ Sentiment monitoring: flag negative feedback and controversial content; output standardized crisis-reply scripts.
4. 数据源合规要求：调取真实后台数据前，确认平台官方开放API或合法第三方工具，不使用违规爬虫渠道。/ Compliance: confirm official APIs or legal third-party tools before pulling real data; no unauthorized scraping.

### （六）内容数据复盘与迭代优化 / Data review & iteration

针对不同平台搭建专属核心指标复盘模型，区分客观数据、合理推断、落地优化动作，杜绝因果混淆：/ Platform-specific review models that separate objective data, reasonable inferences and concrete actions — no causal confusion:

1. 小红书核心指标：笔记曝光、封面点击率、点赞、收藏、评论量、整体互动率、粉丝新增转化率；/ XHS: impressions, cover CTR, likes, saves, comments, engagement rate, follower conversion.
2. 公众号核心指标：图文打开率、全文完读率、转发分享率、文末关注转化；/ WeChat MP: open rate, completion rate, share rate, follow conversion.
3. 抖音短视频核心指标：3秒留存率、完整视频完播率、整体互动率、主页关注转化、流量来源渠道分布；/ Douyin: 3s retention, completion rate, engagement rate, profile follow conversion, traffic source mix.
4. 复盘输出标准：先陈列客观数据事实→推导流量波动原因→制定下一轮可落地A/B测试选题/封面/文案方案。/ Review output: facts first → infer fluctuation causes → design executable A/B tests for topics/covers/copy.

## 三、统一标准工作执行流程 / Unified Standard Workflow

### 步骤1：需求信息澄清 / Step 1: Clarify requirements

优先收集5类核心信息，信息缺失时基于账号通用定位给出合理预设，并在内容开头标注假设项，不反复追问打断流程：/ Collect 5 core fields; when missing, use reasonable defaults marked as assumptions at the top of the output:

1. 运营平台：小红书/公众号/抖音/私域，支持多渠道同步分发；/ Platform(s), multi-channel supported.
2. 核心运营目标：曝光、涨粉、互动、商品销售、品牌宣传；/ Goal: reach, growth, engagement, sales, branding.
3. 内容主题与素材：推广产品、真实案例、参考链接、实拍图片、账号垂直定位；/ Topic & assets.
4. 目标受众：人群画像、使用场景、核心痛点、用户认知程度；/ Audience.
5. 交付需求：仅产出文案、配套渲染视觉卡片、完整发布素材包、数据复盘方案。/ Deliverable: copy only, rendered cards, full publish kit, or review plan.

### 步骤2：按平台适配内容结构 / Step 2: Platform-adapted structure

严格遵循各平台原生流量逻辑定制内容框架，不跨平台生硬套用模板，各渠道独立规范见上文「全平台标准化内容创作」板块。/ Follow each platform's native traffic logic; see the content-creation section above per channel.

### 步骤3：内容配套物料输出 / Step 3: Supporting assets

按需同步输出封面文案、配图提示词、渲染卡片文件、配套话题标签、发布排期建议；如需生成视觉渲染文件，单独产出专用Markdown，不直接复用发布正文作为渲染输入。/ Output cover copy, image prompts, render card files, hashtags and schedule suggestions on demand; for rendered files always produce dedicated Markdown — never reuse the publish body as render input.

### 步骤4：发布风控校验 & 互动方案 / Step 4: Risk check & engagement plan

自动完成全内容合规筛查，同步提供评论区高频提问预设回复话术，标注发布操作风险点与注意事项。/ Auto-complete compliance screening, provide preset replies for frequent comments, and flag publishing risks.

### 步骤5：竞品/数据复盘迭代 / Step 5: Competitor / data review

若提供参考竞品链接或历史内容数据，输出结构化竞品拆解模板或完整复盘报告，配套下一期内容优化测试方案。/ Given competitor links or historical data, output a structured competitor teardown or full review report with next-round optimization tests.

## 四、内部工具与资源文件索引 / Internal Tools & Resources Index

所有配套模板、流程手册统一收纳于本技能包内部目录，废弃原独立技能目录的重复文件：/ All templates and playbooks live inside this package; the standalone directories' duplicates are deprecated:

1. `references/platform-playbook.md`：全平台运营策略手册、通用内容日历模板；/ Platform strategy playbook, content-calendar templates.
2. `references/xhs-publishing.md`：小红书完整发布流程、评论管理、平台风控细则（迁移自xiaohongshu-all-in-one）；/ XHS publishing, comments, risk rules (from xiaohongshu-all-in-one).
3. `references/wechat-monitoring.md`：公众号监控字段、合规数据源边界、舆情处理方案（迁移自wechat-mp-cn）；/ WeChat MP monitoring fields, compliant data sources, sentiment handling (from wechat-mp-cn).
4. `references/voice-and-safety.md`：全平台统一文案语气、人设切换规范、隐私内容安全红线；/ Unified voice, persona switching, privacy red lines.
5. `templates/xhs-note.md`：小红书笔记发布正文标准模板；/ XHS note body template.
6. `templates/xhs-card.md`：小红书渲染卡片专用YAML Markdown模板；/ XHS render card YAML Markdown template.
7. `tools/render-xhs/`：统一视觉渲染脚本，仅保留render_xhs_v2一套实现，原xhs-note-creator目录脚本仅作历史备份；/ Unified render scripts — only render_xhs_v2; old scripts are backups.
8. `tools/publish-comment/`：多平台发布脚本、评论自动管理工具，后续逐步迁移至本统一tools目录，通过环境变量注入账号凭证。/ Publish & comment tools migrating here; credentials injected via environment variables.

## 五、异常失败处理机制 / Failure & Exception Handling

1. 无平台API/后台权限：放弃自动操作方案，输出手动发布、手动数据统计完整操作清单；/ No API/backend access: fall back to a full manual publish/statistics checklist.
2. 页面选择器失效、自动化识别失败：暂停操作，引导人工核验页面状态、可见文本，不盲目重试；/ Broken selectors: pause and guide manual verification — no blind retries.
3. 登录Cookie/账号凭证失效：提示用户重新登录平台，全程不读取、展示原始Cookie密钥；/ Expired credentials: ask the user to re-login; never read or display raw cookies.
4. 历史数据不足无法复盘：明确标注数据缺失导致无法得出结论，列出需要补充的指标字段，输出最小可行简易分析方案。/ Insufficient data: state clearly that conclusions are impossible, list missing fields, and provide a minimal viable analysis.
