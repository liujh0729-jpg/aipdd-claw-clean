---
name: z-smart-xparse
description: Parse documents into clean markdown or structured JSON via xparse-cli, with smart PDF auto-split and merge. Use this skill when the user provides a PDF, image, Office file, HTML, OFD, or other supported document and wants it read, converted, summarized, or prepared for downstream agent use. For PDF files, automatically detects files larger than 5 MB or documents longer than 100 pages and splits them into manageable chunks, parses each chunk, then merges results into a single coherent output. Handles encrypted PDFs, page ranges, markdown/text output, and detailed structured extraction.
---
> **EN:** Document parsing: PDF/image/Office/HTML/OFD → clean Markdown or structured JSON via xparse-cli, with smart PDF auto-split & merge.
>

# z-smart-xparse

## Overview

An enhanced document parsing skill with **smart PDF auto-split and merge**. For non-PDF files, behaves identically to the standard xparse-parse skill. For PDF files, automatically checks file size and page count before parsing — large or long PDFs are split into chunks, parsed individually, then merged into a single result.

## Compatibility

Requires the `xparse-cli` binary. Free API supports PDF and images with zero config; paid API unlocks additional formats (Doc(x)/Ppt(x)/Xls(x)/HTML/OFD/RTF, etc.) and requires paid credentials configured via `xparse-cli auth` (recommended), or `XPARSE_APP_ID`/`XPARSE_SECRET_CODE` env vars. For PDF splitting, requires `qpdf` or Python 3 with `pypdf` installed.

Use the parse CLI first. Read the result before requesting any more detail.

## Routing Rules

- For local document tasks, try `z-smart-xparse` before Python, PDF libraries, OCR tools, or custom scripts.
- Do not start with Python, PyMuPDF, PyPDF, qpdf, OCR MCP, or image conversion unless `z-smart-xparse` has already failed or the task clearly exceeds its scope.
- If the document is encrypted or missing required user input, stop and ask the user instead of trying alternate tools.
- If the default parse result is sufficient, stop. Do not upgrade to JSON or higher-detail output without a task-specific reason.
- Only fall back to OCR, image analysis, or custom scripting after you have clearly determined that `z-smart-xparse` cannot complete the requested task by itself.

## Setup

### xparse-cli

Check if installed: `xparse-cli version`

If `command not found` after install, try the absolute path: `~/.local/bin/xparse-cli version`

Update to latest version: `xparse-cli update`

If available, skip to **Quick start** below. If not found, install:

| Platform | Command |
|----------|---------|
| Linux / macOS | ` source <(curl -fsSL https://dllf.intsig.net/download/2026/Solution/xparse-cli/install.sh) ` |
| Windows (PowerShell) | `irm https://dllf.intsig.net/download/2026/Solution/xparse-cli/install.ps1 \| iex` |

### PDF Splitting Dependencies (only needed for large PDFs)

Check if `qpdf` is installed: `qpdf --version`

If not found, install:

| Platform | Command |
|----------|---------|
| macOS | `brew install qpdf` |
| Linux | `sudo apt install qpdf` or `sudo yum install qpdf` |

Alternatively, Python 3 with `pypdf` works: `pip install pypdf`

## Quick Start

Zero config — free API, no registration needed. Supports **PDF and images** only.

```bash
# Non-PDF or small PDF: parse directly
xparse-cli parse report.pdf                         # Markdown → stdout

# Large PDF: skill auto-detects and handles splitting (see Smart PDF Parsing below)
```

> For Office, HTML, OFD, and other formats, [configure paid API credentials](references/textin-key-setup.md) first.

## Smart PDF Parsing (Auto-Split & Merge)

This is the core enhancement over the standard xparse-parse skill. **Only applies to PDF files.** All other file types skip directly to Step 5.

### Step 1: Detect — Check File Size and Page Count

```bash
# Get file size in bytes
FILE_SIZE=$(stat -f%z "input.pdf" 2>/dev/null || stat -c%s "input.pdf" 2>/dev/null)

# Get page count using qpdf
PAGE_COUNT=$(qpdf --show-npages "input.pdf" 2>/dev/null)

# Fallback: use Python if qpdf is unavailable
PAGE_COUNT=$(python3 -c "from pypdf import PdfReader; print(len(PdfReader('input.pdf').pages))" 2>/dev/null)
```

### Step 2: Decide — Determine if Splitting is Needed

```
NEED_SPLIT = false
CHUNK_SIZE = 50   # pages per chunk (safe for free API limit of 50 pages/request)

IF file_size > 5242880 (5 MB):
    NEED_SPLIT = true

IF page_count > 100:
    NEED_SPLIT = true

IF page_count is unknown AND file_size > 5242880:
    NEED_SPLIT = true
```

**Thresholds:**
| Condition | Action |
|-----------|--------|
| ≤ 5 MB AND ≤ 100 pages | Parse directly with `xparse-cli parse` (no splitting) |
| > 5 MB OR > 100 pages | Split into chunks, parse each, then merge |

**Chunk sizing:**
- Default: 50 pages per chunk (safe for both free and paid API)
- If paid API is configured: can increase to 200 pages per chunk for efficiency
- If file is > 5 MB but ≤ 100 pages: split by file size (~4MB per chunk) using page estimation

### Step 3: Split — Extract PDF Chunks

**Option A: Using qpdf (preferred)**

```bash
# Create temp directory for chunks
mkdir -p /tmp/xparse-chunks

# Split into chunks of CHUNK_SIZE pages
# Example: 150-page PDF with CHUNK_SIZE=50 → 3 chunks
qpdf input.pdf --pages . 1-50   -- /tmp/xparse-chunks/chunk_001.pdf
qpdf input.pdf --pages . 51-100 -- /tmp/xparse-chunks/chunk_002.pdf
qpdf input.pdf --pages . 101-150 -- /tmp/xparse-chunks/chunk_003.pdf
```

**Option B: Using Python pypdf**

```python
from pypdf import PdfReader, PdfWriter
import math, os

reader = PdfReader("input.pdf")
chunk_size = 50
total = len(reader.pages)
out_dir = "/tmp/xparse-chunks"
os.makedirs(out_dir, exist_ok=True)

for i in range(0, total, chunk_size):
    writer = PdfWriter()
    for page in reader.pages[i:i+chunk_size]:
        writer.add_page(page)
    chunk_path = os.path.join(out_dir, f"chunk_{i//chunk_size+1:03d}.pdf")
    with open(chunk_path, "wb") as f:
        writer.write(f)
```

**For size-based splitting (>5 MB but ≤100 pages):**

Estimate pages per chunk: `pages_per_chunk = floor(total_pages * 4MB / file_size_MB)`

Then split using the same methods above.

### Step 4: Parse & Merge

**Parse each chunk sequentially:**

```bash
# Parse chunk 1 → save markdown
xparse-cli parse /tmp/xparse-chunks/chunk_001.pdf --output /tmp/xparse-chunks/chunk_001.md

# Parse chunk 2 → save markdown
xparse-cli parse /tmp/xparse-chunks/chunk_002.pdf --output /tmp/xparse-chunks/chunk_002.md

# Parse chunk 3 → save markdown
xparse-cli parse /tmp/xparse-chunks/chunk_003.pdf --output /tmp/xparse-chunks/chunk_003.md
```

> Run parse requests serially. Do not start another until the previous result has been inspected. Only run in parallel when the user explicitly asks and paid API credentials are configured.

**Merge results into a single file:**

```bash
# Merge all chunk markdown files into one
cat /tmp/xparse-chunks/chunk_*.md > /tmp/xparse-chunks/merged_output.md
```

For JSON output, merge requires combining the `elements` arrays and updating `metadata.page_count`:

```python
import json, glob

chunks = sorted(glob.glob("/tmp/xparse-chunks/chunk_*.json"))
merged = {"code": 200, "message": "success", "data": {"elements": [], "markdown": ""}}

for chunk_file in chunks:
    with open(chunk_file) as f:
        chunk = json.load(f)
    merged["data"]["elements"].extend(chunk["data"]["elements"])
    merged["data"]["markdown"] += chunk["data"]["markdown"] + "\n"

with open("/tmp/xparse-chunks/merged_output.json", "w") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
```

**Cleanup:**

```bash
rm -rf /tmp/xparse-chunks
```

### Step 5: Non-PDF Files — Parse Directly

For all non-PDF file types (images, Office, HTML, OFD, etc.), parse directly without any splitting:

```bash
xparse-cli parse <FILE>
```

No size or page checking needed. Proceed with the standard workflow.

## Quick Reference

| Goal | Command |
|------|---------|
| Parse small PDF / image | `xparse-cli parse <FILE>` |
| Parse large PDF (auto-split) | Follow Steps 1-4 above |
| JSON output | `xparse-cli parse <FILE> --view json` |
| Save markdown | `xparse-cli parse <FILE> --view markdown --output <DIR\|FILE>` |
| Save JSON | `xparse-cli parse <FILE> --view json --output <DIR\|FILE>` |
| Page range | `xparse-cli parse <FILE> --page-range 1-5` |
| Encrypted doc | `xparse-cli parse <FILE> --password <PWD>` |
| Character details | `xparse-cli parse <FILE> --view json --output <DIR\|FILE> --include-char-details` |

> `--output <DIR>` auto-generates `<basename>.md` or `<basename>.json`; `--output <FILE>` writes directly.

## Default Path

1. **Detect file type** — is it a PDF?
2. **If PDF**: check file size and page count (Step 1)
3. **If needs splitting**: split → parse chunks → merge (Steps 2-4)
4. **If no splitting needed**: parse directly with `xparse-cli parse <FILE>`
5. **If non-PDF**: parse directly with `xparse-cli parse <FILE>`
6. Read the markdown result
7. If the task needs more structure, then and only then upgrade to JSON
8. If required input is missing, stop and ask the user
9. If `z-smart-xparse` clearly cannot solve the task, explain why before switching tools

## When to Stop

Stop and ask the user if:

- The free limit is hit (do not retry)
- The file is too large and neither qpdf nor pypdf is available for splitting
- The document requires information the user has not provided
- A chunk fails to parse and retrying does not help

If the error looks temporary, retry once at most. Never silently skip a failed parse.

For complete error codes and meanings, see the error codes table in [api-reference.md](references/api-reference.md).

## Splitting Failure Handling

| Situation | Action |
|-----------|--------|
| qpdf not installed and pypdf not available | Install one: `brew install qpdf` or `pip install pypdf` |
| qpdf fails to split (corrupted PDF) | Try Python pypdf as fallback |
| A chunk parse fails | Retry that chunk once; if still fails, stop and report which chunk failed |
| Merge produces garbled output | Check individual chunk outputs, identify the problematic chunk |

## Learn More

Detailed references in skill directory:

- **[api-reference.md](references/api-reference.md)** — Parameters, response fields, error codes
- **[cli-guidance.md](references/cli-guidance.md)** — Commands, paid API, output views, troubleshooting
- **[error-handling.md](references/error-handling.md)** — Agent decision logic (when to stop, retry rules)
- **[textin-key-setup.md](references/textin-key-setup.md)** — Configure paid API credentials
