# z-md-to-word

> 把本地 Markdown 文章转换成 Word 文档，默认生成 `.docx`，同时生成兼容旧版 Word 的 `.doc`。

## 功能

- 支持带 YAML 信息的 Markdown 文章
- 自动保留标题、作者和日期
- 支持远程图片和本地图片写入 Word
- 自动跳过空上传占位符，例如 `![Uploading file...]()`
- 兼容没有空行分隔的 Markdown 列表
- 转换后自动检查文档能否打开和渲染

## 安装

复制到你的本地 skills 目录：

```bash
cp -r z-md-to-word /path/to/your-project/.agent/skills/z-md-to-word
```

可在 `AGENTS.md` 的触发词表中加入：

```markdown
| 转成doc / Markdown转Word / md转doc / 导出Word | `z-md-to-word` |
```

## 使用

在 Agent 中直接说：

- `把 xxx.md 转成doc`
- `这个 Markdown 导出 Word`
- `md 转 docx`

也可以手动运行脚本：

```bash
python3 .agent/skills/z-md-to-word/scripts/md_to_word.py "/absolute/path/to/article.md"
```

输出默认保存在：

```text
output/doc/<原文件名>.docx
output/doc/<原文件名>.doc
```

只生成 `.docx`：

```bash
python3 .agent/skills/z-md-to-word/scripts/md_to_word.py "/absolute/path/to/article.md" --no-doc
```

保留页面缩略图检查结果：

```bash
python3 .agent/skills/z-md-to-word/scripts/md_to_word.py "/absolute/path/to/article.md" --keep-render
```

## 依赖

- Pandoc
- LibreOffice
- Poppler，可选，用于页数和渲染检查
- ImageMagick，可选，用于生成页面缩略图

## 文件结构

```text
z-md-to-word/
├── MODULE.md
├── README.md
├── evals/
│   └── evals.json
└── scripts/
    └── md_to_word.py
```
