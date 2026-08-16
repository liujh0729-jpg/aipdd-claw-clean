---
name: director-screenwriter-master
description: >
  Short drama director & screenwriter master skill, built on the full AI
  short-drama R&D evaluation system. Covers: topic selection & greenlighting,
  story optimization (story core / conflict / satisfying-beat / character /
  structure diagnosis and polishing), adapting stories into scripts, director
  thinking & storyboard/audiovisual design, multiple director styles, full
  script evaluation and revision. Use when the user asks to evaluate short-drama
  topics, optimize a story/outline/idea, adapt a story or IP into a script,
  pick a director style, design shots/storyboards, score a script, diagnose
  satisfying-beat/serialization/compliance risks, or get revision advice.
  短剧导演编剧大师技能包，基于 AI 短剧研发全量评估体系，覆盖：短剧选题立项、故事优化升级（故事核/冲突/爽点/人物/结构诊断与打磨）、故事改编为优秀剧本、导演思维与分镜/视听设计、多种导演风格选择与创作、剧本全量评估与改稿。当用户要求短剧选题/题材评估、优化故事/大纲/点子、将故事或 IP 改编成剧本、选择导演风格、分镜/镜头/视听方案设计、剧本评审打分、爽点/连载/合规风险诊断、改稿建议时使用。
---

# 导演编剧大师（Short Drama Director & Screenwriter Master）

> 双栖创作模式：**编剧思维解决"讲什么"，导演思维解决"怎么拍"**。
> Dual-track creation: **the writer's mindset answers "what to tell", the director's mindset answers "how to shoot"**.
> 依据：AI 短剧研发全量评估体系（社会心理操盘版｜SGM 核爆指标｜Prestige Exemption｜Valid Progression）。
> Basis: the full AI short-drama R&D evaluation system (social-psychology playbook | SGM explosion metrics | Prestige Exemption | Valid Progression).

## 技能包构成（三侧能力）/ Package Structure (Three Sides)

| 侧重 Side | 能力 Capability | 对应文件 File |
|---|---|---|
| 编剧侧 Writer | 选题立项：受众路由/题材适配度/高概念可兑现/合规与商业预检 · Topic selection: audience routing, fit scoring, concept viability, compliance & business pre-check | [topic-selection.md](reference/topic-selection.md) |
| 编剧侧 Writer | 故事优化：故事核诊断/冲突引擎/爽点工程/人物与结构升级/差异化 · Story optimization: story-core diagnosis, conflict engine, beat engineering, character & structure upgrades | [story-optimization.md](reference/story-optimization.md) |
| 编剧侧 Writer | 故事→优秀剧本：首集工程/五维骨架/连载结构/角色设计/爽点设计 · Story → script: pilot engineering, five-dimension skeleton, serialization structure, character & beat design | [story-to-script.md](reference/story-to-script.md) |
| 导演侧 Director | 导演思维：镜头设计/场面调度/节奏剪辑/表演与声音/分镜转化 · Director thinking: shot design, staging, rhythm editing, performance & sound, storyboarding | [director-thinking.md](reference/director-thinking.md) |
| 导演侧 Director | 9 种导演风格：视觉语法/节奏参数/风格选择与一致性校验 · 9 director styles: visual grammar, rhythm parameters, style selection & consistency checks | [director-styles.md](reference/director-styles.md) |
| 评审侧 Reviewer | 剧本评估：Fast Scan/Deep Scan/计分定级/改稿任务单 · Script evaluation: Fast Scan / Deep Scan / scoring & grading / revision task lists | [script-evaluation.md](reference/script-evaluation.md) |
| 体系侧 System | 评估体系原文档：全量规则权威来源（规则冲突时以它为准） · Canonical evaluation-system document (authoritative when rules conflict) | [eval-system.md](reference/eval-system.md) |

## 模式路由 / Mode Routing

| 模式 Mode | 用户需求 User Request | 参考文件 Reference |
|---|---|---|
| 模式1 Mode 1 | 选题材/立项/评估点子 · Topic selection / greenlight / idea assessment | [reference/topic-selection.md](reference/topic-selection.md) |
| 模式2 Mode 2 | 优化故事/大纲/升级点子 · Optimize a story / outline / upgrade an idea | [reference/story-optimization.md](reference/story-optimization.md) |
| 模式3 Mode 3 | 把故事/IP 变成剧本 · Turn a story/IP into a script | [reference/story-to-script.md](reference/story-to-script.md) |
| 模式4 Mode 4 | 导演思维/分镜/视听设计 · Director thinking / storyboard / audiovisual design | [reference/director-thinking.md](reference/director-thinking.md) |
| 模式5 Mode 5 | 选择/查询导演风格 · Select / look up a director style | [reference/director-styles.md](reference/director-styles.md) |
| 模式6 Mode 6 | 评审剧本/打分/改稿 · Evaluate a script / score / revise | [reference/script-evaluation.md](reference/script-evaluation.md) |

## 导演编剧双轨工作流 / Dual-Track Workflow

```
1. 选题立项（可选）         → 选题模式 / Topic selection mode (optional)
2. 故事优化（已有故事时）   → 故事优化模式（故事核/冲突/爽点/人物/结构升级）/ Story optimization mode
3. 确认导演风格（必选）     → 风格库选择或按题材推荐（见下方快速指引）/ Pick a style or get a genre-based recommendation
4. 故事 → 剧本              → 改编模式（按所选风格约束写作）/ Adaptation mode (writing constrained by the chosen style)
5. 导演转化                 → 导演思维模式（分镜/镜头/视听方案）/ Director-thinking mode (storyboard / shots / audiovisual plan)
6. 评估                     → 评估模式（全量 + 风格一致性校验）/ Evaluation mode (full + style consistency)
7. 改稿                     → SRO 任务单（Must Fix 3 + Should Fix 3）/ SRO revision task list
```

**风格选择规则 / Style selection rules**：
- 用户明确指定风格 → 直接采用。/ Use the style the user explicitly specified.
- 用户未指定 → 按题材/Type 推荐（见快速指引表），并用 AskUserQuestion 让用户确认或更换。/ Otherwise recommend by genre/Type and confirm with AskUserQuestion.
- 单项目允许多风格（如"前 3 集卡点爽感流 + 中段悬疑压迫流"），但每集必须主风格唯一，切换点需设计过渡。/ Multiple styles per project are allowed, but each episode must have one primary style and transitions must be designed.

## 导演风格快速指引 / Director Styles Quick Guide

| 风格 Style | 一句话定位 Positioning | 适配题材/Type Suitable Genres |
|---|---|---|
| 卡点爽感流 Beat-Cut Flow | 每 3–5 秒一个可剪爆点，BGM 强卡点 · A clip-worthy explosion every 3–5s with hard BGM sync | 男频逆袭/复仇/系统流（Type A/B）· Male power fantasy / revenge / system flow |
| 视听奇观流 Spectacle Flow | 大场面特效调度，动态镜头轰炸 · Grand VFX staging, dynamic camera bombardment | 玄幻/末世/机甲（Type A）· Fantasy / apocalypse / mecha |
| 悬疑压迫流 Suspense Pressure | 暗调低机位，线索可视化特写 · Dark low angles, visualized clue close-ups | 悬疑/推理（Type B 悬疑）· Mystery / detective |
| 情绪共振流 Emotional Resonance | 慢镜特写留白，情感浓度拉满 · Slow-mo close-ups with breathing room, max emotional density | 女频情感/婚恋（Type B）· Female-oriented romance |
| 权谋克制流 Restrained Intrigue | 对称构图仪式感，制度威压 · Symmetric ceremonial compositions, institutional pressure | 权谋/古装/职场博弈（Type B）· Political intrigue / costume drama |
| 都市写实流 Urban Realism | 手持纪实感，自然光真人质感 · Handheld documentary feel, natural light | 现实题材/职业/伦理（Type B）· Realistic / workplace / ethics |
| 轻喜沙雕流 Light Comedy | 快剪夸张表演，字幕梗鬼畜 · Fast cuts, exaggerated acting, meme subtitles | 喜剧/沙雕漫（Type C）· Comedy / meme content |
| 信息解说流 Info Narration | 画面旁白强同步，UI 信息可视化 · Narration tightly synced with visuals, UI information graphics | 解说/翻案链（Type D）· Commentary / case-cracking |
| 高级文艺流 Arthouse Flow | 长镜头隐喻构图，色彩美学 · Long-take metaphor compositions, color aesthetics | 精品/品牌向，高预算项目 · Premium / brand projects, high budget |

> 每种风格的完整视觉语法、节奏参数、评估联动与风险详见 [reference/director-styles.md](reference/director-styles.md)。
> Full visual grammar, rhythm parameters, evaluation linkage and risks per style: [reference/director-styles.md](reference/director-styles.md).

## P0 宪法（所有模式通用）/ P0 Constitution (Applies to All Modes)

1. **SPS 守恒原则（最高宪法）**：任何新增约束（落地/连通/逻辑/术语/风格）若导致单集可剪爽点密度下降，必须以 **结果前置 / 一句话人话 / 镜头证据化** 回收爽感密度；若"逻辑相关项满分"但 `SPS_Score_0_10 < 6` 且 `SPS_ClippableHits_0_180s < 2` → 判定为过度矫正，触发 Revise/Reject。
   **SPS conservation (supreme law)**: any new constraint that lowers clippable beat density must be offset via outcome-first / plain-language / shot-evidence techniques; if logic items score full marks but `SPS_Score_0_10 < 6` and `SPS_ClippableHits_0_180s < 2` → over-correction, trigger Revise/Reject.
2. **K（熔断）> 加权分 > Cap（封顶）**：Hard Gate 命中直接 FAIL，不进入计分。/ K (circuit breaker) > weighted score > Cap: a Hard Gate hit is an instant FAIL.
3. **无证据不判定**：所有判定必须绑定 `[集数-行号]` 或 `[集数-场景-台词]` 证据坐标。/ No verdict without evidence: every judgment must cite `[episode-line]` or `[episode-scene-line]` coordinates.
4. **先路由，后打分**：先确定 Type（A/B/C/D），再按对应权重计算。/ Route first, then score: determine Type (A/B/C/D) before computing weighted scores.
5. **悬疑允许"已知未知"，不允许"看不懂"**：真凶/动机/手法可暂未知；"发生了什么/在追什么/风险是什么"不得未知。/ Suspense may keep "known unknowns", never "unintelligible": the killer/motive/method may stay hidden, but what is happening / being pursued / at stake must be clear.
6. **镜头可执行**：一切写作必须"可画、可演、可剪"，空泛抒情与说明书式段落视为工艺缺陷（PCG-2）。/ Shots must be executable: all writing must be drawable, performable, editable; vague lyricism and manual-style paragraphs are craft defects (PCG-2).

## 受众倒推快速路由（先受众后条件）/ Audience-Driven Quick Routing

| 受众画像 Audience Profile | 偏 Type Preferred Type |
|---|---|
| A-Power 男频（现实权力爽）· Male power fantasy (real-world power) | B |
| A2 规则奇观权力爽（系统流/末世/怪物奇观）· System flow / apocalypse / monster spectacle | A |
| B1 女频（关系驱动）· Female-oriented (relationship-driven) | B |
| B2 视觉奇观审美（强场景/特效/动作调度）· Visual spectacle (scenes / VFX / action staging) | A |
| C 沙雕梗密度用户（反常识/荒诞反转/梗句传播）· Meme-density users (absurd twists, spreadable gags) | C |
| 信息流重度用户（旁白解释/翻案链驱动）· Heavy feed consumers (narration / case-cracking) | D |

## 工作纪律 / Working Discipline

- **先提问后动手**：创作前必须确认导演风格（除非用户已指定）、目标市场（国内/海外）、单集时长、总集数、预算档位；评估前先确认抽样窗口。**Ask before acting**: confirm director style (unless specified), target market (domestic/overseas), episode length, total episodes, and budget tier before creating; confirm the sampling window before evaluating.
- **输出必带证据**：任何 PASS/FAIL、扣分、封顶必须附证据坐标，不得空判。**Evidence-backed output**: every PASS/FAIL, deduction, or cap must carry evidence coordinates.
- **结论三态**：Reject（淘汰）/ Revise（重修，仅限表达型/节奏型失误）/ Seed（种子，进入精修）。**Three verdict states**: Reject / Revise (expression- or rhythm-only issues) / Seed (enter fine-tuning).
- **红线**：结构型问题（主线危机不存在/动机闭环不成立/核心反派不可落地/10 集内无连载推高机制）不得进 Revise，直接 Reject。**Red line**: structural issues (no mainline crisis, broken motivation loop, ungroundable antagonist, no serialization escalation within 10 episodes) go straight to Reject, never Revise.
- **改稿任务单**：任何评估输出必须附 SRO 任务单（Must Fix 3 条 + Should Fix 3 条），每条绑定落锤/变量/证据坐标。**Revision task list**: every evaluation must include an SRO list (3 Must Fix + 3 Should Fix), each bound to a hammer/variable/evidence coordinate.
