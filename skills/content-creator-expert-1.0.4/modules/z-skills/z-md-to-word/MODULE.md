---
name: z-md-to-word
description: "Convert local Markdown files into Word documents. Use this skill whenever the user provides a .md path and says 转成doc, 转成 Word, Markdown 转 Word, Markdown转doc, md 转 doc, md转docx, 导出 Word, 生成 doc, 生成 docx, or asks for a Word version of an article. This skill should produce a .docx by default, also produce a legacy .doc when useful, embed valid images, skip empty upload placeholders, keep Markdown lists readable, write outputs under output/doc, and verify the generated files before reporting."
---
> **EN:** Markdown → Word document conversion.
>

# Markdown to Word

## Use This For

- A local `.md` article needs to become a Word file.
- The user says "转成doc", "转成 Word", "md 转 doc", "Markdown 转 Word", "导出 Word", or similar.
- The input is usually an Obsidian or WeChat article with YAML frontmatter and remote images.

## Completion Standard

Finish only after all of these are true:

- The `.docx` file exists under `output/doc/`.
- If the user asked for `.doc`, a legacy `.doc` file also exists.
- The document can be opened or rendered by LibreOffice.
- The extracted text includes representative beginning, middle, and ending content.
- Valid images are embedded; empty upload placeholders like `![]( )` or `![Uploading file...]()` are skipped.
- Markdown lists are readable as lists, even when the source omitted a blank line before `-`.

## Preferred Command

From the workspace root:

```bash
python3 .agent/skills/z-md-to-word/scripts/md_to_word.py "/absolute/path/to/article.md"
```

The script writes outputs to:

```text
output/doc/<markdown-stem>.docx
output/doc/<markdown-stem>.doc
```

Use `--no-doc` only when the user explicitly wants `.docx` only.

## Workflow

1. Confirm the Markdown file exists.
2. Run the bundled script.
3. Read the JSON summary printed by the script.
4. If `rendered_docx` or `rendered_doc` is false, fix the cause and rerun.
5. If layout quality matters, rerun with `--keep-render`, open the generated contact sheet, and inspect the pages.
6. Report only the final file paths and the verification result.

## Details Captured By The Script

- Uses Pandoc with `markdown+yaml_metadata_block+lists_without_preceding_blankline`.
- Preserves frontmatter title, author, and date as Word document metadata/title block.
- Removes empty image nodes before conversion, so upload placeholders do not appear in the final document.
- Embeds valid local or remote images into the `.docx`.
- Converts `.docx` to `.doc` through LibreOffice when available.
- Validates the `.docx` ZIP structure.
- Extracts plain text for a content sanity check.
- Renders Word files to PDF when LibreOffice is available.

## Fallback

If the script cannot run, use this direct conversion pattern:

```bash
pandoc "input.md" \
  --from markdown+yaml_metadata_block+lists_without_preceding_blankline \
  --to docx \
  --standalone \
  --resource-path="/path/to/input-dir:/workspace/root" \
  --lua-filter="/tmp/remove-empty-images.lua" \
  --output "output/doc/name.docx"
```

`/tmp/remove-empty-images.lua`:

```lua
function Image(img)
  if img.src == "" then return {} end
end
```

Then render and inspect:

```bash
soffice -env:UserInstallation=file:///tmp/lo_profile_$$ \
  --headless --convert-to pdf --outdir tmp/docs/check "output/doc/name.docx"
```
