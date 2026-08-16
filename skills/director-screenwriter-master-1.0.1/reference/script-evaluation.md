> **EN:** Mode 6 Script evaluation: dual-level review plus director/style checks — converts “feels good” into verifiable evidence coordinates, thresholds and formulas (sample → Fast Scan → three-state decision → Deep Scan → scoring → SRO revision tickets).
>
# 模式6：剧本评估（双级评审 + 导演/风格校验）

> 目标：把"感觉好不好看"转成**可复核的证据坐标 + 阈值 + 公式**，输出可复算、可复评、可质检的结论。
> 流程：抽样 → Fast Scan（防骗层 + 初筛）→ 三态决策 → Deep Scan（全量引擎 + 导演维度 + 风格一致性）→ 计分/等级 → SRO 改稿任务单。

## 0. 评估前必确认

- **导演风格**：创作时选定的风格（或本次评估为其指定推荐风格），作为风格一致性校验基准。
- **抽样窗口**：必抽 Ep1/Ep2/Ep3/付费点窗口（第 10–15 集选 1 集）/临近结局窗口（倒数 3–5 集选 1 集）。

Ep1 四强制检查点：3 秒钩子 / 15 秒答题 / 60 秒冲突树（≥2 条压强线并行）/ 结尾钩子。

## 1. Fast Scan（防骗层｜先跑，决定是否进入 Deep Scan）

5 项防骗层硬检查（全部必须绑定证据坐标）：

| 检查 | 内容 | FAIL 后果 |
|---|---|---|
| **U7 题眼兑现** | 高概念类：前 2 集 ≥1 处题眼具象化、前 10 集 ≥3 处（反差闭环或公开落锤） | FinalScore -= 5；Verdict 上限 Revise；risk_tags += U7_highconcept_not_realized |
| **U2A 一卡高潮** | 前 1–2 集出现高潮级事件（不可逆代价/公开对抗/主线落锤 三选二） | FinalScore -= 5；标 PCG_warning（首屏工艺失败） |
| **RCC-M 反派闭环** | 反派重大行动通过"要什么/怎么拿/如何承受风险"三问；高风险手段匹配同等级动机 | FinalScore -= 5；标 RCC-M_villain_incoherent |
| **CFS 双主角平衡** | 双/多主角：各自 ≥2 次破局 + ≥1 次公开落锤（前 10 集） | FinalScore -= 3；输出功能位重构任务单 |
| **RRL 关系坡度** | 关系驱动类：前 10 集 ≥3 级台阶（公开站队/共担代价/共享秘密） | FinalScore -= 3；Verdict 上限 Revise；标 RRL_relationship_jump |

快速裁决：U7/U2A/RCC-M 任一 FAIL → 直接 Revise/Reject（按可修复性与产线成本）；CFS/RRL FAIL → Revise（结构级任务单）；全 PASS → 进入初筛。

### 初筛 4 项必查（Fast Pass）

1. **Router_Quick**：Type + ACF 二值判定（≥60/<60）；<60 → Reject。
2. **SPS_Check**：`SPS_Score_0_10`（及格线 6 = 每 90s ≥1 个可剪爽点）+ `SPS_ClippableHits_0_180s`（前 3 分钟可剪爽点计数）；<6 → 默认 Reject。
3. **Hard Gates**：合规 C2 / 硬逻辑矛盾 / DCF 成本失控（命中任一 → Reject）。
4. **DW-90**：15s 答题 + 90s 首次交付（任一 FAIL 进入"是否可 Revise"判定）。

### 三态决策

- 🔴 **Reject**：Hard Gate 挂科 / ACF < 60 / SPS < 6 且不可修复 / 结构型坍塌（写不出可交付结果句）。
- 🟡 **Revise**：仅限**表达型/节奏型**失误（结构仍成立，SPS 机制明确）。准入示例：15s 三问能答清但 90s 缺结果句/证据镜头；爽点位置错位稀释 SPS。
- 🟢 **Seed**：全 Pass，进入 Deep Scan 精修池。

> 硬闸：结构型问题（主线危机不存在/动机闭环不成立/核心反派不可落地/10 集内无连载推高机制）不得进 Revise，直接 Reject。

## 2. Deep Scan（全量引擎｜仅 Seed）

### 2.1 理解成本 U-Scan

- **U1 15秒三问复述**：目标/阻碍/代价 一句话可复述（FAIL -= 5）。悬疑允许 Who/Why/How 未知，不允许"发生了什么/在追什么/风险是什么"未知。
- **U2 90秒结果句**：可复述的进展交付 + 证据坐标（FAIL -= 10）。悬疑等价：线索/排除/锁定/升级/不可逆代价。
- **U3 显性信息载体**：关键场景必须命中台词 / 可读 UI/文字 / 明确行为结果之一；≥2 个高理解成本场景 → -= 6。
- **U4 静默场景**：允许纯镜头语言，但 ≤6 秒或 ≤3 镜头、标 Silent=Y、必须承载 U2 等价交付。
- **U5 术语落地 + ProcessDump 检测**：只记录 `ProcessDump_Count` 与坐标，不直接扣分（唯一扣分入口见 6.13）。
- **U6 系统极简**（系统/面板/数值类）：前 5 集条件语句 >2 层 / 同集 ≥2 次换算解释 / 解释后 60s 无到账 → FAIL（FinalScore -= 5，R-Score 上调 1 档，Verdict 上限 Revise）。
- **U7 题眼兑现**：见防骗层（Seed 项目重新核验坐标）。

### 2.2 连载风险 Phase L（前 10 集）

- **L1 外部主线倒计时**：可复盘的外部节点持续推进。Type A 每 2–3 集推进；Type B 每 2 集；Type C 每 4–6 集但必须梗链升级；Type D 每 1–2 集新增关键信息。
- **L2 落锤密度**：单集有事实/权力/身份/资源/规则/舆论/法律结果落地（不是吵架）。Type A 前 10 集 ≥7 集落锤=绿，连续 2 集无=红；Type B ≥8 集=绿，连续 1 集无=黄，连续 2 集=红；Type C ≥9 集有梗锤=绿；Type D ≥8 集信息结算=绿。强制输出"是否落锤+标签+坐标"清单。
- **L3 持续对抗者**：对抗方持续施压、有升级路径、主角持续付代价；一拳倒/每集换小人/无升级链 → 黄/红。
- **L4 场景同构/疲劳**：同场景+同对话结构+同解决方式重复且信息增量≈0。Type A 同构 ≥3 次=红；Type B ≥2 次=黄、≥3 次=红；Type C 梗不升级=红；Type D 连续 2 集增量≈0=红。联动 VIS_Diversity/OPK_visual_homogeneity → L4-A 疲劳扣罚 -3。
- **L5 剧情连通率（套娃）**：禁止主线危机完全闭环。删集测试（优先 Ep4/5/6）：删掉该集 Ep10 结局是否必须改？"否" → 连通弱/水剧情。输出 `L5_case_id / L5_local_closed / L5_mainline_closed / L5_triggers_bigger_crisis / L5_causal_link_to_final / L5_evidence`。
  - **SW 结算窗口**：30–60 秒纯净结算；Ep3 后连续 ≥3 集无 SW=黄牌，≥5 集=红牌（焦虑跑步机）。悬疑题材可用"线索证据化/认知翻转/误导拆穿"作结算。
  - **L5-A 有效推进**：关系不可逆推进 / 秩序规则重定义 / 认知范式升级 → 亦算 PASS（需删集测试 MustRewrite 佐证）。
- **L6 悬疑清晰度 M-Scan**（仅 Type B 悬疑分支）：每集 ≥1 条可复述线索（证据化）+ ≥1 个新问题；连续 2 集缺失=红。每个关键谜面必须可归责（谁在隐瞒/为什么隐瞒）；作者未交代的空白=黄，累计升级红。
- **L_level 合成**：任一红=RED；0 红且 ≥2 绿=GREEN；其他=YELLOW。RED → FinalScore 封顶 84；YELLOW → 封顶 92。

### 2.3 五维量表（0–100，每维 5 子项 × 0–20）

| 维度 | 子项 |
|---|---|
| **SPS 内容价值** | 12字主爽点清晰度 / 心理代偿链 / 金句折算 / 评论区对立站队驱动 / 载体友好（短句可屏摄可口型） |
| **CAP 性格力** | 性格公理 2+1 / OOC 风险（受损率每 +1% 总分 -2）/ 主角动机稳定性 / 反派系统人格一致性 / 关键关系张力 |
| **B+3 硬骨架** | DW-90 二段式达标 / CFS 因果台阶完整性 / 兑现强度（结果型非解释）/ 单集闭环密度 / 中段变量注入与结局兑现一致性（B+3 < 80 → 总分封顶 85） |
| **APM 叙事动能** | 压强频率（每 3 集 ≥1 次专业打压）/ 系统不可逆压强 / 升级链连续 / 反转质量（位阶关系资源变化）/ 节奏推进 |
| **VIS 视觉张力** | 建模潜力 / 特效溢价空间 / 形变压力可控性 / UI 叙事价值 / 镜头化可执行 |

- **APM_Survival_Density**（末日/求生类硬约束）：每 10 集 ≥1 次倒计时级濒死（血条见底/资源见底/环境倒计时/感染进度条，可镜头化）；长期安全区装逼解说 → APM 归零 + 不得 A 档。
- **VIS_Diversity**（Type A/大招流硬约束）：同一核心道具/特效连续 3 次解决同级别危机后第 4 次必须异构；连续 4 次重合 → VIS 封顶 6/10 + L4-A 扣 -3。
- **IV 信息位移**（Type D 第六维）：资产化信息位移（画面层落地）/ Source Trace 来源追溯 / 每 15s 钩子 / V-Sync 说到即见 / 术语解释负担。

### 2.4 导演维度校验（对照导演思维模式）

- **镜头可执行度（PCG-2）**：连续"不可画/不可演/不可剪"的空泛抒情或说明书式段落 → -3 + 可镜头化改写方案。
- **落锤镜头可见性**：落锤是否"结果可见"（推镜/定格/UI 判定/反应镜头），还是仅台词宣布？台词宣布 = 判为"未落锤"（计入 L2）。
- **竖屏构图**：信息元素 >3 层/左右分屏式叙事 → 标高理解成本（U3）。
- **静默协议（U4）**：>6s 或 >3 镜头且无交付 → 高理解成本场景。
- **肢体互动分级**：>5s 深吻/贴身缠斗/复杂肉搏 → 强制改写（红线）。

### 2.5 风格一致性校验（依据风格库）

- **风格达标**：按所选风格的节奏参数/爽点形态校验（如卡点爽感流镜头均长 1.5–3s、每 90s ≥2 可剪爽点；权谋克制流每场必有局势改变落点）。未达该风格基准 → 进改稿建议（非 Pass/Reject 依据，属审美/工艺级）。
- **越界检查**：主风格之外大面积异质镜头语言 → 标 `Style_inconsistency`，进改稿建议。
- **规则优先**：风格与规则冲突时规则胜出（SPS 守恒/合规 C2/肢体红线/ARG 不可被风格豁免）。
- 风格线索卡点（SPS 守恒复核）：风格化表达若稀释每 90s 爽点密度（如高级文艺流长镜头无交付）→ SPS < 6 照常一票否决。

### 2.6 题材匹配度复核（ACF）

- Type A：ACF-A < 60 → 封顶 84；60–74 → 封顶 92。
- Type B：ACF-B < 60 → 封顶 84；60–74 → 封顶 92；ACF_B_1（职业高光）< 14 → ACF_B 封顶 74 + 标 job_highlight_weak + Type II 反差封顶 10。
- Type C：C-Fit ≥70 强支持，50–69 需补梗链升级。

### 2.7 SGM 社会心理矩阵（爽点质量制衡｜P0）

逐项选标签 + 绑坐标 + 一句话解释（≤20 字）：

| 指标 | 20分 | 10分 | 0分（扣分项） |
|---|---|---|---|
| **IAI 信息差势能** | 全知碾压（有认知崩塌坐标）/ 绝境盲盒（悬疑优先） | — | 认知同频（只能互殴/运气） |
| **SCPR 社会资本剥夺** | 杀人诛心（社会性死亡/背书崩塌/夺解释权） | 物理降维 | 隔靴搔痒（只动口舌） |
| **ELR 情绪杠杆** | 核爆杠杆（支点短→爆点毁灭性释放） | 线性对冲 | 疲劳通胀 |

- `SGM_Score_0_10 = round((IAI_pts + SCPR_pts + ELR_pts) / 6, 0)`（各 pts ∈ {0,10,20}）。
- **制衡**：SPS ≥6 但 SGM ≤3 → 等级封顶 B + 强制 Revise（补"资本剥夺/认知崩塌/杠杆爆点"其一）。
- 复仇/权谋/鉴渣/职场清算且 SCPR=⚫ → 必 Revise；前 10 集仍无 ≥🟡 → Reject。
- 悬疑豁免：IAI=🟡 可作满分；SCPR 可延迟，但前 10 集需 ≥1 次 🔴 或 ≥2 次 🟡。

### 2.8 硬闸与扣罚速查

| 规则 | 触发 | 动作 |
|---|---|---|
| 合规 C2 | 未成年细节化霸凌/虐待/性剥削 | HardGate FAIL，不进入计分 |
| 逻辑 L-Scan | 关键设定自相矛盾且当段不可修复 | HardGate FAIL |
| DCF 成本 | 高频不可控形变/极端动作不可代偿 | HardGate FAIL |
| Process Dump（6.13 唯一扣分入口） | Count==1 | FinalScore -= 3，SPS -= 1 |
| | Count≥2 | FinalScore -= 6，SPS -= 2，标 Dump-Heavy（默认 Revise，同时 DW-90 FAIL 则 Reject） |
| 6.13A 高级感豁免 | 连续 ≥3 句术语承担"权力/制度威压"+"延时闭环/服务 SGM"任意两项 | 不计 Dump |
| OOC | 受损率每 +1% | 总分 -2 |
| UI 遮脸（Type B） | ≥2 次/集 | -10 且分流 |
| Source Trace | 资产到账无来源 | B+3 兑现强度封顶 10；连续 2 集 → 封顶 92 |
| OPK 一键通关 | 同一技能连续 3 集主解矛盾且无新限制 | -5；付费窗内 → 封顶 92 |
| OPK 同质化 | 通关方式高度同质（同武器/特效/景别/结算） | -3，联动 VIS/L4-A |
| ARG-1 截屏风险 | 单句/单镜头截取即擦边/敏感 | 强制 Revise + 给替代句/镜头 |
| ARG-2 高敏组合 | 平台高敏镜头组合 | -3 + 投放安全版任务单 |
| PCG-1 文本工艺 | 前三集错字/口语污染/跳切糙感 | 降档 1 级或 -5 |
| PCG-2 镜头可执行 | 连续不可画/不可演/不可剪段落 | -3 + 可镜头化改写方案 |
| RCC 规则一致性 | 15s 复述不一致/90s 因果不闭环/系统四要素缺失 | -5 或 Verdict 上限 Revise |

## 3. 计分与等级

### 权重表（先路由后打分）

- Type B：`W = SPS*0.30 + CAP*0.25 + B3*0.20 + APM*0.15 + VIS*0.10`
- Type A：`W = SPS*0.20 + CAP*0.10 + B3*0.10 + APM*0.25 + VIS*0.35`
- Type D：`W = SPS*0.15 + CAP*0.10 + B3*0.10 + APM*0.20 + VIS*0.10 + IV*0.35`
- Type C：兼容五维量表（SPS/CAP/B+3/APM/VIS）

### 扣罚/封顶伪代码（关键项）

```
FinalScore = W
FinalScore -= OOC_Rate_Percent * 2
IF Type B AND UI_Mask_Per_Ep>=2: FinalScore -= 10
IF DW90_answer_15s==FAIL: FinalScore -= 5
IF DW90_delivery_90s==FAIL: FinalScore -= 10
IF U1==FAIL: FinalScore -= 5   # 等价"15s答题不可复述"
IF U2==FAIL: FinalScore -= 10  # 等价"90s交付不可复述"
IF U3_high_cost>=2: FinalScore -= 6
IF B3 < 80: FinalScore = MIN(FinalScore, 85)
IF SPS_Score_0_10 < 6: FinalScore = MIN(FinalScore, 84)
IF UntracedAsset_Consecutive>=2: FinalScore = MIN(FinalScore, 92)
IF OPK_repeat: FinalScore -= 5; IF 付费窗: FinalScore = MIN(FinalScore, 92)
IF ACF < 60: FinalScore = MIN(FinalScore, 84)
IF ACF 60–74: FinalScore = MIN(FinalScore, 92)
IF L_level==RED: FinalScore = MIN(FinalScore, 84)
IF L_level==YELLOW: FinalScore = MIN(FinalScore, 92)
# 叠加防骗层扣分（U7/U2A/RCC-M -= 5，CFS/RRL -= 3）+ 各 Hard Gate 扣罚
```

### 等级裁定

- S：≥93；A：85–92；B：75–84；C/Reject：<75 或命中 Hard Gates。

### 二维结论（P-Score / R-Score）

- **P-Score（潜力）**：核爆潜力、题材匹配、爽点质量（含 SGM）、风格与题材适配度。
- **R-Score（可修复成本）**：合规降噪成本、系统重写成本、前三集工艺返工成本、视觉同构返工成本、风格调整成本。
- 推荐决策：P高+R低 → 立项（Pass）；P高+R高 → 修改后立项（Revise）；P低+R高 → 不推荐（Reject）；P低+R低 → 备选。

## 4. 评审输出模板

```
【评审报告】
〇、风格：主风格=______（风格达标：达标/未达标｜越界：Y/N）
一、维度分：SPS=__ / CAP=__ / B+3=__ / APM=__ / VIS=__（Type D 加 IV=__）【每维附 ≥3 条证据：坐标+摘要+标签】
二、合规输出：compliance_profile=CN/Overseas；C_score_level=C0/C1/C2；risk_tags=[...]；evidence=[...]
三、计分：W=__ → 扣罚明细（逐条：原因+分值+坐标）→ FinalScore=__
四、等级：S/A/B/C（附档位依据）
五、推荐载体：Type A/B/C/D + 路由理由 + 推荐导演风格
六、强制字段：DW90_answer_15s / DW90_delivery_90s(R/P) / CFS_jumps / source_trace / OPK_check / U1–U5 / ProcessDump_Count / L_level+L_triggers / SGM 三标签+坐标+一句话 / (Type B) CAP_CL+JobGrounding+PSD / (悬疑) L6 / (Seed) RedTeam_Issues+Radar_Hits / 导演维度：PCG-2+落锤可见+竖屏+静默+肢体分级
七、SRO 改稿任务单：
  Must Fix（必须改）：
    1）______（绑定落锤/变量/证据坐标）
    2）______
    3）______
  Should Fix（建议改）：
    1）______（含风格调整项）
    2）______
    3）______
```

## 5. 复评与质检

- 双评审独立打分（Seed 强制）；总分差 >8 或任一维差 >15 → 第三人复评。
- 第三人只允许核查：①证据坐标是否成立 ②K/Cap/Deduction 是否按规则执行。
- **分歧归因字典**：D1 证据分歧 / D2 阈值分歧 / D3 风控分歧 / D4 审美分歧——审美分歧（含风格喜好）不得决定 Pass/Reject，只能进改稿建议。

## 6. AI 评审信号路由（人机共驾时）

- AI 只输出三路可审计信号：SPS_Signal（Hit_Exist/Hit_Type/Result_Sentence/Evidence_Coords/Conf）、DW90_Signal（Result_Sentence/Evidence_Coords/Conf）、ProcessDump_Signal（Dump_Exist/Count/Conf，No 时坐标可空）。
- `Conf_Min = min(Conf_SPSHit, Conf_DW90_ResultSentence, Conf_ProcessDump)`；≥90 → AutoPass（仅免人工抽检）；70–89 → Suspect（只查短板信号）；<70 或证据不齐 → Abstain（人类完整裁决）。
- **规则引擎不可跳过**：无论 Router_Status 如何，Hard Gates/ACF/Revise_Feasibility 必须执行，合成最终 Decision。
- **反作弊 Overconfidence Strike**：仅客观事实错误（坐标不存在/无中生有/计数错误）记 Strike；3 次后置信度上限 89%。
