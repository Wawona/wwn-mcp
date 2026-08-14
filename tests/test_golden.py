"""Golden retrieval / contributor-tool tests (no network).

Indexes shipped knowledge/ into a temp DB and checks that architecture /
capability questions land on the right projects and tool answers.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
import sys

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture()
def knowledge_index(tmp_path: Path):
    os.environ["WWN_MCP_DATA_DIR"] = str(tmp_path / "data")
    os.environ["WWN_MCP_CORPUS_TOML"] = str(REPO / "corpus.toml")
    from wwn_mcp.config import Settings
    from wwn_mcp.index import build_index

    settings = Settings.load()
    settings.ensure_dirs()
    stats = build_index(
        settings,
        only=["wwn-knowledge", "wwn-knowledge-wawona"],
        reset=True,
    )
    assert stats["totals"]["chunks"] > 0
    return settings


def test_contribute_capability_gates():
    from wwn_mcp.contribute import get_capability, where_to_edit, list_repos

    assert get_capability("watchos", "gpu")["state"] == "blocked"
    assert get_capability("tvos", "gpu")["state"] == "planned"
    assert get_capability("visionos", "vm")["state"] == "forbidden"
    assert get_capability("ios", "anowaw")["state"] == "planned"
    assert get_capability("ipados", "anowaw")["state"] == "planned"
    assert where_to_edit("ANGLE ownership")["repo"] == "wwn-iland"
    assert where_to_edit("niri recipe")["repo"] == "wwn-niri"
    assert where_to_edit("zsh patch")["repo"] == "wwn-zsh"
    repos = {r["repo"] for r in list_repos()}
    assert "wwn-niri" in repos and "wwn-kmscube" in repos and "Wawona" in repos


def test_golden_knowledge_search(knowledge_index):
    from wwn_mcp.store import Store

    store = Store(knowledge_index)

    cases = [
        ("repo DAG L0 toolchain", "wawona"),
        ("watchOS GPU blocked", "wawona"),
        ("visionOS VMs forbidden", "wawona"),
        ("who owns ANGLE", "wawona"),
        ("kmscube must not depend on weston", "wawona"),
        ("waypipe equivalence port fidelity", "wawona"),
        ("anowaW is not Desktop", "wawona"),
        ("Mode A libiland_userland", "wawona"),
        ("contribute development branch", "wawona"),
        ("four-state capability gate planned blocked", "wawona"),
    ]
    for query, project in cases:
        hits = store.search(query, kind="docs", project=project, top_k=5)
        assert hits, f"no hits for {query!r}"
        # At least one hit should be curated knowledge
        paths = " ".join(h.path for h in hits)
        assert any(
            x in paths
            for x in (
                "knowledge",
                "wwn-repo-dag",
                "platform-capability",
                "contribute",
                "iland-mode",
                "multi-repo",
                "wwn-repos-catalog",
                "wwn-iland-graphics",
            )
        ), f"unexpected paths for {query!r}: {paths}"


def test_cli_bare_defaults_to_serve_help():
    from wwn_mcp.cli import build_parser

    p = build_parser()
    ns = p.parse_args([])
    assert ns.cmd is None  # main() treats None as serve


def test_cli_serve_on_tty_prints_usage(tmp_path, monkeypatch, capsys):
    """Interactive `wwn-mcp` must not start JSON-RPC; print Cursor wiring instead."""
    import wwn_mcp.cli as cli

    monkeypatch.setenv("WWN_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)

    rc = cli.main([])
    assert rc == 0
    err = capsys.readouterr().err
    assert "stdio MCP server for Cursor" in err
    assert "mcpServers" in err
    assert "wwn-mcp -- info" in err or "#wwn-mcp -- info" in err
