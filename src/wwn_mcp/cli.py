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


_TTY_USAGE = """\
wwn-mcp is a stdio MCP server for AI agents — not an interactive CLI chat.

Running it in a terminal and pressing Enter is not supported: stdin must be
valid newline-delimited JSON-RPC from an MCP host (a blank line is invalid).

It is host-agnostic RAG over stdio. Cursor is one client; also VS Code,
Claude Desktop, Windsurf, Antigravity, Zed, and any other MCP host.

Prefer a PATH binary (fast spawn). Do **not** put `nix run --refresh` in an
MCP host config — eval/build routinely exceeds host initialize timeouts (~60s).

Cursor / VS Code / Claude Desktop / Windsurf (~/.cursor/mcp.json or equivalent):

  {{
    "mcpServers": {{
      "wwn-mcp": {{ "command": "wwn-mcp", "args": [] }}
    }}
  }}

Until installed on PATH (still avoid --refresh):

  {{
    "mcpServers": {{
      "wwn-mcp": {{
        "command": "nix",
        "args": ["run", "github:Wawona/WWN-MCP#wwn-mcp"]
      }}
    }}
  }}

Zed (~/.config/zed/settings.json — key is context_servers; args required):

  {{
    "context_servers": {{
      "wwn-mcp": {{
        "command": "wwn-mcp",
        "args": [],
        "env": {{}}
      }}
    }}
  }}

Install once:  nix profile install github:Wawona/WWN-MCP
               # or:  programs.wwn-mcp.enable = true;  (home-manager)

From a terminal (smoke tests — these print and exit):

  nix run github:Wawona/WWN-MCP#wwn-mcp -- info
  nix run github:Wawona/WWN-MCP#wwn-mcp -- search "watchOS GPU"
  nix run github:Wawona/WWN-MCP#wwn-mcp -- index --knowledge

Force stdio even on a TTY (debug only): WWN_MCP_FORCE_STDIO=1

Docs: https://github.com/Wawona/wwn-mcp#readme
      https://wawona.io/docs/contributor/wwn-mcp/
"""


def _is_interactive_terminal() -> bool:
    """True when a human is typing at a terminal — do not start JSON-RPC.

    MCP hosts (Cursor, Zed, VS Code, …) spawn us with **piped stdin**. A human
    ``nix run …#wwn-mcp`` has stdin as a TTY. Only stdin matters: some hosts
    leave stdout attached to a TTY while stdin is a pipe; treating stdout-only
    as interactive made those hosts print setup help and exit, then time out
    on ``initialize``.
    """
    import os

    if os.environ.get("WWN_MCP_FORCE_STDIO", "").strip() in ("1", "true", "yes"):
        return False
    try:
        return bool(sys.stdin.isatty())
    except Exception:
        return False


def _ensure_knowledge_index_async(settings: Settings) -> None:
    """Index shipped knowledge/ in a daemon thread — never block MCP initialize.

    Zed (and other hosts) abort context servers that do not answer
    ``initialize`` within ~60s. Embedding/model download on a cold DB can
    exceed that, so serve must listen first.
    """
    import threading

    def _run() -> None:
        try:
            _ensure_knowledge_index(settings)
        except Exception as exc:  # pragma: no cover - logged for operators
            print(f"wwn-mcp: background knowledge index failed: {exc}", file=sys.stderr)

    threading.Thread(target=_run, name="wwn-mcp-index", daemon=True).start()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wwn-mcp",
        description=__doc__,
        epilog=(
            "Bare `wwn-mcp` on an interactive terminal prints setup help and exits. "
            "An MCP host (piped stdin+stdout) starts the stdio server."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
        # Interactive terminals are not MCP clients. Print host wiring help
        # instead of blocking on stdin and erroring on a blank Enter/`\n`.
        if _is_interactive_terminal():
            print(_TTY_USAGE.format(), file=sys.stderr)
            print(
                f"data_dir={settings.data_dir}  db={settings.db_path}",
                file=sys.stderr,
            )
            return 0

        from .server import run_server

        # Answer initialize immediately; fill an empty DB in the background.
        _ensure_knowledge_index_async(settings)
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
