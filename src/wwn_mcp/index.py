"""Indexing pipeline: walk fetched corpus -> chunk -> embed -> store.

Incremental: per source we compute the set of current chunk ids, skip chunks
whose content hash is unchanged, upsert new/changed ones, and prune stale ones.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from .chunk import Chunk, chunk_file
from .config import Settings
from .corpus import Source, filter_sources, load_sources, source_root
from .embed import Embedder
from .store import Store

_DEFAULT_INCLUDE = [
    "**/*.md", "**/*.mdx", "**/*.markdown", "**/*.rst", "**/*.adoc", "**/*.txt", "**/*.scd",
    "**/*.rs", "**/*.c", "**/*.h", "**/*.m", "**/*.mm", "**/*.cpp", "**/*.hpp",
    "**/*.swift", "**/*.kt", "**/*.java", "**/*.nix", "**/*.sh", "**/*.py",
    "**/*.xml", "**/*.html", "**/*.patch", "**/*.json",
]
_DEFAULT_EXCLUDE = ["**/.git/**", "**/node_modules/**", "**/target/**", "**/build/**"]
_MAX_FILE_BYTES = 2_000_000
_BATCH = 128


def _iter_files(root: Path, include: list[str], exclude: list[str]):
    inc = include or _DEFAULT_INCLUDE
    exc = (exclude or []) + _DEFAULT_EXCLUDE
    seen: set[Path] = set()
    for pat in inc:
        for p in root.glob(pat):
            if not p.is_file() or p in seen:
                continue
            rel = p.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, e) or fnmatch.fnmatch(rel, e.replace("/**", "/*")) for e in exc):
                continue
            try:
                if p.stat().st_size > _MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            seen.add(p)
            yield p, rel


def _index_source(store: Store, embedder: Embedder, src: Source, root: Path) -> dict:
    existing = store.existing_hashes(src.name)
    seen_ids: set[str] = set()
    pending: list[Chunk] = []
    added = changed = unchanged = 0

    def flush() -> None:
        nonlocal pending
        if not pending:
            return
        vecs = embedder.embed([c.text for c in pending])
        for c, v in zip(pending, vecs, strict=False):
            store.upsert(c, v)
        pending = []

    for abs_path, rel in _iter_files(root, src.include, src.exclude):
        for ch in chunk_file(src, abs_path, rel):
            seen_ids.add(ch.chunk_id)
            prev = existing.get(ch.chunk_id)
            if prev == ch.content_hash:
                unchanged += 1
                continue
            if prev is None:
                added += 1
            else:
                changed += 1
            pending.append(ch)
            if len(pending) >= _BATCH:
                flush()
    flush()
    pruned = store.prune(src.name, seen_ids)
    store.commit()
    return {"added": added, "changed": changed, "unchanged": unchanged, "pruned": pruned}


def build_index(settings: Settings, only: list[str] | None = None, reset: bool = False) -> dict:
    sources = filter_sources(load_sources(settings.corpus_manifest), only)
    store = Store(settings)
    if reset:
        store.reset()
    embedder = Embedder(settings.model_name, settings.embed_dim)
    per_source: dict[str, dict] = {}
    for src in sources:
        if not src.enabled:
            continue
        root = source_root(settings.corpus_dir, settings.corpus_manifest.parent, src)
        if not root.exists():
            per_source[src.name] = {"skipped": "not fetched"}
            continue
        print(f"  index: {src.name} ({src.project}) <- {root}")
        per_source[src.name] = _index_source(store, embedder, src, root)

    # Derived inventories (patches + protocols) for the dedicated MCP tools.
    from .patches import generate_inventory

    patch_inv = generate_inventory(settings, sources)
    store.db.execute(
        "INSERT INTO meta(key,value) VALUES('patch_count',?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (str(patch_inv.get("count", 0)),),
    )
    store.commit()

    return {
        "embedder": embedder.backend,
        "vector_backend": store.stats()["vector_backend"],
        "sources": per_source,
        "patches": patch_inv.get("count", 0),
        "totals": store.stats(),
    }
