#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import mimetypes
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from readability import Document


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
}

SKIP_EXTENSIONS = IMAGE_EXTENSIONS | {
    ".7z",
    ".avi",
    ".css",
    ".dmg",
    ".eot",
    ".exe",
    ".gz",
    ".ics",
    ".iso",
    ".js",
    ".m4a",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".otf",
    ".rar",
    ".tar",
    ".ttf",
    ".wav",
    ".webm",
    ".woff",
    ".woff2",
    ".zip",
}

SKIP_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "pinterest.com",
    "t.co",
    "twitter.com",
    "x.com",
    "youtube.com",
    "youtu.be",
}

ALWAYS_KEEP_EXTERNAL_DOMAINS = {
    "biorxiv.org",
    "cognition.ai",
    "platform.claude.com",
    "red.anthropic.com",
    "support.claude.com",
    "wikipedia.org",
}

SKIP_PATH_MARKERS = {
    "/account",
    "/accounts",
    "/careers",
    "/cart",
    "/checkout",
    "/cookie",
    "/cookies",
    "/download",
    "/events",
    "/jobs",
    "/legal",
    "/login",
    "/logout",
    "/newsletter",
    "/pricing",
    "/privacy",
    "/register",
    "/sales",
    "/search",
    "/settings",
    "/signin",
    "/signup",
    "/subscribe",
    "/support",
    "/terms",
}


@dataclass
class PageResult:
    url: str
    final_url: str
    title: str
    filename: str
    status: str
    depth: int
    role: str
    links: list[dict[str, Any]] = field(default_factory=list)
    images: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme and parsed.netloc:
        parsed = parsed._replace(scheme="https")
    elif not parsed.scheme:
        parsed = urlparse("https://" + url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = quote(unquote(parsed.path or "/"), safe="/:@")
    query = parsed.query
    normalized = urlunparse((scheme, netloc, path, "", query, ""))
    if normalized.endswith("/") and path != "/":
        normalized = normalized[:-1]
    return normalized


def slugify(value: str, fallback: str = "untitled", max_length: int = 80) -> str:
    value = unquote(value or "").strip().lower()
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if not value:
        digest = hashlib.sha1(fallback.encode("utf-8", errors="ignore")).hexdigest()[:8]
        value = f"{fallback}-{digest}"
    return value[:max_length].strip("-") or fallback


def make_out_dir(out_root: Path, title: str) -> Path:
    date_prefix = dt.date.today().isoformat()
    base_name = f"{date_prefix}-{slugify(title, 'web-pack')}"
    out_dir = out_root / base_name
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
        return out_dir
    for index in range(2, 100):
        candidate = out_root / f"{base_name}-{index}"
        if not candidate.exists():
            candidate.mkdir(parents=True)
            return candidate
    raise RuntimeError(f"Cannot create unique output directory under {out_root}")


def page_role(depth: int) -> str:
    return "MAIN" if depth == 0 else "LINKED"


def page_filename(index: int, title: str, depth: int) -> str:
    prefix = "MAIN" if depth == 0 else "LINKED"
    return f"{prefix}-{index:02d}-{slugify(title, 'page')}.md"


def should_skip_url(url: str, root_hosts: set[str], same_domain_only: bool) -> tuple[bool, str]:
    parsed = urlparse(normalize_url(url))
    if parsed.scheme not in {"http", "https"}:
        return True, "non-http"
    host = parsed.netloc.lower()
    bare_host = host[4:] if host.startswith("www.") else host
    root_bare_hosts = {h[4:] if h.startswith("www.") else h for h in root_hosts}
    if same_domain_only and bare_host not in root_bare_hosts:
        return True, "external-domain"
    if any(bare_host == d or bare_host.endswith("." + d) for d in SKIP_DOMAINS):
        return True, "social-or-low-value-domain"
    path = parsed.path.lower()
    suffix = Path(path).suffix
    if suffix in SKIP_EXTENSIONS:
        return True, "asset-link"
    if any(marker in path for marker in SKIP_PATH_MARKERS):
        return True, "low-value-path"
    if bare_host not in root_bare_hosts and not any(
        bare_host == d or bare_host.endswith("." + d) for d in ALWAYS_KEEP_EXTERNAL_DOMAINS
    ):
        meaningful_path = path.strip("/")
        if not meaningful_path or meaningful_path.lower() in {"home", "en", "www"}:
            return True, "external-homepage"
    return False, ""


def _choose_img_url(tag: Tag, base_url: str) -> str:
    for attr in ("src", "data-src", "data-original", "data-lazy-src"):
        value = tag.get(attr)
        if value:
            return urljoin(base_url, str(value))
    srcset = tag.get("srcset") or tag.get("data-srcset")
    if srcset:
        first = str(srcset).split(",")[0].strip().split(" ")[0]
        if first:
            return urljoin(base_url, first)
    return ""


def _extension_from_response(url: str, response: requests.Response) -> str:
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
    ext = mimetypes.guess_extension(content_type) or ""
    if ext == ".jpe":
        ext = ".jpg"
    path_ext = Path(urlparse(url).path).suffix.lower()
    if path_ext in IMAGE_EXTENSIONS:
        ext = path_ext
    return ext or ".img"


def _asset_name(index: int, source_url: str, response: requests.Response) -> str:
    parsed = urlparse(source_url)
    source_name = slugify(Path(parsed.path).stem or parsed.netloc or "image", "image", 40)
    digest = hashlib.sha1(source_url.encode("utf-8", errors="ignore")).hexdigest()[:8]
    ext = _extension_from_response(source_url, response)
    return f"image-{index:03d}-{source_name}-{digest}{ext}"


def download_image(
    source_url: str,
    page_url: str,
    session: requests.Session,
    assets_dir: Path,
    global_image_index: list[int],
) -> dict[str, Any]:
    source_url = urljoin(page_url, source_url)
    if not source_url or source_url.startswith("data:"):
        return {"source_url": source_url, "status": "skipped", "error": "inline-or-empty-image"}
    try:
        response = session.get(
            source_url,
            timeout=15,
            headers={"Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"},
        )
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if "image" not in content_type and Path(urlparse(source_url).path).suffix.lower() not in IMAGE_EXTENSIONS:
            return {
                "source_url": source_url,
                "status": "failed",
                "error": f"not-image-content-type:{content_type or 'unknown'}",
            }
        global_image_index[0] += 1
        filename = _asset_name(global_image_index[0], source_url, response)
        local_path = assets_dir / filename
        local_path.write_bytes(response.content)
        return {
            "source_url": source_url,
            "local_path": f"assets/{filename}",
            "status": "ok",
            "bytes": len(response.content),
            "content_type": content_type.split(";")[0],
        }
    except Exception as exc:
        return {"source_url": source_url, "status": "failed", "error": str(exc)}


def localize_markdown_images(
    markdown: str,
    page_url: str,
    session: requests.Session,
    assets_dir: Path,
    global_image_index: list[int],
) -> tuple[str, list[dict[str, Any]]]:
    images: list[dict[str, Any]] = []
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1).strip()
        source = match.group(2).strip("<>")
        if not source.lower().startswith(("http://", "https://", "/")):
            return match.group(0)
        record = download_image(source, page_url, session, assets_dir, global_image_index)
        record["alt"] = alt
        images.append(record)
        if record.get("status") == "ok":
            return f"![{alt}]({record['local_path']})"
        return f"[Image unavailable: {alt or 'image'}]({urljoin(page_url, source)})"

    return pattern.sub(replace, markdown), images


def extract_markdown_links(
    markdown: str,
    page_url: str,
    root_hosts: set[str],
    same_domain_only: bool,
) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    seen: set[str] = set()
    pattern = re.compile(r"(?<!!)\[([^\]]{1,180})\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
    for match in pattern.finditer(markdown):
        label = re.sub(r"\s+", " ", match.group(1)).strip()
        raw_url = match.group(2).strip("<>")
        absolute = normalize_url(urljoin(page_url, raw_url))
        if absolute in seen:
            continue
        seen.add(absolute)
        skip, reason = should_skip_url(absolute, root_hosts, same_domain_only)
        links.append(
            {
                "text": label,
                "url": absolute,
                "skipped": skip,
                "reason": reason,
            }
        )
    return links


def _clean_soup(soup: BeautifulSoup) -> None:
    selectors = [
        "aside",
        "footer",
        "form",
        "header nav",
        "nav",
        "noscript",
        "script",
        "style",
        "svg",
        "[aria-label='breadcrumb']",
        "[class*='breadcrumb']",
        "[class*='cookie']",
        "[class*='footer']",
        "[class*='nav']",
        "[class*='newsletter']",
        "[class*='promo']",
        "[class*='share']",
        "[id*='cookie']",
        "[id*='footer']",
        "[id*='nav']",
        "[id*='newsletter']",
        "[id*='share']",
    ]
    for selector in selectors:
        for tag in soup.select(selector):
            tag.decompose()


def _get_text_content(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    return node.get_text(" ", strip=True)


def _inline_markdown(node: Tag | NavigableString, base_url: str) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    name = node.name.lower()
    text = "".join(_inline_markdown(child, base_url) for child in node.children)
    text = re.sub(r"\s+", " ", text)
    if name == "a":
        href = node.get("href")
        label = text.strip() or str(href or "").strip()
        if href and label:
            return f"[{label}]({urljoin(base_url, str(href))})"
        return label
    if name in {"strong", "b"}:
        return f"**{text.strip()}**"
    if name in {"em", "i"}:
        return f"*{text.strip()}*"
    if name == "code":
        return f"`{text.strip()}`"
    if name == "br":
        return "\n"
    return text


def _table_to_markdown(table: Tag, base_url: str) -> str:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        rows.append([re.sub(r"\s+", " ", _inline_markdown(cell, base_url)).strip() for cell in cells])
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    header = rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _blocks_to_markdown(
    root: Tag,
    base_url: str,
    session: requests.Session,
    assets_dir: Path,
    global_image_index: list[int],
    images: list[dict[str, Any]],
) -> str:
    lines: list[str] = []

    def emit(line: str = "") -> None:
        line = line.rstrip()
        if line:
            lines.append(line)
        elif lines and lines[-1] != "":
            lines.append("")

    def walk(node: Tag | NavigableString, list_prefix: str = "") -> None:
        if isinstance(node, NavigableString):
            return
        name = node.name.lower()
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(name[1])
            text = re.sub(r"\s+", " ", _inline_markdown(node, base_url)).strip()
            if text:
                emit()
                emit(f"{'#' * level} {text}")
                emit()
            return
        if name == "p":
            text = re.sub(r"\s+", " ", _inline_markdown(node, base_url)).strip()
            if text:
                emit(text)
                emit()
            return
        if name == "blockquote":
            text = re.sub(r"\s+", " ", _inline_markdown(node, base_url)).strip()
            if text:
                emit("> " + text)
                emit()
            return
        if name == "pre":
            text = node.get_text("\n").strip()
            if text:
                emit("```")
                lines.extend(text.splitlines())
                emit("```")
                emit()
            return
        if name == "img":
            source = _choose_img_url(node, base_url)
            alt = str(node.get("alt") or "").strip()
            record = download_image(source, base_url, session, assets_dir, global_image_index)
            record["alt"] = alt
            images.append(record)
            if record.get("status") == "ok":
                emit(f"![{alt}]({record['local_path']})")
                emit()
            elif alt:
                emit(f"[Image unavailable: {alt}]({record.get('source_url', source)})")
                emit()
            return
        if name in {"ul", "ol"}:
            ordered = name == "ol"
            index = 1
            for li in node.find_all("li", recursive=False):
                text = re.sub(r"\s+", " ", _inline_markdown(li, base_url)).strip()
                if text:
                    marker = f"{index}." if ordered else "-"
                    emit(f"{marker} {text}")
                    index += 1
            emit()
            return
        if name == "table":
            table_md = _table_to_markdown(node, base_url)
            if table_md:
                emit(table_md)
                emit()
            return
        for child in node.children:
            if isinstance(child, Tag):
                walk(child, list_prefix)

    for child in root.children:
        if isinstance(child, Tag):
            walk(child)
    text = "\n".join(lines)
    text = re.sub(r"\n{4,}", "\n\n\n", text).strip()
    return text


def _extract_article_soup(html: str, final_url: str) -> tuple[str, BeautifulSoup]:
    soup = BeautifulSoup(html, "lxml")
    raw_title = ""
    if soup.title and soup.title.string:
        raw_title = soup.title.string.strip()
    h1 = soup.find("h1")
    if h1:
        raw_title = h1.get_text(" ", strip=True) or raw_title
    try:
        doc = Document(html)
        title = doc.short_title() or raw_title or final_url
        article_html = doc.summary(html_partial=True)
        article_soup = BeautifulSoup(article_html, "lxml")
        _clean_soup(article_soup)
        if len(article_soup.get_text(" ", strip=True)) > 250:
            return title, article_soup
    except Exception:
        pass
    _clean_soup(soup)
    root = soup.find("article") or soup.find("main") or soup.body or soup
    title = raw_title or final_url
    return title, BeautifulSoup(str(root), "lxml")


def _plain_resource_to_markdown(content: str, content_type: str) -> str:
    if "json" in content_type:
        return "```json\n" + content.strip() + "\n```"
    if "markdown" in content_type or "text/plain" in content_type:
        return content.strip()
    return "```\n" + content.strip() + "\n```"


def process_page(
    session: requests.Session,
    url: str,
    depth: int,
    out_dir: Path,
    assets_dir: Path,
    index: int,
    root_hosts: set[str],
    same_domain_only: bool,
    global_image_index: list[int],
) -> PageResult:
    role = page_role(depth)
    normalized = normalize_url(url)
    try:
        final_url_for_error = normalized
        response = session.get(normalized, timeout=20, stream=True)
        response.raise_for_status()
        final_url = normalize_url(response.url)
        final_url_for_error = final_url
        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
        images: list[dict[str, Any]] = []
        if "pdf" in content_type or Path(urlparse(final_url).path).suffix.lower() == ".pdf":
            response.close()
            raise RuntimeError("direct extraction unsupported for pdf")
        response_text = response.text
        if "html" in content_type or "<html" in response_text[:500].lower():
            title, article_soup = _extract_article_soup(response_text, final_url)
            markdown = _blocks_to_markdown(
                article_soup,
                final_url,
                session,
                assets_dir,
                global_image_index,
                images,
            )
            if len(re.sub(r"\s+", "", markdown)) < 120:
                raise RuntimeError("direct extraction produced too little text")
        else:
            title = Path(urlparse(final_url).path).name or final_url
            markdown = _plain_resource_to_markdown(response_text, content_type)
        links = extract_markdown_links(markdown, final_url, root_hosts, same_domain_only)
        filename = page_filename(index, title, depth)
        write_page_markdown(out_dir / filename, title, normalized, final_url, role, markdown, links)
        return PageResult(
            url=normalized,
            final_url=final_url,
            title=title,
            filename=filename,
            status="ok",
            depth=depth,
            role=role,
            links=links,
            images=images,
        )
    except Exception as exc:
        final_url_for_error = locals().get("final_url_for_error", normalized)
        filename = page_filename(index, normalized, depth)
        return PageResult(
            url=normalized,
            final_url=final_url_for_error,
            title=normalized,
            filename=filename,
            status="failed",
            depth=depth,
            role=role,
            error=str(exc),
        )


def _escape_table(value: Any) -> str:
    text = str(value or "").replace("\n", " ").replace("|", "\\|")
    return re.sub(r"\s+", " ", text).strip()


def write_page_markdown(
    path: Path,
    title: str,
    url: str,
    final_url: str,
    role: str,
    body: str,
    links: list[dict[str, Any]],
) -> None:
    lines = [
        "---",
        f"title: {_escape_table(title)}",
        f"source: {url}",
        f"final_url: {final_url}",
        f"role: {role}",
        f"captured_at: {dt.datetime.now().isoformat(timespec='seconds')}",
        "---",
        "",
        f"# {title}",
        "",
        body.strip(),
        "",
    ]
    usable_links = [link for link in links if not link.get("skipped")]
    skipped_links = [link for link in links if link.get("skipped")]
    if usable_links:
        lines.extend(["", "## Body Links", ""])
        for link in usable_links:
            label = _escape_table(link.get("text") or link.get("url"))
            lines.append(f"- [{label}]({link['url']})")
    if skipped_links:
        lines.extend(["", "## Skipped Links", ""])
        for link in skipped_links:
            label = _escape_table(link.get("text") or link.get("url"))
            reason = _escape_table(link.get("reason"))
            lines.append(f"- {label}: {link['url']} ({reason})")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_inventory(
    out_dir: Path,
    title: str,
    roots: list[str],
    pages: list[PageResult],
    skipped_queue: list[dict[str, Any]],
    max_depth: int,
    max_pages: int,
) -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")
    ok_pages = [page for page in pages if page.status == "ok"]
    restricted_pages = [page for page in pages if page.status == "restricted"]
    available_pages = [page for page in pages if page.status in {"ok", "restricted"}]
    linked_ok = [page for page in available_pages if page.role == "LINKED"]
    main_ok = [page for page in available_pages if page.role == "MAIN"]
    images = [img | {"page": page.title} for page in pages for img in page.images]
    fallback_pages = [page for page in pages if "r.jina.ai" in page.final_url or "used-r.jina.ai" in page.error]
    failed_pages = [page for page in pages if page.status not in {"ok", "restricted"}]

    readme = [
        f"# {title}",
        "",
        f"- Generated: {now}",
        "- Generator: `1-web-research-pack`",
        f"- Entry URLs: {len(roots)}",
        f"- Pages captured: {len(ok_pages)}",
        f"- Main pages: {len(main_ok)}",
        f"- Linked pages: {len(linked_ok)}",
        f"- Restricted pages: {len(restricted_pages)}",
        f"- Images saved: {sum(1 for img in images if img.get('status') == 'ok')}",
        f"- Max depth: {max_depth}",
        f"- Max pages: {max_pages}",
        "",
        "## Files",
        "",
        "- `00-research-brief.md`",
        "- `01-link-inventory.md`",
        "- `02-image-inventory.md`",
        "- `03-reading-map.md`",
    ]
    out_dir.joinpath("README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    brief = [
        f"# Research Brief: {title}",
        "",
        "## Source Set",
        "",
        *[f"- {root}" for root in roots],
        "",
        "## Capture Summary",
        "",
        f"- Main pages captured: {len(main_ok)}",
        f"- Linked pages captured: {len(linked_ok)}",
        f"- Restricted pages: {len(restricted_pages)}",
        f"- Images saved: {sum(1 for img in images if img.get('status') == 'ok')}",
        f"- Failed pages: {len(failed_pages)}",
        f"- Skipped queued links: {len(skipped_queue)}",
        f"- Jina fallback pages: {len(fallback_pages)}",
        "",
        "## Primary Reading Order",
        "",
    ]
    for page in main_ok + linked_ok:
        brief.append(f"- `{page.filename}` - {page.title}")
    if restricted_pages or failed_pages or skipped_queue:
        brief.extend(["", "## Caveats", ""])
        for page in restricted_pages:
            brief.append(f"- Restricted: {page.url} ({page.error})")
        for page in failed_pages:
            brief.append(f"- Failed: {page.url} ({page.error})")
        for item in skipped_queue[:50]:
            brief.append(f"- Skipped: {item.get('url')} ({item.get('reason')})")
    out_dir.joinpath("00-research-brief.md").write_text("\n".join(brief) + "\n", encoding="utf-8")

    inventory = [
        f"# Link Inventory: {title}",
        "",
        "| Role | Status | File | Title | URL | Final URL | Note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for page in pages:
        note = page.error or ""
        inventory.append(
            "| "
            + " | ".join(
                [
                    _escape_table(page.role),
                    _escape_table(page.status),
                    _escape_table(page.filename),
                    _escape_table(page.title),
                    _escape_table(page.url),
                    _escape_table(page.final_url),
                    _escape_table(note),
                ]
            )
            + " |"
        )
    if skipped_queue:
        inventory.extend(["", "## Skipped Queue", ""])
        inventory.extend(["| URL | Reason |", "| --- | --- |"])
        for item in skipped_queue:
            inventory.append(f"| {_escape_table(item.get('url'))} | {_escape_table(item.get('reason'))} |")
    out_dir.joinpath("01-link-inventory.md").write_text("\n".join(inventory) + "\n", encoding="utf-8")

    image_inventory = [
        f"# Image Inventory: {title}",
        "",
        "| Status | Page | Local Path | Source URL | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for img in images:
        image_inventory.append(
            "| "
            + " | ".join(
                [
                    _escape_table(img.get("status")),
                    _escape_table(img.get("page")),
                    _escape_table(img.get("local_path")),
                    _escape_table(img.get("source_url")),
                    _escape_table(img.get("error") or img.get("content_type") or img.get("bytes")),
                ]
            )
            + " |"
        )
    if not images:
        image_inventory.append("| none | none | none | none | no body images found |")
    out_dir.joinpath("02-image-inventory.md").write_text("\n".join(image_inventory) + "\n", encoding="utf-8")

    reading_map = [
        f"# Reading Map: {title}",
        "",
        "## Main",
        "",
    ]
    if main_ok:
        reading_map.extend([f"- `{page.filename}` - {page.title}" for page in main_ok])
    else:
        reading_map.append("- No main page captured.")
    reading_map.extend(["", "## Linked", ""])
    if linked_ok:
        reading_map.extend([f"- `{page.filename}` - {page.title}" for page in linked_ok])
    else:
        reading_map.append("- No linked pages captured.")
    if fallback_pages:
        reading_map.extend(["", "## Jina Fallback", ""])
        reading_map.extend([f"- `{page.filename}` - {page.url}" for page in fallback_pages])
    if restricted_pages:
        reading_map.extend(["", "## Restricted", ""])
        reading_map.extend([f"- `{page.filename}` - {page.url}: {page.error}" for page in restricted_pages])
    if failed_pages:
        reading_map.extend(["", "## Failed", ""])
        reading_map.extend([f"- {page.url}: {page.error}" for page in failed_pages])
    if skipped_queue:
        reading_map.extend(["", "## Skipped Queue", ""])
        reading_map.extend([f"- {item.get('url')}: {item.get('reason')}" for item in skipped_queue[:100]])
    out_dir.joinpath("03-reading-map.md").write_text("\n".join(reading_map) + "\n", encoding="utf-8")
