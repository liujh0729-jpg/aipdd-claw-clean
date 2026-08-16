#!/usr/bin/env python3
"""Retrieve ranked, paragraph-level evidence from arbitrary Markdown/text sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt"}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PAGE_PATTERNS = (
    re.compile(r"^#{1,6}\s+PDF\s+Page\s+(\d+)\s*$", re.I),
    re.compile(r"^<!--\s*page\s*:\s*(\d+)\s*-->\s*$", re.I),
    re.compile(r"^\[Page\s+(\d+)\]\s*$", re.I),
)
TIMESTAMP_RE = re.compile(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*$")
SPEAKER_RE = re.compile(
    r"^(?:\*\*)?([^:\n]{1,40}?)(?:\*\*)?\s*[:：]\s+(.+)$"
)


@dataclass(frozen=True)
class SourceFile:
    path: Path
    document: str


@dataclass(frozen=True)
class Location:
    document: str
    line_start: int
    line_end: int
    page: int | None
    timestamp: str | None
    section: str
    speaker: str | None


@dataclass
class Block:
    block_id: str
    location: Location
    content: str
    index: int
    document_index: int


@dataclass
class Evidence:
    evidence_id: str
    score: int
    matched_terms: list[str]
    content: str
    location: Location
    additional_locations: list[Location]
    block_ids: list[str]
    previous_context: str
    next_context: str
    content_hash: str
    index: int
    document_index: int

    def public_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload.pop("index", None)
        payload.pop("document_index", None)
        return payload


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalized_hash(value: str) -> str:
    compact = re.sub(r"\W+", "", value, flags=re.UNICODE).lower()
    return hashlib.sha1(compact.encode("utf-8")).hexdigest()[:12]


def display_path(path: Path, root: Path) -> str:
    if root.is_dir():
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            pass
    return path.name


def discover_sources(inputs: Iterable[Path]) -> tuple[list[SourceFile], list[str]]:
    files: list[SourceFile] = []
    warnings: list[str] = []
    seen: set[Path] = set()

    for raw_path in inputs:
        root = raw_path.expanduser().resolve()
        if not root.exists():
            warnings.append(f"Source path does not exist: {raw_path}")
            continue
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for candidate in candidates:
            if not candidate.is_file():
                continue
            if candidate.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(
                SourceFile(
                    path=resolved,
                    document=display_path(resolved, root),
                )
            )

    files.sort(key=lambda item: (item.document.lower(), str(item.path)))
    if not files:
        warnings.append("No supported Markdown or text files were discovered.")
    return files, warnings


def page_marker(value: str) -> int | None:
    for pattern in PAGE_PATTERNS:
        match = pattern.match(value)
        if match:
            return int(match.group(1))
    return None


def split_speaker(content: str) -> tuple[str | None, str]:
    match = SPEAKER_RE.match(content)
    if not match:
        return None, content
    label = normalize_text(match.group(1).strip("*"))
    body = normalize_text(match.group(2))
    if not label or "://" in label or len(label.split()) > 6:
        return None, content
    return label, body


def parse_source(source: SourceFile, document_index: int) -> list[Block]:
    lines = source.path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks: list[Block] = []
    section_levels: dict[int, str] = {}
    page: int | None = None
    timestamp: str | None = None
    paragraph: list[str] = []
    line_start = 0
    in_frontmatter = bool(lines and lines[0].strip() == "---")

    def current_section() -> str:
        return " / ".join(
            section_levels[level] for level in sorted(section_levels)
        )

    def flush(line_end: int) -> None:
        nonlocal paragraph, line_start
        content = normalize_text(" ".join(paragraph))
        paragraph = []
        if not content:
            return
        speaker, body = split_speaker(content)
        block_number = len(blocks) + 1
        blocks.append(
            Block(
                block_id=f"d{document_index + 1:03d}-b{block_number:04d}",
                location=Location(
                    document=source.document,
                    line_start=line_start,
                    line_end=max(line_start, line_end),
                    page=page,
                    timestamp=timestamp,
                    section=current_section(),
                    speaker=speaker,
                ),
                content=body,
                index=-1,
                document_index=document_index,
            )
        )

    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if in_frontmatter:
            if line_number > 1 and stripped == "---":
                in_frontmatter = False
            continue

        marker = page_marker(stripped)
        if marker is not None:
            flush(line_number - 1)
            page = marker
            continue

        heading = HEADING_RE.match(stripped)
        if heading:
            flush(line_number - 1)
            level = len(heading.group(1))
            title = normalize_text(heading.group(2))
            for existing_level in list(section_levels):
                if existing_level >= level:
                    section_levels.pop(existing_level)
            section_levels[level] = title
            continue

        timestamp_match = TIMESTAMP_RE.match(stripped)
        if timestamp_match:
            flush(line_number - 1)
            timestamp = timestamp_match.group(1)
            continue

        if not stripped:
            flush(line_number - 1)
            continue

        if not paragraph:
            line_start = line_number
        paragraph.append(stripped)

    flush(len(lines))
    return blocks


def load_blocks(files: list[SourceFile]) -> list[Block]:
    blocks: list[Block] = []
    for document_index, source in enumerate(files):
        document_blocks = parse_source(source, document_index)
        for block in document_blocks:
            block.index = len(blocks)
            blocks.append(block)
    return blocks


def compile_patterns(
    queries: Iterable[str], regex: bool
) -> list[tuple[str, re.Pattern[str]]]:
    patterns: list[tuple[str, re.Pattern[str]]] = []
    seen: set[str] = set()
    for raw_query in queries:
        query = normalize_text(raw_query)
        key = query.lower()
        if not query or key in seen:
            continue
        seen.add(key)
        expression = query if regex else re.escape(query)
        patterns.append((query, re.compile(expression, re.I)))
    return patterns


def score_block(
    block: Block,
    patterns: list[tuple[str, re.Pattern[str]]],
) -> tuple[int, list[str]]:
    score = 0
    matches: list[str] = []
    section = block.location.section

    for term, pattern in patterns:
        occurrences = len(pattern.findall(block.content))
        if occurrences:
            matches.append(term)
            score += 4 + min(occurrences, 3)
            if len(term) >= 4:
                score += 2
        if section and pattern.search(section):
            score += 2

    if len(matches) > 1:
        score += (len(matches) - 1) * 4
    if 60 <= len(block.content) <= 1600:
        score += 1
    return score, matches


def neighbor_preview(
    blocks: list[Block],
    block: Block,
    direction: int,
    limit: int = 220,
) -> str:
    candidate_index = block.index + direction
    if candidate_index < 0 or candidate_index >= len(blocks):
        return ""
    candidate = blocks[candidate_index]
    if candidate.document_index != block.document_index:
        return ""
    content = candidate.content
    return content if len(content) <= limit else content[: limit - 1] + "…"


def merge_adjacent(items: list[Evidence]) -> list[Evidence]:
    if not items:
        return []
    ordered = sorted(items, key=lambda item: item.index)
    merged: list[Evidence] = []
    for item in ordered:
        previous = merged[-1] if merged else None
        if (
            previous
            and previous.document_index == item.document_index
            and item.index == previous.index + len(previous.block_ids)
            and previous.location.page == item.location.page
            and previous.location.section == item.location.section
        ):
            previous.block_ids.extend(item.block_ids)
            previous.matched_terms = list(
                dict.fromkeys([*previous.matched_terms, *item.matched_terms])
            )
            previous.score = max(previous.score, item.score) + 2
            previous.content = f"{previous.content}\n\n{item.content}"
            previous.location = Location(
                document=previous.location.document,
                line_start=previous.location.line_start,
                line_end=item.location.line_end,
                page=previous.location.page,
                timestamp=previous.location.timestamp,
                section=previous.location.section,
                speaker=previous.location.speaker or item.location.speaker,
            )
            previous.next_context = item.next_context
            previous.content_hash = normalized_hash(previous.content)
            previous.evidence_id = f"ev-{previous.content_hash}"
            continue
        merged.append(item)
    return merged


def deduplicate(items: list[Evidence]) -> list[Evidence]:
    deduped: dict[str, Evidence] = {}
    for item in items:
        existing = deduped.get(item.content_hash)
        if existing is None:
            deduped[item.content_hash] = item
            continue
        locations = [existing.location, *existing.additional_locations]
        if item.location not in locations:
            existing.additional_locations.append(item.location)
        for location in item.additional_locations:
            if location not in [existing.location, *existing.additional_locations]:
                existing.additional_locations.append(location)
        existing.matched_terms = list(
            dict.fromkeys([*existing.matched_terms, *item.matched_terms])
        )
        existing.score = max(existing.score, item.score)
    return list(deduped.values())


def search(
    source_paths: Iterable[Path],
    queries: Iterable[str],
    *,
    regex: bool = False,
    top_k: int = 5,
) -> tuple[dict[str, object], list[Evidence]]:
    files, warnings = discover_sources(source_paths)
    patterns = compile_patterns(queries, regex)
    if not patterns:
        raise ValueError("At least one non-empty query is required.")

    blocks = load_blocks(files)
    hits: list[Evidence] = []
    for block in blocks:
        score, matched_terms = score_block(block, patterns)
        if not matched_terms:
            continue
        block_hash = normalized_hash(block.content)
        hits.append(
            Evidence(
                evidence_id=f"ev-{block_hash}",
                score=score,
                matched_terms=matched_terms,
                content=block.content,
                location=block.location,
                additional_locations=[],
                block_ids=[block.block_id],
                previous_context=neighbor_preview(blocks, block, -1),
                next_context=neighbor_preview(blocks, block, 1),
                content_hash=block_hash,
                index=block.index,
                document_index=block.document_index,
            )
        )

    merged = merge_adjacent(hits)
    unique = deduplicate(merged)
    ranked = sorted(
        unique,
        key=lambda item: (
            -item.score,
            -len(item.matched_terms),
            item.location.document.lower(),
            item.location.line_start,
        ),
    )[: max(1, top_k)]

    note = (
        "Current query expressions did not match. This does not prove the source "
        "corpus lacks relevant material; rewrite the queries, add synonyms, or "
        "read the closest source sections directly."
        if not ranked
        else (
            "Results are ranked by exact phrase matches, query coverage, section "
            "matches, and paragraph completeness."
        )
    )
    meta: dict[str, object] = {
        "query_terms": [term for term, _ in patterns],
        "source_files": len(files),
        "source_documents": [item.document for item in files],
        "searched_blocks": len(blocks),
        "matched_blocks": len(hits),
        "unique_results": len(unique),
        "returned_results": len(ranked),
        "top_k": max(1, top_k),
        "warnings": warnings,
        "note": note,
    }
    return meta, ranked


def print_text(meta: dict[str, object], evidence: list[Evidence]) -> None:
    print("Queries:", " | ".join(str(term) for term in meta["query_terms"]))
    print(
        "Search:",
        f"{meta['source_files']} files, "
        f"{meta['searched_blocks']} blocks, "
        f"{meta['unique_results']} unique results, "
        f"returning {meta['returned_results']}",
    )
    print("Note:", meta["note"])
    for number, item in enumerate(evidence, start=1):
        location = f"{item.location.document}:{item.location.line_start}"
        if item.location.page is not None:
            location += f" | page {item.location.page}"
        if item.location.timestamp:
            location += f" | {item.location.timestamp}"
        print(f"\n--- Evidence {number} | score {item.score} | {location} ---")
        if item.location.section:
            print("Section:", item.location.section)
        if item.location.speaker:
            print("Speaker:", item.location.speaker)
        print("Matched:", ", ".join(item.matched_terms))
        print(item.content)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Search arbitrary Markdown/text sources and return ranked, "
            "paragraph-level evidence with source locations."
        )
    )
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Markdown/text file or directory; repeat for multiple sources.",
    )
    parser.add_argument(
        "--query",
        action="append",
        required=True,
        help="Search expression; 3-8 related expressions are recommended.",
    )
    parser.add_argument("--regex", action="store_true", help="Treat queries as regex.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        meta, evidence = search(
            [Path(value) for value in args.source],
            args.query,
            regex=args.regex,
            top_k=args.top_k,
        )
    except (ValueError, re.error) as exc:
        parser.error(str(exc))

    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "meta": meta,
                    "evidence": [item.public_dict() for item in evidence],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(meta, evidence)
    return 0 if evidence else 1


if __name__ == "__main__":
    raise SystemExit(main())
