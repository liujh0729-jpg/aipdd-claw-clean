# Source preparation

Use this guide when a corpus needs conversion or metadata cleanup before retrieval.

## Supported input

The bundled retrieval script reads:

- Markdown: `.md`, `.markdown`
- plain text: `.txt`
- individual files
- directories, recursively

Convert PDF, Word, spreadsheet, image, audio, video, and web content to Markdown or text with an appropriate tool before running retrieval.

For text-based PDFs with Poppler installed, use:

```bash
pdftotext -layout source.pdf extracted.txt

python3 scripts/prepare_pdftotext.py \
  extracted.txt prepared-source.md \
  --title "Source title"
```

Use `--mode numbered` for aphorisms, numbered quotations, or numbered rules. The preparation script converts form-feed page breaks into `## PDF Page N` markers and joins visual line wraps into semantic paragraphs.

Keep converted files beside the originals or in a separate corpus directory. Do not overwrite source files unless the user explicitly asks.

## Preserve verification metadata

Retain metadata that lets another person return to the source:

- original filename
- page number
- section heading
- timestamp
- speaker
- publication or meeting date
- source URL when the local document was captured from the web

## Recognized markers

### Page

```markdown
## PDF Page 12
```

```markdown
<!-- page: 12 -->
```

```markdown
[Page 12]
```

### Timestamp

```markdown
[00:18:42]
```

### Speaker

```markdown
Speaker Name: Complete paragraph
```

```markdown
**Speaker Name:** Complete paragraph
```

### Section

Use normal Markdown headings. The retrieval result keeps the heading path:

```markdown
# Interview
## Product strategy
### Pricing
```

## Paragraph boundaries

Use blank lines between semantic paragraphs. Keep sentences that form one claim, mechanism, or example in the same paragraph.

Avoid hard wrapping every sentence with blank lines. It fragments evidence and weakens neighboring context.

## Corpus boundary

Before retrieval, identify:

- included files
- excluded drafts or obsolete versions
- date range
- whether duplicate exports exist
- whether the sources are authoritative, secondary, or AI-generated transcripts

Record material limitations in the final answer.
