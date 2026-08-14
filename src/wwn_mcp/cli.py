"""``wwn-mcp`` command-line entry point.

Bare ``wwn-mcp`` (no subcommand) starts the MCP server over **stdio**
(mcp-nixos host model). Subcommands: fetch | index | search | serve | info.
"""

from __future__ import annotations

import argparse
import json
import sys

from .config import Settings

# Knowledge sources indexed automatically when the DB is empty (first spawn).
_KNOWLEDGE_ONLY = ["wwn-knowledge", "wwn-knowledge-wawona"]


def _add_only(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--only",
        nargs="*",
        default=None,
        metavar="NAME",
        help="Limit to these source/project names (default: all).",
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wwn-mcp", description=__doc__)
    p.add_argument("--data-dir", default=None, help="Override the runtime data dir.")
    sub = p.add_subparsers(dest="cmd", required=False)

    p_fetch = sub.add_parser("fetch", help="Mirror/clone corpus sources from corpus.toml.")
    _add_only(p_fetch)
    p_fetch.add_argument("--depth", type=int, default=1, help="git shallow clone depth (0=full).")

    p_index = sub.add_parser("index", help="Chunk + embed the fetched corpus into the index.")
    _add_only(p_index)
    p_index.add_argument("--reset", action="store_true", help="Drop and rebuild the index.")
    p_index.add_argument(
        "--local-siblings",
        action="store_true",
        help="Index only local-sibling / knowledge sources (skip git/web that are not fetched).",
    )
    p_index.add_argument(
        "--knowledge",
        action="store_true",
        help="Index only shipped knowledge/ sources (fast first-run).",
    )

    p_search = sub.add_parser("search", help="Query the hybrid index from the terminal.")
    p_search.add_argument("query")
    p_search.add_argument("--kind", default=None, help="docs|code|symbol|protocol|patch")
    p_search.add_argument("--project", default=None)
    p_search.add_argument("--lang", default=None)
    p_search.add_argument("-k", "--top-k", type=int, default=8)
    p_search.add_argument("--json", action="store_true")

    sub.add_parser("serve", help="Start the MCP server over stdio (same as bare wwn-mcp).")
    sub.add_parser("info", help="Print resolved settings and index status.")
    return p


def _settings(args: argparse.Namespace) -> Settings:
    import os

    if args.data_dir:
        os.environ["WWN_MCP_DATA_DIR"] = args.data_dir
    return Settings.load()


def _ensure_knowledge_index(settings: Settings) -> None:
    """If the sqlite index is missing or empty, index shipped knowledge/ only."""
    needs = (not settings.db_path.exists()) or settings.db_path.stat().st_size < 4096
    if not needs:
        from .store import Store

        store = Store(settings)
        if store.stats().get("chunks", 0) > 0:
            return
    from .index import build_index

    print("wwn-mcp: empty index — indexing shipped knowledge/ …", file=sys.stderr)
    build_index(settings, only=_KNOWLEDGE_ONLY, reset=False)


def _index_only_args(args: argparse.Namespace) -> list[str] | None:
    if getattr(args, "knowledge", False):
        return list(_KNOWLEDGE_ONLY)
    if getattr(args, "local_siblings", False):
        from .corpus import load_sources

        return [s.name for s in load_sources(Settings.load().corpus_manifest)
                if s.kind == "local" and s.enabled]
    return args.only


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = _settings(args)
    settings.ensure_dirs()

    cmd = args.cmd
    if cmd is None:
        cmd = "serve"

    if cmd == "fetch":
        from .fetch import fetch_all

        n = fetch_all(settings, only=args.only, depth=args.depth)
        print(f"fetched/updated {n} source(s) into {settings.corpus_dir}")
        return 0

    if cmd == "index":
        from .index import build_index

        only = _index_only_args(args)
        stats = build_index(settings, only=only, reset=args.reset)
        print(json.dumps(stats, indent=2))
        return 0

    if cmd == "search":
        from .store import Store

        store = Store(settings)
        results = store.search(
            args.query,
            kind=args.kind,
            project=args.project,
            lang=args.lang,
            top_k=args.top_k,
        )
        if args.json:
            print(json.dumps([r.as_dict() for r in results], indent=2))
        else:
            for r in results:
                print(f"[{r.score:.3f}] {r.project}/{r.kind} {r.path}:{r.start_line}-{r.end_line}")
                print(f"        {r.title}")
        return 0

    if cmd == "serve":
        from .server import run_server

        _ensure_knowledge_index(settings)
        run_server(settings)
        return 0

    if cmd == "info":
        from .store import Store

        store = Store(settings)
        info = {
            "data_dir": str(settings.data_dir),
            "corpus_dir": str(settings.corpus_dir),
            "db_path": str(settings.db_path),
            "model": settings.model_name,
            "embed_dim": settings.embed_dim,
            "transport": "stdio",
            "index": store.stats(),
        }
        print(json.dumps(info, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
