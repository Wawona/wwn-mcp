"""Patched-software inventory across the Wawona org.

Scans ``dependencies/`` trees in the Wawona integration repo and every ``wwn-*``
patched-software flake repo (zsh, weston, iland, waypipe, coreutils, foot,
toolchain) for patch artifacts (``*.patch``, ``patch-*.{sh,py}``,
``*-patched-src.nix``, ``Cargo.lock.patched``) and inline ``postPatch`` /
``substituteInPlace`` edits. Answers ``list_patches`` / ``get_patch`` with
repo-qualified paths like ``wwn-zsh/dependencies/libs/zsh/ios.nix``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Settings
from .corpus import Source, source_root

_PATCH_FILE_RE = re.compile(
    r"(\.patch$|^patch-.*\.(sh|py)$|-patched-src\.nix$|Cargo\.lock\.patched$)"
)
_INLINE_RE = re.compile(
    r"\b(postPatch|prePatch|patchPhase|substituteInPlace|patches\s*=)\b"
)
_PLATFORM_RE = re.compile(
    r"\b(ios|ipados|tvos|watchos|visionos|macos|android|wearos|linux)\b",
    re.IGNORECASE,
)
_EXCLUDE = "dependencies/generators/gradlegen/output/"

# Corpus source names whose checkouts contain Wawona patch-overlay recipes.
_PATCH_SOURCE_NAMES = frozenset({
    "wawona",
    "wawona-git",
    "wwn-toolchain",
    "wwn-zsh",
    "wwn-weston",
    "wwn-iland",
    "wwn-waypipe",
    "wwn-coreutils",
    "wwn-foot",
    "wwn-fastfetch",
})


def _patch_roots(settings: Settings, sources: list[Source]) -> list[tuple[str, Path]]:
    """Return ``(repo_name, root_path)`` for each source that has ``dependencies/``."""
    manifest_parent = settings.corpus_manifest.parent
    out: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for source in sources:
        if source.name not in _PATCH_SOURCE_NAMES:
            continue
        candidates: list[Path] = [source_root(settings.corpus_dir, manifest_parent, source)]
        # Dev fallback: sibling org checkout at ~/Wawona/<repo> next to WWN-MCP
        # when the git mirror has not been fetched into the corpus cache yet.
        if source.kind == "git":
            candidates.append((manifest_parent / ".." / source.name).resolve())
        elif source.name == "wawona":
            candidates.append((manifest_parent / ".." / "Wawona").resolve())
        elif source.name == "wawona-git":
            candidates.append((manifest_parent / ".." / "Wawona").resolve())
        for root in candidates:
            if root in seen or not root.exists():
                continue
            if (root / "dependencies").is_dir():
                seen.add(root)
                out.append((source.name.removesuffix("-git"), root))
                break
    return out


def _software_key(rel: str) -> str | None:
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "dependencies" and parts[1] in ("libs", "clients", "wawona"):
        return f"{parts[1]}/{parts[2]}"
    return None


def _scan_tree(repo: str, root: Path) -> dict[str, dict]:
    deps = root / "dependencies"
    entries: dict[str, dict] = {}

    def ensure(key: str) -> dict:
        category, name = key.split("/", 1)
        full_key = f"{repo}/{key}"
        return entries.setdefault(
            full_key,
            {
                "repo": repo,
                "key": full_key,
                "software": key,
                "category": category,
                "name": name,
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
        qualified = f"{repo}/{rel}"
        if p.suffix == ".nix":
            e["recipes"].append(qualified)
        if _PATCH_FILE_RE.search(p.name):
            e["patch_files"].append(qualified)
        elif p.suffix == ".nix":
            try:
                if _INLINE_RE.search(p.read_text(encoding="utf-8", errors="ignore")):
                    e["inline_patches"].append(qualified)
            except OSError:
                pass

    return entries


def generate_inventory(settings: Settings, sources: list[Source]) -> dict:
    entries: dict[str, dict] = {}
    for repo, root in _patch_roots(settings, sources):
        entries.update(_scan_tree(repo, root))

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


def resolve_patch(entries: dict[str, dict], software: str) -> dict | None:
    """Look up one patch entry by repo-qualified or short name."""
    if software in entries:
        return entries[software]

    # repo/name shorthand, e.g. wwn-zsh/zsh
    if "/" in software and not software.startswith(("libs/", "clients/", "wawona/")):
        repo, tail = software.split("/", 1)
        for _key, entry in entries.items():
            if entry["repo"] == repo and entry["name"] == tail:
                return entry
            if entry["repo"] == repo and entry["software"] == tail:
                return entry

    matches = [
        e for e in entries.values()
        if software in (e["name"], e["software"], e["key"])
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return {
            "ambiguous": True,
            "software": software,
            "matches": [
                {
                    "repo": m["repo"],
                    "key": m["key"],
                    "name": m["name"],
                    "platforms": m["platforms"],
                }
                for m in matches
            ],
        }
    return None
