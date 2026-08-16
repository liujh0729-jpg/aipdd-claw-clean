---
name: z-docx-format-brush
description: "docx 格式刷：从模板 Word 文档提取格式指纹（字体/字号/行距/缩进/对齐/表格边框/封面/分页），然后统一应用到目标 docx，做到与模板格式完全一致。触发词：格式刷、格式统一、统一格式、套用模板格式、参照模板格式、docx格式修复、Word格式不一致、pandoc转出来的docx格式乱、按模板生成docx、公文格式。凡是'参照某个 docx 模板写/改/修复另一个 docx'的任务都用本 skill，包括新建文档按模板排版、修复其他工具（pandoc/其他模型）产出的格式混乱 docx。"
---
> **EN:** docx format brush: extract a format fingerprint (fonts/sizes/spacing/indents/table borders/cover/page breaks) from a template Word doc and apply it uniformly to target docx files.
>

# docx 格式刷（Format Brush）

把一份模板 docx 的格式"刷"到另一份 docx 上。核心思想：**格式参数从模板实测出来，收敛到唯一出口应用**，凭感觉手调必然不统一。

## 适用场景

1. **修复场景**：已有内容正确但格式混乱的 docx（典型：pandoc / 其他模型转换产出），按模板统一格式
2. **新建场景**：从零生成 docx，要求格式与某模板一致
3. **诊断场景**：只想知道两份 docx 格式差异在哪

## 三步工作流

### 第一步：解剖模板 → 格式指纹

```bash
python3 scripts/extract_fingerprint.py "模板.docx"
```

输出模板的格式指纹（JSON + 可读摘要）：
- 各样式（Normal/Heading 1-3/Body Text）的字体、eastAsia 中文字体、字号、加粗、颜色
- 正文段落实测的行距、首行缩进、对齐分布（取众数为准，样式定义常与实际 run 不符）
- 标题段落实测参数（模板作者往往在 run 层覆盖了样式，必须以 run 实测为准）
- 封面段落结构（前3段的字号/对齐）
- 表格：边框有无、单元格字体字号
- 章节标题是否分页（pageBreakBefore）

**为什么要实测而非只看样式表**：中文公文类 docx 几乎都在 run 层直接设置仿宋等字体，样式表里可能还是默认值。只信样式表必然刷错。

### 第二步：诊断目标文件（修复场景）

```bash
python3 scripts/extract_fingerprint.py "目标.docx"
```

对比两份指纹，列出病灶清单。pandoc 产物的典型病灶：
- 所有 run 字体/字号为 None（裸继承 Body Text/First Paragraph 默认样式 → Calibri/宋体混排）
- 标题带默认主题蓝（0F4761）
- 表格无 tblBorders（无边框）
- 无封面、章节不分页
- 中文引号开闭反向（`"xxx"` 被转成 `”xxx“`）

### 第三步：应用格式刷

```bash
python3 scripts/apply_format.py "目标.docx" --config fingerprint.json [--out "输出.docx"]
```

不带 `--out` 时原地修复。脚本按五层顺序应用（顺序重要，样式层先兜底，run 层再精确覆盖）：

1. **样式层**：Normal/Body Text/First Paragraph/Heading 1-3 全部改为模板字体字号，清除颜色 —— 兜住一切继承
2. **段落层**：正文统一行距/首行缩进；标题清缩进、按指纹设置字号加粗；`第X章` 型 Heading 1 居中 + pageBreakBefore
3. **封面层**：首段含"文件/报告/方案"等关键词时重做三行式封面（公司名/项目名大字号 + 文档类型更大字号，居中加粗）
4. **表格层**：补齐单线 tblBorders、单元格统一字体字号、表头行加粗、行距 1.0、清缩进
5. **文字层**：中文引号按开闭配对重排为 `“xxx”`

## 关键技术要点（写任何 docx 处理代码前必读）

- **中文字体要设两遍**：`run.font.name` 只管西文；必须再 `rPr.rFonts.set(qn('w:eastAsia'), '仿宋')`，否则 Word 中文回落宋体
- **字号换算**：docx 内部是 EMU，`磅 = EMU / 12700`（如 152400 = 12磅，203200 = 16磅）
- **首行缩进2字符** ≈ Emu(304800)（12磅正文）或 Emu(406400)（16磅正文），即 2×字号
- **清颜色**：`r.font.color.rgb = None` 不够，需从 rPr 中 remove `w:color` 元素
- **章节分页**：往 pPr 里插 `w:pageBreakBefore` 元素，优于插入分页符 run
- **新建场景**：先准备结构化内容 JSON，再调用 `scripts/gen_from_template.py`。脚本内的 `title()`、`para()` 和 `table()` 工厂统一应用指纹参数，所有内容只从工厂函数写入。

```bash
python3 scripts/gen_from_template.py "content.json" \
  --config fingerprint.json \
  --out "output/doc/输出.docx"
```

内容 JSON 使用 `cover` 和 `blocks`。`blocks` 支持 `heading`、`paragraph`、`table`、`page_break`；完整示例见脚本顶部说明。

## 验证（必做，做完才算完成）

```bash
python3 scripts/verify_format.py "输出.docx"
```

通过标准：
- run 字体分布收敛到指纹规定的少数几档（如 仿宋12/15/22磅），无 None 无杂色
- 全部表格有 tblBorders
- 所有 `第X章` Heading 1 有 pageBreakBefore
- 抽查含引号段落方向正确

验证输出贴给用户看，用表格汇报"病灶 → 修复"对照。

## 输出约定

- 修复场景默认原地保存，同时按用户此前要求的目录放置副本
- 新建场景输出到 `output/doc/`
- 汇报时列出格式指纹表（元素/参数）让用户可核对
