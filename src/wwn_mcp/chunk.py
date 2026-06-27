"""Turn corpus files into retrievable chunks with rich metadata + citations.

Chunkers:
  * markdown  - split by heading, keep line ranges
  * code      - split by top-level symbol (regex heuristics) then window
  * protocol  - one chunk per Wayland <interface> in a protocol .xml
  * patch     - whole-file (small) patch artifacts
  * text/html - strip + window

Every chunk records project, path, line range, kind, lang, tags and a content
hash for incremental indexing, plus a source URL hint for citations.
"""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .corpus import Source

_CODE_EXT = {
    ".rs": "rust", ".c": "c", ".h": "c", ".m": "objc", ".mm": "objcpp",
    ".cpp": "cpp", ".hpp": "cpp", ".swift": "swift", ".kt": "kotlin",
    ".java": "java", ".nix": "nix", ".sh": "bash", ".py": "python",
    ".js": "javascript", ".ts": "typescript",
}
_DOC_EXT = {".md", ".mdx", ".markdown", ".rst", ".adoc", ".txt", ".scd"}
_WINDOW_LINES = 60
_WINDOW_OVERLAP = 10
_MAX_CHARS = 4000

# Regex of top-level symbol starts, per family (best-effort, not a parser).
_SYMBOL_RE = re.compile(
    r"^\s*(?:pub\s+)?(?:async\s+)?"
    r"(?:fn|struct|enum|trait|impl|mod|class|interface|func|object|"
    r"def|void|static|public|private|internal|extension|protocol)\b"
)


@dataclass
class Chunk:
    chunk_id: str
    project: str
    source: str
    path: str
    kind: str  # docs | code | protocol | patch | text
    lang: str | None
    title: str
    text: str
    start_line: int
    end_line: int
    url: str | None
    license: str | None
    tags: dict[str, str] = field(default_factory=dict)
    content_hash: str = ""

    def as_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "project": self.project,
            "source": self.source,
            "path": self.path,
            "kind": self.kind,
            "lang": self.lang,
            "title": self.title,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "url": self.url,
            "license": self.license,
            "tags": self.tags,
        }


def _hash(*parts: str) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update(p.encode("utf-8", errors="ignore"))
        h.update(b"\0")
    return h.hexdigest()


def _kind_for(path: Path) -> tuple[str, str | None]:
    ext = path.suffix.lower()
    if ext == ".patch":
        return "patch", "diff"
    if ext in _CODE_EXT:
        return "code", _CODE_EXT[ext]
    if ext == ".xml":
        return "protocol", "xml"
    if ext in _DOC_EXT:
        return "docs", "markdown" if ext in {".md", ".mdx", ".markdown"} else None
    if ext in {".html", ".htm"}:
        return "docs", "html"
    if ext == ".json":
        return "text", "json"
    return "text", None


def _make(
    src: Source, rel: str, kind: str, lang: str | None, title: str, text: str,
    start: int, end: int,
) -> Chunk:
    chash = _hash(text)
    return Chunk(
        chunk_id=_hash(src.name, rel, str(start), chash[:8]),
        project=src.project,
        source=src.name,
        path=rel,
        kind=kind,
        lang=lang,
        title=title[:200] or rel,
        text=text[:_MAX_CHARS],
        start_line=start,
        end_line=end,
        url=_cite_url(src, rel),
        license=src.license,
        tags=_tags(src),
        content_hash=chash,
    )


def _tags(src: Source) -> dict[str, str]:
    t: dict[str, str] = {}
    if src.stability:
        t["stability"] = src.stability
    if src.platform:
        t["platform"] = ",".join(src.platform)
    return t


def _cite_url(src: Source, rel: str) -> str | None:
    if src.kind == "git" and src.url:
        base = src.url.rstrip("/").removesuffix(".git")
        ref = src.ref or "HEAD"
        return f"{base}/blob/{ref}/{rel}"
    if src.kind in ("web-mirror", "rustdoc") and src.url:
        return src.url
    return None


# --- markdown ---------------------------------------------------------------

def _chunk_markdown(src: Source, rel: str, text: str) -> Iterator[Chunk]:
    lines = text.splitlines()
    section: list[str] = []
    title = rel
    start = 1
    for i, line in enumerate(lines, start=1):
        if line.lstrip().startswith("#") and section:
            body = "\n".join(section).strip()
            if body:
                yield _make(src, rel, "docs", "markdown", title, body, start, i - 1)
            section = []
            title = line.lstrip("#").strip() or title
            start = i
        else:
            if line.lstrip().startswith("#") and not section:
                title = line.lstrip("#").strip() or title
                start = i
            section.append(line)
    body = "\n".join(section).strip()
    if body:
        yield _make(src, rel, "docs", "markdown", title, body, start, len(lines))


# --- code -------------------------------------------------------------------

def _chunk_code(src: Source, rel: str, lang: str | None, text: str) -> Iterator[Chunk]:
    lines = text.splitlines()
    # Symbol-aware boundaries; fall back to windows if too few symbols.
    starts = [i for i, ln in enumerate(lines) if _SYMBOL_RE.match(ln)]
    if len(starts) >= 2 and len(lines) > _WINDOW_LINES:
        bounds = starts + [len(lines)]
        for a, b in zip(bounds, bounds[1:], strict=False):
            seg = "\n".join(lines[a:b]).strip()
            if seg:
                title = lines[a].strip()
                yield _make(src, rel, "code", lang, title, seg, a + 1, b)
        # also a header window (imports/top) for context
        head = "\n".join(lines[: starts[0]]).strip()
        if head:
            yield _make(src, rel, "code", lang, f"{rel} (header)", head, 1, starts[0])
        return
    yield from _chunk_windows(src, rel, "code", lang, lines)


def _chunk_windows(src: Source, rel: str, kind: str, lang: str | None, lines: list[str]) -> Iterator[Chunk]:
    step = _WINDOW_LINES - _WINDOW_OVERLAP
    n = len(lines)
    if n == 0:
        return
    for a in range(0, n, step):
        seg = "\n".join(lines[a : a + _WINDOW_LINES]).strip()
        if seg:
            yield _make(src, rel, kind, lang, rel, seg, a + 1, min(a + _WINDOW_LINES, n))


# --- protocol (wayland xml) -------------------------------------------------

def _chunk_protocol(src: Source, rel: str, text: str) -> Iterator[Chunk]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        yield from _chunk_windows(src, rel, "text", "xml", text.splitlines())
        return
    if root.tag != "protocol":
        yield from _chunk_windows(src, rel, "text", "xml", text.splitlines())
        return
    proto_name = root.get("name", Path(rel).stem)
    for iface in root.findall("interface"):
        iname = iface.get("name", "")
        parts = [f"protocol {proto_name} :: interface {iname} (v{iface.get('version','?')})"]
        desc = iface.find("description")
        if desc is not None and (desc.text or desc.get("summary")):
            parts.append((desc.get("summary") or "") + "\n" + (desc.text or "").strip())
        for kind_tag in ("request", "event", "enum"):
            for el in iface.findall(kind_tag):
                summ = ""
                d = el.find("description")
                if d is not None:
                    summ = d.get("summary") or ""
                parts.append(f"  {kind_tag} {el.get('name','')}: {summ}".rstrip())
        body = "\n".join(parts).strip()
        yield Chunk(
            chunk_id=_hash(src.name, rel, iname),
            project=src.project,
            source=src.name,
            path=rel,
            kind="protocol",
            lang="xml",
            title=iname or proto_name,
            text=body[:_MAX_CHARS],
            start_line=1,
            end_line=len(text.splitlines()),
            url=_cite_url(src, rel),
            license=src.license,
            tags={**_tags(src), "protocol": proto_name, "interface": iname},
            content_hash=_hash(body),
        )


# --- html / text ------------------------------------------------------------

class _TextHTML:
    """Minimal HTML -> text (strip tags/scripts/styles)."""

    @staticmethod
    def strip(html: str) -> str:
        html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
        html = re.sub(r"(?is)<[^>]+>", " ", html)
        html = re.sub(r"&[a-z]+;", " ", html)
        return re.sub(r"\s+", " ", html).strip()


def _chunk_text(src: Source, rel: str, lang: str | None, text: str) -> Iterator[Chunk]:
    if lang == "html":
        text = _TextHTML.strip(text)
        lang = None
    yield from _chunk_windows(src, rel, "text", lang, text.splitlines() or [text])


# --- file dispatch ----------------------------------------------------------

def chunk_file(src: Source, abs_path: Path, rel: str) -> Iterator[Chunk]:
    try:
        if abs_path.suffix.lower() == ".pdf":
            # No PDF text dep: index a reference stub so the doc is discoverable.
            yield _make(src, rel, "text", None, f"{rel} (PDF reference)",
                        f"PDF document: {rel}", 1, 1)
            return
        text = abs_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    if not text.strip():
        return
    kind, lang = _kind_for(abs_path)
    if kind == "docs" and lang == "markdown":
        yield from _chunk_markdown(src, rel, text)
    elif kind == "code":
        yield from _chunk_code(src, rel, lang, text)
    elif kind == "protocol":
        yield from _chunk_protocol(src, rel, text)
    elif kind == "patch":
        yield _make(src, rel, "patch", "diff", rel, text, 1, len(text.splitlines()))
    else:
        yield from _chunk_text(src, rel, lang, text)
