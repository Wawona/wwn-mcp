"""Load and validate the ``corpus.toml`` source manifest.

A source describes one indexable corpus: where it comes from (``git``,
``web-mirror``, ``rustdoc``, ``local``), how to filter it (include/exclude
globs), and metadata tags (``project``, ``platform``, ``stability``,
``license``) used for filtered search and citations.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

VALID_KINDS = {"git", "web-mirror", "rustdoc", "local"}


@dataclass(frozen=True)
class Source:
    name: str
    project: str
    kind: str
    # git/rustdoc/web-mirror: remote URL(s). local: filesystem path.
    url: str | None = None
    urls: list[str] = field(default_factory=list)
    ref: str | None = None
    path: str | None = None
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    # git sparse-checkout directory prefixes (cone mode) for huge repos, so we
    # materialize only the relevant subtrees (e.g. github/docs -> content/actions).
    sparse: list[str] = field(default_factory=list)
    platform: list[str] = field(default_factory=lambda: ["all"])
    stability: str | None = None
    license: str | None = None
    description: str | None = None
    # Optional crawl depth / seed list for web-mirror sources.
    seeds: list[str] = field(default_factory=list)
    max_pages: int | None = None
    # Sources whose canonical upstream URL is unconfirmed are shipped disabled
    # so `fetch` skips them cleanly until the URL/ref is verified.
    enabled: bool = True

    def all_urls(self) -> list[str]:
        out = list(self.urls)
        if self.url:
            out.insert(0, self.url)
        return out


def _coerce_source(name: str, raw: dict) -> Source:
    kind = raw.get("kind", "git")
    if kind not in VALID_KINDS:
        raise ValueError(f"source '{name}': invalid kind '{kind}' (expected one of {VALID_KINDS})")
    project = raw.get("project") or name
    return Source(
        name=name,
        project=project,
        kind=kind,
        url=raw.get("url"),
        urls=list(raw.get("urls", [])),
        ref=raw.get("ref"),
        path=raw.get("path"),
        include=list(raw.get("include", [])),
        exclude=list(raw.get("exclude", [])),
        sparse=list(raw.get("sparse", [])),
        platform=list(raw.get("platform", ["all"])),
        stability=raw.get("stability"),
        license=raw.get("license"),
        description=raw.get("description"),
        seeds=list(raw.get("seeds", [])),
        max_pages=raw.get("max_pages"),
        enabled=bool(raw.get("enabled", True)),
    )


def load_sources(manifest: Path) -> list[Source]:
    """Parse ``corpus.toml`` into a list of :class:`Source`."""
    if not manifest.exists():
        raise FileNotFoundError(f"corpus manifest not found: {manifest}")
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    sources: list[Source] = []
    # Support both [[source]] array-of-tables and [source.<name>] tables.
    for raw in data.get("source", []) if isinstance(data.get("source"), list) else []:
        sources.append(_coerce_source(raw.get("name", "unnamed"), raw))
    if isinstance(data.get("source"), dict):
        for name, raw in data["source"].items():
            sources.append(_coerce_source(name, raw))
    if not sources:
        raise ValueError(f"no [[source]] entries found in {manifest}")
    return sources


def filter_sources(sources: list[Source], only: list[str] | None) -> list[Source]:
    if not only:
        return sources
    wanted = set(only)
    return [s for s in sources if s.name in wanted or s.project in wanted]


def source_root(corpus_dir: Path, repo_root: Path, source: Source) -> Path:
    """Directory that the indexer reads for ``source``.

    ``local`` sources point at their own path (resolved relative to the repo
    root); everything else lands under ``<corpus_dir>/<name>`` once fetched.
    """
    if source.kind == "local":
        p = Path(source.path or ".")
        return p if p.is_absolute() else (repo_root / p).resolve()
    return corpus_dir / source.name
