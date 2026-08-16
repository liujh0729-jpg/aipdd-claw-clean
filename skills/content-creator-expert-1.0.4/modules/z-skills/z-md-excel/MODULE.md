---
name: z-md-excel
description: "Extract all Markdown tables from a .md file and export to Excel (.xlsx). Use this skill when the user wants to: convert Markdown tables to Excel, extract tables from .md files, export MD table data to spreadsheet, batch convert multiple tables from one Markdown file. Supports multiple tables, GFM alignment markers, inline Markdown stripping. Each table becomes a separate sheet in the output Excel file."
---
> **EN:** Extract Markdown tables from .md files and export to Excel (.xlsx).
>

# z-md-excel

Extract all Markdown tables from a `.md` file and save them to a formatted Excel `.xlsx` file.

## When to Use

Trigger this skill when the user asks to:
- Convert/extract Markdown tables to Excel
- Export tables from a `.md` file to `.xlsx`
- Batch extract multiple tables from one Markdown file
- Parse Markdown table data into a spreadsheet

## Requirements

- **Python 3.7+**
- **openpyxl**: `pip install openpyxl`

## Usage

### Command Line

```bash
# Basic usage (output defaults to <input_name>.xlsx)
python scripts/md2xlsx.py input.md

# Specify output file
python scripts/md2xlsx.py input.md output.xlsx
```

### As Agent (recommended workflow)

1. **Identify the Markdown file** the user wants to extract tables from.
2. **Ensure openpyxl is installed**: `pip install openpyxl`
3. **Run the script**:
   ```bash
   python /path/to/z-md-excel/scripts/md2xlsx.py <input.md> [output.xlsx]
   ```
4. **Report results**: The script prints the number of tables found and their dimensions.

### Programmatic (inline Python)

```python
import sys
sys.path.insert(0, '/path/to/z-md-excel/scripts')
from md2xlsx import extract_tables, write_xlsx

tables = extract_tables('input.md')
write_xlsx(tables, 'output.xlsx')
```

## Output Format

- Each table becomes a **separate sheet** named `Table_1`, `Table_2`, etc.
- **Header row**: Bold white text on blue background, centered
- **Data rows**: Regular font, auto-fitted column widths
- **Alignment**: Preserved from Markdown GFM markers (`:---` left, `:---:` center, `---:` right)
- **Frozen pane**: Top row frozen for easy scrolling
- **Inline Markdown stripped**: Bold, italic, code, links, images are converted to plain text

## How It Works

1. Reads the Markdown file line by line
2. Detects table blocks (consecutive lines containing `|`)
3. Skips lines inside code blocks (``` fenced blocks)
4. Requires a GFM separator row (`|---|---|`) to validate a table
5. Strips inline Markdown formatting from cell content
6. Writes all tables to a single Excel file

## Limitations

- Only supports GFM-style pipe tables (`| col1 | col2 |`)
- Does not support HTML `<table>` elements
- Does not preserve complex Markdown formatting (converts to plain text)
- Nested tables are not supported

## File Structure

```
z-md-excel/
├── MODULE.md          # This file (Agent instructions)
├── README.md         # Human-readable documentation
└── scripts/
    └── md2xlsx.py    # Core extraction script
```
