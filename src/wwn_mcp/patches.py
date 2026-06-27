"""Patched-software inventory.

Scans the Wawona ``dependencies/`` tree for patch artifacts (``*.patch``,
``patch-*.{sh,py}``, ``*-patched-src.nix``, ``Cargo.lock.patched``) and inline
``postPatch``/``substituteInPlace`` edits, grouping them by software so the MCP
can answer "how is <upstream> patched for Apple/Android?" via
``list_patches`` / ``get_patch``. Generated build output is excluded.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Settings
from .corpus import Source, source_root

_PATCH_FILE_RE = re.compile(r"(\.patch$|^patch-.*\.(sh|py)$|-patched-src\.nix$|Cargo\.lock\.patched$)")
_INLINE_RE = re.compile(r"\b(postPatch|prePatch|patchPhase|substituteInPlace|patches\s*=)\b")
_PLATFORM_RE = re.compile(
    r"\b(ios|ipados|tvos|watchos|visionos|macos|android|wearos|linux)\b", re.IGNORECASE
)
_EXCLUDE = "dependencies/generators/gradlegen/output/"


def _wawona_root(settings: Settings, sources: list[Source]) -> Path | None:
    for s in sources:
        if s.project == "wawona" and s.kind == "local":
            root = source_root(settings.corpus_dir, settings.corpus_manifest.parent, s)
            if root.exists():
                return root
    # fallback: fetched git checkout
    cand = settings.corpus_dir / "wawona-git"
    return cand if cand.exists() else None


def _software_key(rel: str) -> str | None:
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "dependencies" and parts[1] in ("libs", "clients"):
        return f"{parts[1]}/{parts[2]}"
    return None


def generate_inventory(settings: Settings, sources: list[Source]) -> dict:
    root = _wawona_root(settings, sources)
    if root is None:
        return {"count": 0, "entries": {}}
    deps = root / "dependencies"
    if not deps.exists():
        return {"count": 0, "entries": {}}

    entries: dict[str, dict] = {}

    def ensure(key: str) -> dict:
        return entries.setdefault(
            key,
            {
                "software": key,
                "category": key.split("/")[0],
                "name": key.split("/")[1],
                "platforms": set(),
                "patch_files": [],
                "inline_patches": [],
                "recipes": [],
            },
        )

    for p in deps.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if _EXCLUDE in rel:
            continue
        key = _software_key(rel)
        if key is None:
            continue
        e = ensure(key)
        plat = _PLATFORM_RE.search(p.stem)
        if plat:
            e["platforms"].add(plat.group(1).lower())
        if p.suffix == ".nix":
            e["recipes"].append(rel)
        if _PATCH_FILE_RE.search(p.name):
            e["patch_files"].append(rel)
        elif p.suffix == ".nix":
            try:
                if _INLINE_RE.search(p.read_text(encoding="utf-8", errors="ignore")):
                    e["inline_patches"].append(rel)
            except OSError:
                pass

    # Keep only software that is actually patched.
    patched = {
        k: {**v, "platforms": sorted(v["platforms"])}
        for k, v in entries.items()
        if v["patch_files"] or v["inline_patches"]
    }
    out = {"count": len(patched), "entries": patched}
    inv_path = settings.data_dir / "patch_inventory.json"
    inv_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def load_inventory(settings: Settings) -> dict:
    inv_path = settings.data_dir / "patch_inventory.json"
    if inv_path.exists():
        try:
            return json.loads(inv_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"count": 0, "entries": {}}
