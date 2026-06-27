"""``wwn-mcp`` command-line entry point: fetch | index | search | serve."""

from __future__ import annotations

import argparse
import json
import sys

from .config import Settings


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
    sub = p.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="Mirror/clone corpus sources from corpus.toml.")
    _add_only(p_fetch)
    p_fetch.add_argument("--depth", type=int, default=1, help="git shallow clone depth (0=full).")

    p_index = sub.add_parser("index", help="Chunk + embed the fetched corpus into the index.")
    _add_only(p_index)
    p_index.add_argument("--reset", action="store_true", help="Drop and rebuild the index.")

    p_search = sub.add_parser("search", help="Query the hybrid index from the terminal.")
    p_search.add_argument("query")
    p_search.add_argument("--kind", default=None, help="docs|code|symbol|protocol|patch")
    p_search.add_argument("--project", default=None)
    p_search.add_argument("--lang", default=None)
    p_search.add_argument("-k", "--top-k", type=int, default=8)
    p_search.add_argument("--json", action="store_true")

    p_serve = sub.add_parser("serve", help="Start the MCP server.")
    p_serve.add_argument("--host", default=None)
    p_serve.add_argument("--port", type=int, default=None)
    p_serve.add_argument(
        "--transport",
        choices=["http", "stdio"],
        default="http",
        help="http = Streamable HTTP (default); stdio = local Cursor stdio.",
    )

    sub.add_parser("info", help="Print resolved settings and index status.")
    return p


def _settings(args: argparse.Namespace) -> Settings:
    import os

    if args.data_dir:
        os.environ["WWN_MCP_DATA_DIR"] = args.data_dir
    return Settings.load()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = _settings(args)
    settings.ensure_dirs()

    if args.cmd == "fetch":
        from .fetch import fetch_all

        n = fetch_all(settings, only=args.only, depth=args.depth)
        print(f"fetched/updated {n} source(s) into {settings.corpus_dir}")
        return 0

    if args.cmd == "index":
        from .index import build_index

        stats = build_index(settings, only=args.only, reset=args.reset)
        print(json.dumps(stats, indent=2))
        return 0

    if args.cmd == "search":
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

    if args.cmd == "serve":
        from .server import run_server

        run_server(
            settings,
            host=args.host or settings.host,
            port=args.port or settings.port,
            transport=args.transport,
        )
        return 0

    if args.cmd == "info":
        from .store import Store

        store = Store(settings)
        info = {
            "data_dir": str(settings.data_dir),
            "corpus_dir": str(settings.corpus_dir),
            "db_path": str(settings.db_path),
            "model": settings.model_name,
            "embed_dim": settings.embed_dim,
            "auth": "bearer" if settings.token else "none",
            "index": store.stats(),
        }
        print(json.dumps(info, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
