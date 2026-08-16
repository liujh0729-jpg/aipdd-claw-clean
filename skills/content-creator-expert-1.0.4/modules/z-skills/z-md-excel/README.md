# z-md-excel

> 从 Markdown 文件中提取所有表格并导出为 Excel (.xlsx) 文件。

## 功能特点

- **多表格支持** — 自动检测并提取 Markdown 文件中的所有表格
- **独立 Sheet** — 每个表格导出为 Excel 中的一个独立工作表
- **GFM 对齐** — 保留 Markdown 表格的对齐方式（左对齐 / 居中 / 右对齐）
- **格式清理** — 自动去除 Markdown 内联格式（粗体、斜体、代码、链接、图片）
- **代码块安全** — 自动跳过代码块中的管道符，避免误识别
- **专业格式** — 蓝色表头、自适应列宽、冻结首行、细边框

## 安装

### 1. 环境要求

- Python 3.7+
- openpyxl

### 2. 安装依赖

```bash
pip install openpyxl
```

### 3. 安装 Skill

将 `z-md-excel` 目录复制到你的 skills 目录下，例如：

```bash
# 复制到 Obsidian 项目的 skills 目录
cp -r z-md-excel /path/to/your/project/.agent/skills/

# 或复制到全局 skills 目录
cp -r z-md-excel ~/Desktop/z-skills/
```

## 使用方法

### 命令行

```bash
# 基本用法（输出文件默认为 <输入文件名>.xlsx）
python scripts/md2xlsx.py input.md

# 指定输出文件路径
python scripts/md2xlsx.py input.md output.xlsx
```

### 在 AI Agent 中使用

将 `z-md-excel` 放入 skills 目录后，Agent 会自动识别并在需要时调用。

**触发词示例**：
- "把这个 Markdown 里的表格提取到 Excel"
- "导出 md 文件中的所有表格"
- "把 xxx.md 的表格转成 xlsx"

### Python 代码调用

```python
import sys
sys.path.insert(0, '/path/to/z-md-excel/scripts')
from md2xlsx import extract_tables, write_xlsx

# 提取表格
tables = extract_tables('input.md')

# 查看提取结果
for i, t in enumerate(tables):
    print(f"Table {i+1}: {len(t['header'])} columns, {len(t['rows'])} rows")

# 导出到 Excel
write_xlsx(tables, 'output.xlsx')
```

## 示例

### 输入 (README.md)

```markdown
| 类别 | 能力 |
| --- | --- |
| 日历 | 查看、创建和更新日程 |
| 即时通讯 | 发送/回复消息、创建群聊 |

| Skill | 说明 |
| --- | --- |
| lark-shared | 应用配置、认证 |
| lark-calendar | 日历日程管理 |
```

### 输出

```
Found 2 table(s) in 'README.md'.
  Table 1: 2 columns, 2 data rows
  Table 2: 2 columns, 2 data rows
Saved 2 table(s) to: README.xlsx
```

Excel 文件中包含两个 Sheet：`Table_1` 和 `Table_2`。

## 输出格式说明

| 特性 | 说明 |
| --- | --- |
| Sheet 命名 | Table_1, Table_2, ... |
| 表头样式 | 白色粗体 + 蓝色背景 + 居中 |
| 数据行 | 常规字体 + 顶部对齐 + 自动换行 |
| 列宽 | 自适应内容（最小 10，最大 60） |
| 对齐方式 | 保留 Markdown GFM 对齐标记 |
| 冻结窗格 | 首行冻结 |
| 边框 | 浅灰色细边框 |

## 限制

- 仅支持 GFM 管道表格语法（`| col1 | col2 |`）
- 不支持 HTML `<table>` 元素
- 内联 Markdown 格式会被转换为纯文本
- 不支持嵌套表格

## 文件结构

```
z-md-excel/
├── MODULE.md          # Agent 使用指南
├── README.md         # 本文档
└── scripts/
    └── md2xlsx.py    # 核心提取脚本
```

## License

MIT
