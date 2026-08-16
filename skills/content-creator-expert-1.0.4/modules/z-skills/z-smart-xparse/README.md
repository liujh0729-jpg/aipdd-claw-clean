# z-smart-xparse

> An AI Agent skill for smart document parsing with automatic PDF splitting and merging.

## What This Skill Does

`z-smart-xparse` wraps the `xparse-cli` tool and adds **intelligent PDF auto-split and merge** logic on top:

| File Type | Behavior |
|-----------|----------|
| **PDF** (≤ 5 MB AND ≤ 100 pages) | Parse directly, no splitting |
| **PDF** (> 5 MB OR > 100 pages) | Auto-split → parse each chunk → merge into one result |
| **Images / Office / HTML / OFD / etc.** | Parse directly, same as standard xparse-parse |

### Why Split?

The xparse API has per-request limits:
- Free API: ≤ 10 MB and ≤ 50 pages per request
- Paid API: ≤ 500 MB and ≤ 1000 pages per request

A 200-page or 20 MB PDF will fail on the free tier. This skill detects that condition **before** calling the API, splits the file into safe chunks, parses them sequentially, and stitches the results back together — all transparently to the user.

---

## Installation

### For Qoder / Claude Code / Cursor / Gemini CLI / other supported agents

```bash
npx skills add /path/to/z-smart-xparse --yes
```

Or copy the `z-smart-xparse/` folder into your project's skills directory:

```
<project>/.agents/skills/z-smart-xparse/
├── MODULE.md                         # Main skill instructions (agent reads this)
└── references/
    ├── api-reference.md             # API parameters, response fields, error codes
    ├── cli-guidance.md              # CLI commands, paid API, output views
    ├── error-handling.md            # Error decision matrix, retry policy
    └── textin-key-setup.md          # Paid API credential setup
```

### Prerequisites

| Dependency | Required For | Install |
|------------|--------------|---------|
| `xparse-cli` | All parsing | `source <(curl -fsSL https://dllf.intsig.net/download/2026/Solution/xparse-cli/install.sh)` |
| `qpdf` | PDF splitting (preferred) | `brew install qpdf` (macOS) / `apt install qpdf` (Linux) |
| `pypdf` (Python) | PDF splitting (fallback) | `pip install pypdf` |

> `qpdf` or `pypdf` is only needed when the agent encounters a large PDF. Small PDFs and non-PDF files work without them.

---

## How It Works (Agent Decision Flow)

```
User provides a document
│
├─ Is it a PDF?
│   │
│   ├─ NO → xparse-cli parse <FILE> → return result
│   │
│   └─ YES → Check file size and page count
│       │
│       ├─ ≤ 5 MB AND ≤ 100 pages
│       │   └─ xparse-cli parse <FILE> → return result
│       │
│       └─ > 5 MB OR > 100 pages
│           │
│           ├─ 1. Split PDF into chunks (50 pages each, via qpdf or pypdf)
│           ├─ 2. Parse each chunk: xparse-cli parse chunk_N.pdf --output chunk_N.md
│           ├─ 3. Merge: cat chunk_*.md > merged_output.md
│           ├─ 4. Cleanup temp files
│           └─ 5. Return merged result
│
└─ Done
```

---

## Usage Examples

### Example 1: Small PDF (no splitting)

```bash
# Agent detects: 2 MB, 30 pages → parse directly
xparse-cli parse report.pdf
```

### Example 2: Large PDF (auto-split triggered)

```bash
# Agent detects: 15 MB, 200 pages → needs splitting

# Step 1: Split with qpdf
mkdir -p /tmp/xparse-chunks
qpdf report.pdf --pages . 1-50    -- /tmp/xparse-chunks/chunk_001.pdf
qpdf report.pdf --pages . 51-100  -- /tmp/xparse-chunks/chunk_002.pdf
qpdf report.pdf --pages . 101-150 -- /tmp/xparse-chunks/chunk_003.pdf
qpdf report.pdf --pages . 151-200 -- /tmp/xparse-chunks/chunk_004.pdf

# Step 2: Parse each chunk
xparse-cli parse /tmp/xparse-chunks/chunk_001.pdf --output /tmp/xparse-chunks/chunk_001.md
xparse-cli parse /tmp/xparse-chunks/chunk_002.pdf --output /tmp/xparse-chunks/chunk_002.md
xparse-cli parse /tmp/xparse-chunks/chunk_003.pdf --output /tmp/xparse-chunks/chunk_003.md
xparse-cli parse /tmp/xparse-chunks/chunk_004.pdf --output /tmp/xparse-chunks/chunk_004.md

# Step 3: Merge
cat /tmp/xparse-chunks/chunk_*.md > /tmp/xparse-chunks/merged_output.md

# Step 4: Cleanup
rm -rf /tmp/xparse-chunks
```

### Example 3: Non-PDF file (no splitting)

```bash
# Office doc, image, HTML, etc. → parse directly
xparse-cli parse presentation.pptx
xparse-cli parse photo.jpg
```

---

## Chunk Sizing Strategy

| API Tier | Chunk Size | Rationale |
|----------|------------|-----------|
| Free API | 50 pages | Matches the free tier per-request limit |
| Paid API | 200 pages (configurable) | Larger chunks reduce API call overhead |
| Size-based (>5 MB, ≤100 pages) | ~4 MB per chunk | Ensures each chunk stays under the 10 MB free limit |

---

## Error Handling

| Error | Agent Action |
|-------|--------------|
| qpdf / pypdf not installed | Install one before proceeding with large PDFs |
| Chunk parse fails (transient) | Retry that chunk once |
| Chunk parse fails (permanent) | Stop, report which chunk failed, ask user |
| Free API limit hit (40307) | Stop, suggest configuring paid API credentials |
| File too large for free tier (40302) | Already handled by auto-split; if still failing, check credentials |
| Merge garbled | Inspect individual chunk outputs to find the problematic one |

Full error code reference: see `references/error-handling.md` and `references/api-reference.md`.

---

## Directory Structure

```
z-smart-xparse/
├── MODULE.md                        # Main skill instructions (agent entry point)
├── README.md                       # This file
└── references/
    ├── api-reference.md            # xparse-cli parameters, JSON response, error codes
    ├── cli-guidance.md             # CLI commands, paid API setup, output views
    ├── error-handling.md           # Decision matrix, retry policy, recovery scenarios
    └── textin-key-setup.md         # TextIn API credential configuration
```

---

## Differences from xparse-parse

| Feature | xparse-parse | z-smart-xparse |
|---------|-------------|----------------|
| Non-PDF parsing | Standard | Identical |
| Small PDF parsing | Standard | Identical |
| Large PDF (>5 MB) | Fails or requires manual `--page-range` | **Auto-split + merge** |
| Long PDF (>100 pages) | Fails or requires manual `--page-range` | **Auto-split + merge** |
| Splitting dependencies | None | qpdf or pypdf (optional, only for large PDFs) |
| Merge logic | N/A | Markdown concatenation or JSON element merging |

---

## License

This skill wraps the [xparse-cli](https://docs.textin.com/xparse/v1/) tool by TextIn / IntSig.
