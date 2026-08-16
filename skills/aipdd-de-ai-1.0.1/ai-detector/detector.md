---
name: ai-detector
version: 1.0.0
description: Detect AI-generated content in Chinese text and score the AI content ratio with a detailed risk report. Use when the user asks to check AI content, AI detection, AI score, AI ratio, or whether text was written by AI.
description_zh: 检测文本的 AI 含量，输出 AI 百分比评分与各维度风险明细报告，用于识别 AI 生成内容
user-invocable: true
argument-hint: 待检测的文本内容
---
> **EN:** Sub-skill ai-detector: detects AI-generated content in Chinese text and scores the AI-content ratio with a detailed risk report.
>

# AI 含量检测

## 任务

对用户提供的文本进行 AI 生成痕迹检测，输出**量化评分**与**明细报告**。

## 工作流程

1. **读取输入**：获取待检测文本。若用户同时提供多个片段，逐段检测后汇总。
2. **逐维度分析**：按 [detection-rules.md](references/detection-rules.md) 中六个维度逐项检查：
   - 结构模板化
   - 语言模式与词汇
   - 句式与表达
   - 内容熵值波动
   - 情感与主观性
   - 违禁特征（禁用词与格式）
3. **打分**：每个维度 0-100 分，按规则中的权重加权，得到 AI 含量百分比。
4. **定位证据**：每条风险点必须引用原文片段作为证据，说明原因。
5. **输出报告**：按下方模板输出，不得省略任何部分。

## 评分等级

| AI 含量 | 等级 | 结论 |
|---------|------|------|
| 0-20% | 人类写作 | 基本无 AI 痕迹 |
| 20-40% | 轻微 AI 痕迹 | 少量模板化表达 |
| 40-60% | 明显 AI 痕迹 | 存在明显 AI 写作模式 |
| 60-80% | 高度 AI 生成 | 大量 AI 特征，需改写 |
| 80-100% | 疑似完全 AI 生成 | 高度怀疑由 AI 直接生成 |

## 输出报告模板

```markdown
## AI 含量检测报告

### 总评分
- **AI 含量**：XX%（等级：XXX）
- **结论**：一句话总结

### 各维度得分
| 维度 | 得分 | 权重 | 加权分 |
|------|------|------|--------|
| 结构模板化 | XX | 20% | XX |
| 语言模式与词汇 | XX | 25% | XX |
| 句式与表达 | XX | 15% | XX |
| 内容熵值波动 | XX | 15% | XX |
| 情感与主观性 | XX | 15% | XX |
| 违禁特征 | XX | 10% | XX |

### 风险点明细
1. **位置**：引用原文片段（不超过 50 字）
   - **维度**：XXX
   - **问题**：为什么像 AI
   - **修改建议**：如何改得像真人

### 总体修改建议
- 按严重程度列出改写优先级
```

## 评分原则

- **宁严勿松**：检测到特征即计入，AI 含量评分反映最坏情况
- **证据优先**：每个维度得分必须至少有 1 条原文证据支撑，无证据则给 0 分
- **区分意图**：AI 生成的内容即使语法完全正确也要按特征扣分，真人写作允许少量不规范

## 附加说明

- 检测对象为中文文本为主；若混有英文，英文部分按同样规则评估
- 检测完成后，若用户需要改写，可推荐使用 ai-humanizer 模块（见 ../ai-humanizer/humanizer.md）
- 详细特征清单与示例见 [detection-rules.md](references/detection-rules.md)
