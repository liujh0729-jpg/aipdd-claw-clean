#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run(cmd, *, check=True):
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(str(x) for x in cmd)
            + "\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    return result


def find_tool(name):
    found = shutil.which(name)
    if found:
        return found
    fallback = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin" / name
    if fallback.exists():
        return str(fallback)
    return None


def find_workspace(input_path):
    for candidate in [input_path.parent, *input_path.parents]:
        if (candidate / ".agent" / "skills").exists() or (candidate / "AGENTS.md").exists():
            return candidate
    return Path.cwd()


def test_docx(docx_path):
    with zipfile.ZipFile(docx_path) as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"Invalid docx entry: {bad}")
        media_count = sum(1 for name in zf.namelist() if name.startswith("word/media/"))
    return media_count


def extract_text(pandoc, docx_path):
    result = run([pandoc, str(docx_path), "-t", "plain"], check=False)
    if result.returncode != 0:
        return "", result.stderr.strip()
    return result.stdout, ""


def render_to_pdf(soffice, input_path, outdir, profile_suffix):
    outdir.mkdir(parents=True, exist_ok=True)
    profile = f"file:///tmp/lo_profile_md_to_word_{profile_suffix}_{os.getpid()}"
    run(
        [
            soffice,
            f"-env:UserInstallation={profile}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(input_path),
        ]
    )
    pdf_path = outdir / f"{input_path.stem}.pdf"
    return pdf_path if pdf_path.exists() else None


def pdf_page_count(pdfinfo, pdf_path):
    if not pdfinfo or not pdf_path or not pdf_path.exists():
        return None
    result = run([pdfinfo, str(pdf_path)], check=False)
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    return None


def make_contact_sheet(pdftoppm, magick, pdf_path, render_dir):
    if not (pdftoppm and magick and pdf_path and pdf_path.exists()):
        return None
    page_prefix = render_dir / "page"
    run([pdftoppm, "-png", "-r", "110", str(pdf_path), str(page_prefix)], check=False)
    pages = sorted(render_dir.glob("page-*.png"))
    if not pages:
        return None
    contact_sheet = render_dir / "contact-sheet.png"
    font = "/System/Library/Fonts/Supplemental/Arial.ttf"
    cmd = [
        magick,
        "montage",
        *[str(p) for p in pages],
        "-thumbnail",
        "260x336",
        "-tile",
        "4x",
        "-geometry",
        "+8+8",
        "-background",
        "white",
        str(contact_sheet),
    ]
    if Path(font).exists():
        cmd.insert(2, "-font")
        cmd.insert(3, font)
    result = run(cmd, check=False)
    if result.returncode == 0 and contact_sheet.exists():
        return contact_sheet
    return None


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Word documents.")
    parser.add_argument("input", help="Path to a Markdown file")
    parser.add_argument("--outdir", help="Output directory, default: <workspace>/output/doc")
    parser.add_argument("--no-doc", action="store_true", help="Only create .docx")
    parser.add_argument("--keep-render", action="store_true", help="Keep rendered PDF/PNG checks")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")
    if input_path.suffix.lower() != ".md":
        raise SystemExit(f"Input file must be .md: {input_path}")

    workspace = find_workspace(input_path)
    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else workspace / "output" / "doc"
    outdir.mkdir(parents=True, exist_ok=True)

    pandoc = find_tool("pandoc")
    soffice = find_tool("soffice") or find_tool("libreoffice")
    pdfinfo = find_tool("pdfinfo")
    pdftoppm = find_tool("pdftoppm")
    magick = find_tool("magick")
    if not pandoc:
        raise SystemExit("pandoc is required but was not found")

    docx_path = outdir / f"{input_path.stem}.docx"
    doc_path = outdir / f"{input_path.stem}.doc"

    render_root = workspace / "tmp" / "docs" / f"md-to-word-{input_path.stem}"
    if render_root.exists():
        shutil.rmtree(render_root)
    render_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        lua_filter = Path(tmp) / "remove-empty-images.lua"
        lua_filter.write_text('function Image(img)\n  if img.src == "" then return {} end\nend\n', encoding="utf-8")
        resource_path = os.pathsep.join([str(input_path.parent), str(workspace)])
        run(
            [
                pandoc,
                str(input_path),
                "--from",
                "markdown+yaml_metadata_block+lists_without_preceding_blankline",
                "--to",
                "docx",
                "--standalone",
                f"--resource-path={resource_path}",
                f"--lua-filter={lua_filter}",
                "--output",
                str(docx_path),
            ]
        )

    media_count = test_docx(docx_path)
    text, text_error = extract_text(pandoc, docx_path)

    made_doc = False
    if not args.no_doc and soffice:
        run(
            [
                soffice,
                f"-env:UserInstallation=file:///tmp/lo_profile_md_to_word_doc_{os.getpid()}",
                "--headless",
                "--convert-to",
                "doc",
                "--outdir",
                str(outdir),
                str(docx_path),
            ]
        )
        made_doc = doc_path.exists()

    docx_render_dir = render_root / "docx"
    doc_render_dir = render_root / "doc"
    docx_pdf = render_to_pdf(soffice, docx_path, docx_render_dir, "docx") if soffice else None
    doc_pdf = render_to_pdf(soffice, doc_path, doc_render_dir, "doc") if made_doc and soffice else None
    docx_contact_sheet = make_contact_sheet(pdftoppm, magick, docx_pdf, docx_render_dir) if args.keep_render else None

    summary = {
        "input": str(input_path),
        "output_docx": str(docx_path),
        "output_doc": str(doc_path) if made_doc else None,
        "docx_valid": True,
        "media_count": media_count,
        "text_characters": len(text),
        "text_error": text_error or None,
        "contains_upload_placeholder": "Uploading file" in text,
        "rendered_docx": bool(docx_pdf and docx_pdf.exists()),
        "rendered_doc": bool(doc_pdf and doc_pdf.exists()) if made_doc else None,
        "docx_pages": pdf_page_count(pdfinfo, docx_pdf),
        "doc_pages": pdf_page_count(pdfinfo, doc_pdf) if made_doc else None,
        "contact_sheet": str(docx_contact_sheet) if docx_contact_sheet else None,
    }

    if not args.keep_render:
        shutil.rmtree(render_root, ignore_errors=True)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["contains_upload_placeholder"]:
        raise SystemExit("Upload placeholder leaked into output")
    if not summary["rendered_docx"]:
        raise SystemExit("DOCX render check failed")
    if made_doc and not summary["rendered_doc"]:
        raise SystemExit("DOC render check failed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise
