"""FastMCP server exposing the WWN-MCP retrieval tools and resources.

Transport is **stdio only** (mcp-nixos host model — any MCP client). There is no
HTTP / Streamable HTTP path.

Every tool returns structured results that carry citations (project, path,
line range, source URL) so models can open the underlying files.
"""

from __future__ import annotations

from typing import Any

from .config import Settings
from .corpus import load_sources, source_root
from .patches import load_inventory
from .store import SearchResult, Store


def _fmt(results: list[SearchResult]) -> list[dict[str, Any]]:
    return [
        {
            "title": r.title,
            "project": r.project,
            "kind": r.kind,
            "lang": r.lang,
            "path": r.path,
            "lines": [r.start_line, r.end_line],
            "url": r.url,
            "license": r.license,
            "tags": r.tags,
            "citation": r.citation(),
            "snippet": r.text[:1200],
            "score": round(r.score, 4),
        }
        for r in results
    ]


def build_server(settings: Settings):  # -> FastMCP
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("wwn-mcp")
    store = Store(settings)

    @mcp.tool()
    def search(query: str, kind: str | None = None, project: str | None = None,
               lang: str | None = None, top_k: int = 8) -> list[dict]:
        """Hybrid (semantic + lexical) search across the whole Wawona corpus.

        Filter with kind (docs|code|protocol|patch|text), project, or lang.
        """
        return _fmt(store.search(query, kind=kind, project=project, lang=lang, top_k=top_k))

    @mcp.tool()
    def search_docs(query: str, project: str | None = None, top_k: int = 8) -> list[dict]:
        """Search documentation/prose only."""
        return _fmt(store.search(query, kind="docs", project=project, top_k=top_k))

    @mcp.tool()
    def search_code(query: str, project: str | None = None, lang: str | None = None,
                    top_k: int = 8) -> list[dict]:
        """Search source code only (optionally by language)."""
        return _fmt(store.search(query, kind="code", project=project, lang=lang, top_k=top_k))

    @mcp.tool()
    def find_symbol(name: str, project: str | None = None, top_k: int = 10) -> list[dict]:
        """Find a function/type/symbol definition by name across code."""
        return _fmt(store.search(name, kind="code", project=project, top_k=top_k))

    @mcp.tool()
    def get_architecture(topic: str, top_k: int = 8) -> list[dict]:
        """Retrieve Wawona architecture docs for a topic (multi-repo + knowledge).

        Searches curated knowledge under ``project=wawona`` and ``ios-shell``,
        plus architecture READMEs from Wawona integration and ``wwn-*`` repos
        (weston, iland, waypipe, coreutils, niri, kmscube, ssh).
        """
        per = max(2, (top_k + 4) // 5)
        projects = [
            "wawona", "ios-shell", "weston", "iland", "waypipe", "coreutils",
            "niri", "kmscube", "ssh",
        ]
        seen: set[str] = set()
        merged: list = []
        for proj in projects:
            for r in store.search(topic, kind="docs", project=proj, top_k=per):
                cid = r.citation()
                if cid in seen:
                    continue
                seen.add(cid)
                merged.append(r)
        merged.sort(key=lambda r: r.score, reverse=True)
        return _fmt(merged[:top_k])

    @mcp.tool()
    def list_projects() -> list[dict]:
        """List indexed projects and their chunk counts."""
        s = store.stats()
        return [{"project": k, "chunks": v} for k, v in sorted(s["by_project"].items())]

    @mcp.tool()
    def list_protocols(family: str | None = None, stability: str | None = None) -> list[dict]:
        """List Wayland protocols (optionally filtered by family/stability)."""
        return store.list_protocols(family=family, stability=stability)

    @mcp.tool()
    def get_protocol(name: str) -> list[dict]:
        """Get a Wayland protocol's interfaces/requests/events/enums by name."""
        return _fmt(store.get_protocol(name))

    @mcp.tool()
    def list_patches() -> list[dict]:
        """List patched upstreams across Wawona + all wwn-* repos (dependencies/)."""
        inv = load_inventory(settings)
        return [
            {
                "repo": e["repo"],
                "key": e["key"],
                "software": e["software"],
                "name": e["name"],
                "category": e["category"],
                "platforms": e["platforms"],
                "patch_files": e["patch_files"],
                "inline_patches": e["inline_patches"],
            }
            for e in inv.get("entries", {}).values()
        ]

    @mcp.tool()
    def get_patch(software: str) -> dict:
        """Get patch detail for one upstream (e.g. 'zsh', 'wwn-zsh/zsh', 'weston')."""
        from .patches import resolve_patch

        inv = load_inventory(settings)
        entry = resolve_patch(inv.get("entries", {}), software)
        if entry is not None:
            return entry
        available = sorted(
            f"{e['repo']}/{e['name']}" for e in inv.get("entries", {}).values()
        )
        return {"error": f"no patched software named '{software}'", "available": available}

    @mcp.tool()
    def list_repos() -> list[dict]:
        """List Wawona org repos with layer, role, and when-to-edit hints."""
        from .contribute import list_repos as _list

        return _list()

    @mcp.tool()
    def where_to_edit(change: str) -> dict:
        """Map a change description to the correct Wawona org repo.

        Examples: 'zsh patch', 'ANGLE', 'niri recipe', 'Machines UI', 'wayland protocol'.
        """
        from .contribute import where_to_edit as _where

        return _where(change)

    @mcp.tool()
    def get_capability(platform: str, feature: str) -> dict:
        """Four-state capability gate for a platform + feature.

        States: available | planned | blocked | forbidden.
        Platforms: macos, ios, ipados, tvos, watchos, visionos, android, linux.
        Features: native, remote, vm, container, multi_window, nested_compositors,
        gpu, desktop, anowaw.
        """
        from .contribute import get_capability as _cap

        return _cap(platform, feature)

    @mcp.tool()
    def read_document(ref: str, start: int | None = None, end: int | None = None) -> dict:
        """Read a chunk by id, or a file by 'source/relative/path' (optional line range)."""
        # chunk id?
        row = store.db.execute("SELECT * FROM chunks WHERE chunk_id=?", (ref,)).fetchone()
        if row is not None:
            return {"path": row["path"], "project": row["project"], "lines": [row["start_line"],
                    row["end_line"]], "url": row["url"], "text": row["text"]}
        # source/relpath
        if "/" in ref:
            source_name, rel = ref.split("/", 1)
            roots = {s.name: source_root(settings.corpus_dir, settings.corpus_manifest.parent, s)
                     for s in load_sources(settings.corpus_manifest)}
            root = roots.get(source_name)
            if root is not None:
                fp = (root / rel)
                if fp.exists() and fp.is_file():
                    lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
                    a = (start or 1) - 1
                    b = end or len(lines)
                    return {"path": rel, "source": source_name,
                            "lines": [a + 1, b], "text": "\n".join(lines[a:b])}
        return {"error": f"could not resolve ref '{ref}'"}

    # --- resources ---------------------------------------------------------

    @mcp.resource("wwn://status")
    def status() -> str:
        """Index status + corpus statistics."""
        import json

        stats = store.stats()
        meta = {
            k: v
            for k, v in (
                (r["key"], r["value"])
                for r in store.db.execute("SELECT key, value FROM meta").fetchall()
            )
        }
        from .embed import Embedder

        emb = Embedder(settings.model_name, settings.embed_dim)
        out = {
            **stats,
            "embed_backend": emb.backend,
            "last_indexed": meta.get("last_indexed"),
            "source_shas": json.loads(meta.get("source_shas", "{}")),
            "transport": "stdio",
        }
        return json.dumps(out, indent=2)

    @mcp.resource("wwn://patches")
    def patches_resource() -> str:
        """The full patched-software inventory."""
        import json

        return json.dumps(load_inventory(settings), indent=2)

    return mcp


def run_server(settings: Settings) -> None:
    """Run the MCP server over stdio (only supported transport)."""
    mcp = build_server(settings)
    mcp.run(transport="stdio")
