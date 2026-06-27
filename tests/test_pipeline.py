"""End-to-end pipeline tests that run without fastembed/sqlite-vec/mcp.

They exercise chunking, the hashing-embedder fallback, the FTS5 +
brute-force hybrid store, incremental indexing, the patch inventory, and the
Wayland protocol chunker.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
import sys

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


PROTOCOL_XML = """<?xml version="1.0"?>
<protocol name="demo_shell">
  <interface name="demo_surface" version="2">
    <description summary="a demo surface">A surface for testing.</description>
    <request name="commit"><description summary="commit pending state"/></request>
    <event name="configure"><description summary="suggest a size"/></event>
    <enum name="error"><entry name="bad" value="0"/></enum>
  </interface>
</protocol>
"""


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    """A tiny fake corpus + a fake dependencies tree, with a manifest."""
    repo = tmp_path / "repo"
    corpus_src = repo / "corpus_src"
    (corpus_src / "dependencies" / "libs" / "foo").mkdir(parents=True)
    (corpus_src / "docs").mkdir(parents=True)

    (corpus_src / "docs" / "guide.md").write_text(
        "# Liquid Glass\nLiquid glass is the OS 26 material.\n\n## Details\nMore text here.\n"
    )
    (corpus_src / "demo.rs").write_text(
        "pub fn alpha() -> u32 { 1 }\n\npub struct Beta { x: u32 }\n\nimpl Beta { pub fn go(&self) {} }\n"
    )
    (corpus_src / "demo.xml").write_text(PROTOCOL_XML)
    foo = corpus_src / "dependencies" / "libs" / "foo"
    (foo / "ios.nix").write_text('stdenv.mkDerivation { postPatch = "substituteInPlace x"; }\n')
    (foo / "patch-foo-source.sh").write_text("#!/bin/sh\necho patch\n")

    manifest = repo / "corpus.toml"
    manifest.write_text(
        f"""
[[source]]
name = "wawona"
project = "wawona"
kind = "local"
path = "{corpus_src.as_posix()}"
include = ["**/*.md", "**/*.rs", "**/*.xml", "dependencies/**/*.nix", "dependencies/**/*.sh"]
license = "MIT"
"""
    )
    os.environ["WWN_MCP_DATA_DIR"] = str(tmp_path / "data")
    os.environ["WWN_MCP_CORPUS_TOML"] = str(manifest)
    # ensure local source resolves relative to the manifest's repo root
    return repo


def test_embedder_fallback_dimension():
    from wwn_mcp.embed import Embedder

    emb = Embedder("BAAI/bge-small-en-v1.5", 384)
    v = emb.embed_one("hello world")
    assert len(v) == 384
    assert abs(sum(x * x for x in v) - 1.0) < 1e-3  # L2-normalized (hashing path)


def test_index_and_search(project: Path):
    from wwn_mcp.config import Settings
    from wwn_mcp.index import build_index
    from wwn_mcp.store import Store

    settings = Settings.load()
    settings.ensure_dirs()
    stats = build_index(settings)
    totals = stats["totals"]
    assert totals["chunks"] > 0
    assert "docs" in totals["by_kind"]
    assert "code" in totals["by_kind"]
    assert "protocol" in totals["by_kind"]

    store = Store(settings)
    res = store.search("liquid glass", kind="docs", top_k=5)
    assert res, "expected a docs hit for 'liquid glass'"
    assert res[0].url is None or isinstance(res[0].url, str)
    assert res[0].citation()


def test_incremental_reindex(project: Path):
    from wwn_mcp.config import Settings
    from wwn_mcp.index import build_index

    settings = Settings.load()
    settings.ensure_dirs()
    build_index(settings)
    second = build_index(settings)
    w = second["sources"]["wawona"]
    assert w["added"] == 0 and w["changed"] == 0
    assert w["unchanged"] > 0


def test_protocol_chunking(project: Path):
    from wwn_mcp.config import Settings
    from wwn_mcp.index import build_index
    from wwn_mcp.store import Store

    settings = Settings.load()
    settings.ensure_dirs()
    build_index(settings)
    store = Store(settings)
    protos = store.list_protocols()
    assert any(p["protocol"] == "demo_shell" for p in protos)
    chunks = store.get_protocol("demo_surface")
    assert chunks and "commit" in chunks[0].text


def test_patch_inventory(project: Path):
    from wwn_mcp.config import Settings
    from wwn_mcp.corpus import load_sources
    from wwn_mcp.patches import generate_inventory

    settings = Settings.load()
    settings.ensure_dirs()
    inv = generate_inventory(settings, load_sources(settings.corpus_manifest))
    assert inv["count"] >= 1
    foo = inv["entries"].get("libs/foo")
    assert foo is not None
    assert any("patch-foo-source.sh" in p for p in foo["patch_files"])
    assert any("ios.nix" in p for p in foo["inline_patches"])
    assert "ios" in foo["platforms"]
