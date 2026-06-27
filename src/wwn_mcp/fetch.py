"""Fetch corpus sources declared in ``corpus.toml`` into the corpus cache.

Supported kinds:
  * ``git``        - shallow clone (or fetch/reset if already present)
  * ``web-mirror`` - bounded same-host BFS crawl, stdlib only (HTML/PDF/JSON)
  * ``rustdoc``    - treated as a web-mirror of the docs site
  * ``local``      - no fetch; the indexer reads the path directly

Network/clone failures for a single source are logged and skipped so one bad
upstream never aborts the whole run.
"""

from __future__ import annotations

import shutil
import subprocess
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

from .config import Settings
from .corpus import Source, filter_sources, load_sources, source_root

_UA = "Mozilla/5.0 (compatible; WWN-MCP/0.1; +https://github.com/Wawona/WWN-MCP)"


def fetch_all(settings: Settings, only: list[str] | None = None, depth: int = 1) -> int:
    sources = filter_sources(load_sources(settings.corpus_manifest), only)
    settings.ensure_dirs()
    ok = 0
    for src in sources:
        if not src.enabled:
            print(f"  skip (disabled): {src.name}")
            continue
        try:
            if src.kind == "local":
                root = source_root(settings.corpus_dir, _repo_root(settings), src)
                if not root.exists():
                    print(f"  WARN local source missing: {src.name} -> {root}")
                    continue
                print(f"  local: {src.name} -> {root}")
                ok += 1
            elif src.kind == "git":
                _fetch_git(settings, src, depth)
                ok += 1
            elif src.kind in ("web-mirror", "rustdoc"):
                _fetch_web(settings, src)
                ok += 1
        except Exception as exc:  # noqa: BLE001 - one source must not abort all
            print(f"  ERROR fetching {src.name}: {exc}")
    return ok


def _repo_root(settings: Settings) -> Path:
    return settings.corpus_manifest.parent


def _fetch_git(settings: Settings, src: Source, depth: int) -> None:
    dest = settings.corpus_dir / src.name
    ref = src.ref or "HEAD"
    if (dest / ".git").exists():
        print(f"  git update: {src.name} ({ref})")
        _apply_sparse(dest, src)
        subprocess.run(["git", "-C", str(dest), "fetch", "--depth", str(max(depth, 1)), "origin", ref],
                       check=True)
        subprocess.run(["git", "-C", str(dest), "checkout", "-f", "FETCH_HEAD"], check=True)
        return
    sparse_note = f" [sparse: {', '.join(src.sparse)}]" if src.sparse else ""
    print(f"  git clone: {src.name} <- {src.url} ({ref}){sparse_note}")
    cmd = ["git", "clone", "--filter=blob:none", "--no-checkout"]
    if depth and depth > 0:
        cmd += ["--depth", str(depth), "--branch", ref]
    cmd += [str(src.url), str(dest)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        # --branch fails for raw commit refs; retry without it.
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", str(src.url), str(dest)],
                       check=True)
    _apply_sparse(dest, src)
    subprocess.run(["git", "-C", str(dest), "checkout", "-f", ref], check=False)


def _apply_sparse(dest: Path, src: Source) -> None:
    """Restrict the working tree to `src.sparse` dir prefixes (cone mode)."""
    if not src.sparse:
        return
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "init", "--cone"], check=False)
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", *src.sparse], check=False)


class _LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href and not href.startswith("#") and not href.lower().startswith("javascript:"):
            self.links.append(href.strip())


def _safe_name(url: str) -> str:
    p = urlparse(url)
    path = (p.path or "/").strip("/").replace("/", "_") or "index"
    if not path.endswith((".html", ".pdf", ".json", ".txt", ".xml")):
        path += ".html"
    return path


def _fetch_web(settings: Settings, src: Source) -> None:
    dest = settings.corpus_dir / src.name
    dest.mkdir(parents=True, exist_ok=True)
    seeds = src.seeds or src.all_urls()
    if not seeds:
        return
    base = urlparse(seeds[0])
    base_prefix = f"{base.scheme}://{base.netloc}{base.path.rsplit('/', 1)[0]}"
    max_pages = src.max_pages or 100
    seen: set[str] = set()
    queue: list[str] = list(dict.fromkeys(seeds))
    fetched = 0
    print(f"  web-mirror: {src.name} (<= {max_pages} pages from {base.netloc})")
    while queue and fetched < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            body, ctype = _http_get(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            print(f"    miss {url}: {exc}")
            continue
        (dest / _safe_name(url)).write_bytes(body)
        fetched += 1
        if ctype and "html" in ctype:
            for href in _extract_links(body):
                nxt = urljoin(url, href)
                if nxt.startswith(base_prefix) and nxt not in seen:
                    queue.append(nxt)
        time.sleep(0.2)  # be polite
    print(f"    saved {fetched} page(s) -> {dest}")


def _http_get(url: str) -> tuple[bytes, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read(), resp.headers.get("Content-Type")


def _extract_links(body: bytes) -> list[str]:
    try:
        parser = _LinkExtractor()
        parser.feed(body.decode("utf-8", errors="ignore"))
        return parser.links
    except Exception:  # noqa: BLE001
        return []
