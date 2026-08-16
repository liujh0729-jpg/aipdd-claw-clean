#!/usr/bin/env python3
"""Convert pdftotext output into page-marked Markdown for evidence retrieval."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


NUMBERED_ITEM_RE = re.compile(r"^\s*(\d{1,4})\s*[.、]\s*(.*)$")
SECTION_RE = re.compile(r"^【\s*(.+?)\s*】$")
PAGE_NUMBER_RE = re.compile(r"^\d{1,4}$")


def is_cjk(value: str) -> bool:
    return bool(value) and (
        "\u3400" <= value <= "\u4dbf"
        or "\u4e00" <= value <= "\u9fff"
        or "\uf900" <= value <= "\ufaff"
    )


def join_wrapped_lines(lines: list[str]) -> str:
    """Join visual PDF lines while avoiding spaces inside Chinese sentences."""
    cleaned = [re.sub(r"[ \t]+", " ", line.strip()) for line in lines]
    cleaned = [line for line in cleaned if line]
    if not cleaned:
        return ""

    result = cleaned[0]
    no_space_after = set("，。！？；：、）》】”’…—")
    no_space_before = set("，。！？；：、）》】”’…—")
    for line in cleaned[1:]:
        left = result[-1]
        right = line[0]
        if is_cjk(left) or is_cjk(right) or left in no_space_after or right in no_space_before:
            result += line
        else:
            result += " " + line
    return result.strip()


def paragraph_blocks(page_text: str) -> list[str]:
    raw_blocks = re.split(r"\n\s*\n", page_text.strip())
    return [
        paragraph
        for block in raw_blocks
        if (paragraph := join_wrapped_lines(block.splitlines()))
    ]


def numbered_blocks(page_text: str) -> list[str]:
    """Group numbered aphorisms that pdftotext emits as hard-wrapped lines."""
    blocks: list[str] = []
    pending: list[str] = []
    pending_prefix: str | None = None

    def flush() -> None:
        nonlocal pending, pending_prefix
        content = join_wrapped_lines(pending)
        pending = []
        if not content:
            pending_prefix = None
            return
        blocks.append(f"{pending_prefix}{content}" if pending_prefix else content)
        pending_prefix = None

    for raw_line in page_text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line.strip())
        if not line:
            continue

        section = SECTION_RE.match(line)
        if section:
            flush()
            blocks.append(f"### {section.group(1)}")
            continue

        item = NUMBERED_ITEM_RE.match(line)
        if item:
            flush()
            pending_prefix = f"{item.group(1)}. "
            if item.group(2):
                pending.append(item.group(2))
            continue

        if PAGE_NUMBER_RE.fullmatch(line) and not pending:
            continue

        pending.append(line)

    flush()
    return blocks


def convert_text(
    source_text: str,
    *,
    title: str,
    mode: str = "paragraphs",
    start_page: int = 1,
) -> str:
    normalized = source_text.replace("\r\n", "\n").replace("\r", "\n")
    pages = normalized.split("\f")
    renderer = numbered_blocks if mode == "numbered" else paragraph_blocks

    output = [f"# {title}", ""]
    for offset, page_text in enumerate(pages):
        page_number = start_page + offset
        blocks = renderer(page_text)
        if not blocks:
            continue
        output.extend([f"## PDF Page {page_number}", ""])
        for block in blocks:
            output.extend([block, ""])

    return "\n".join(output).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert UTF-8 pdftotext output into page-marked Markdown."
    )
    parser.add_argument("input", type=Path, help="Text file created by pdftotext")
    parser.add_argument("output", type=Path, help="Destination Markdown file")
    parser.add_argument("--title", required=True, help="Top-level Markdown title")
    parser.add_argument(
        "--mode",
        choices=("paragraphs", "numbered"),
        default="paragraphs",
        help="Use numbered for quote or aphorism collections",
    )
    parser.add_argument("--start-page", type=int, default=1)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Input file does not exist: {args.input}")
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {args.output}")

    rendered = convert_text(
        args.input.read_text(encoding="utf-8", errors="replace"),
        title=args.title,
        mode=args.mode,
        start_page=args.start_page,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Prepared {args.output} ({rendered.count('## PDF Page')} pages with text)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
