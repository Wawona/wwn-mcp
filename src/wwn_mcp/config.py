"""Runtime configuration and filesystem layout for WWN-MCP.

All paths default under a single data dir (``$WWN_MCP_DATA_DIR`` or
``./data``) so the server is hermetic and the runtime artifacts are easy to
``.gitignore``. Nothing here is committed to the repo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_EMBED_DIM = 384  # bge-small-en-v1.5 / hashing-fallback dimension


def _env_path(name: str, default: Path) -> Path:
    val = os.environ.get(name)
    return Path(val).expanduser().resolve() if val else default


def repo_root() -> Path:
    """Directory of the installed package's repo root (best effort)."""
    return Path(__file__).resolve().parents[2]


def default_data_dir() -> Path:
    """Writable runtime dir.

    Prefer an XDG location so an installed (e.g. Nix-store, read-only) package
    works out of the box. Fall back to ``./data`` only for an editable checkout
    whose repo root is actually writable.
    """
    rr = repo_root()
    if (rr / "corpus.toml").exists() and os.access(rr, os.W_OK):
        return rr / "data"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "share"
    return base / "wwn-mcp"


def find_manifest() -> Path:
    """Locate ``corpus.toml``: env override, packaged copy, then dev checkout."""
    env = os.environ.get("WWN_MCP_CORPUS_TOML")
    if env:
        return Path(env).expanduser().resolve()
    packaged = Path(__file__).resolve().parent / "corpus.toml"
    if packaged.exists():
        return packaged
    return repo_root() / "corpus.toml"


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    corpus_dir: Path
    db_path: Path
    model_name: str
    embed_dim: int
    host: str
    port: int
    token: str | None
    corpus_manifest: Path

    @staticmethod
    def load() -> Settings:
        data_dir = _env_path("WWN_MCP_DATA_DIR", default_data_dir())
        corpus_dir = _env_path("WWN_MCP_CORPUS_DIR", data_dir / "corpus")
        db_path = _env_path("WWN_MCP_DB", data_dir / "index.sqlite")
        manifest = find_manifest()
        return Settings(
            data_dir=data_dir,
            corpus_dir=corpus_dir,
            db_path=db_path,
            model_name=os.environ.get("WWN_MCP_MODEL", DEFAULT_MODEL),
            embed_dim=int(os.environ.get("WWN_MCP_EMBED_DIM", DEFAULT_EMBED_DIM)),
            host=os.environ.get("WWN_MCP_HOST", DEFAULT_HOST),
            port=int(os.environ.get("WWN_MCP_PORT", DEFAULT_PORT)),
            token=os.environ.get("WWN_MCP_TOKEN") or None,
            corpus_manifest=manifest,
        )

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
