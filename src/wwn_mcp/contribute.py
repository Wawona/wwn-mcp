"""Contributor helpers: repo catalog, where-to-edit, capability gates.

Data mirrors ``knowledge/wawona/`` so tools answer even before a full corpus
index. Keep in sync with ``Wawona/docs/wwn-repo-dag.md`` and platform rules.
"""

from __future__ import annotations

import re
from typing import Any

# L0-L4 catalog (stdio RAG; not a flake input graph).
_REPOS: list[dict[str, Any]] = [
    {
        "repo": "wwn-toolchain",
        "layer": "L0",
        "role": "Cross-builders + substrate (cairo/pango/pixman/libwayland/…)",
        "when": "substrate libs, mkToolchains, baseRegistry, wawona-pty",
        "project": "wawona",
    },
    {
        "repo": "wwn-iland",
        "layer": "L1",
        "role": "Complete graphics stack (iland, ANGLE, SwiftShader, MoltenVK, KosmicKrisp)",
        "when": "DRM/KMS/GBM/EGL, ANGLE, ICDs, Mode A/B dylib",
        "project": "iland",
    },
    {
        "repo": "wwn-kmscube",
        "layer": "L2",
        "role": "Graphics acceptance clients",
        "when": "kmscube / GL acceptance against iland",
        "project": "kmscube",
    },
    {
        "repo": "wwn-weston",
        "layer": "L3",
        "role": "Weston nested compositor + clients",
        "when": "weston patches, apple-mobile compositor, weston-simple-shm",
        "project": "weston",
    },
    {
        "repo": "wwn-niri",
        "layer": "L3",
        "role": "Niri nested compositor (mandatory bundle on every target)",
        "when": "niri recipe, niri_main, compositor backend",
        "project": "niri",
    },
    {
        "repo": "wwn-waypipe",
        "layer": "L3'",
        "role": "waypipe-rs remote streaming",
        "when": "waypipe patches, remote display",
        "project": "waypipe",
    },
    {
        "repo": "Wawona-Swinging-Bridge",
        "layer": "L3'",
        "role": "Wawona Swinging Bridge: host apps to Wayland (not Desktop/LockScreen)",
        "when": "Swinging Bridge, Cocoa/Android/UIKit as Wayland clients, waypipe to Linux",
        "project": "swinging-bridge",
    },
    {
        "repo": "wwn-vms",
        "layer": "L3'",
        "role": "VM machine kinds (planned)",
        "when": "virtual_machine profiles / engines",
        "project": "vms",
    },
    {
        "repo": "wwn-containers",
        "layer": "L3'",
        "role": "Container machine kinds (planned)",
        "when": "container profiles / engines",
        "project": "containers",
    },
    {
        "repo": "wwn-ssh",
        "layer": "L3'",
        "role": "SSH / libssh2 vs OpenSSH split",
        "when": "remote SSH, Apple-mobile libssh2, macOS OpenSSH",
        "project": "ssh",
    },
    {
        "repo": "wwn-iowatchdog",
        "layer": "L3'",
        "role": "macOS IOWatchdog Path B tools (Desktop Mode B; nixpkgs-only)",
        "when": "claim-ok, Path B, wwn-iowatchdog status/doctor, never unload watchdogd without ACK",
        "project": "wawona",
    },
    {
        "repo": "wwn-igetty",
        "layer": "L3'",
        "role": "Session switching: macOS Classic VTs, iOS TrollStore logical zsh PTYs",
        "when": "igettyd, F1-F9, DesktopReplacementGuiVt, iOS Mode B zsh PTYs",
        "project": "wawona",
    },
    {
        "repo": "wwn-zsh",
        "layer": "L3'",
        "role": "In-process App Store zsh + RootFS",
        "when": "zsh patches, RootFS, wawona_zsh_main",
        "project": "wawona",
    },
    {
        "repo": "wwn-coreutils",
        "layer": "L3'",
        "role": "uutils coreutils in-process multicall",
        "when": "coreutils patches / dispatch",
        "project": "coreutils",
    },
    {
        "repo": "wwn-foot",
        "layer": "L3'",
        "role": "foot terminal port",
        "when": "foot patches / recipes",
        "project": "wawona",
    },
    {
        "repo": "wwn-fastfetch",
        "layer": "L3'",
        "role": "fastfetch port",
        "when": "fastfetch patches / in-process main",
        "project": "wawona",
    },
    {
        "repo": "wwn-neovim",
        "layer": "L3'",
        "role": "neovim port / optional module",
        "when": "neovim patches / App Store module",
        "project": "neovim",
    },
    {
        "repo": "wwn-phoon-rs",
        "layer": "L3'",
        "role": "phoon-rs client",
        "when": "phoon recipe / client",
        "project": "wawona",
    },
    {
        "repo": "wwn-apt",
        "layer": "L3'",
        "role": "App Store apt module catalog (StoreKit + ODR)",
        "when": "optional modules, apt CLI, catalog firewall",
        "project": "wawona",
    },
    {
        "repo": "wwn-mcp",
        "layer": "tooling",
        "role": "Local-embeddings RAG + MCP (stdio)",
        "when": "corpus, knowledge mirrors, MCP tools",
        "project": "wawona",
    },
    {
        "repo": "Wawona",
        "layer": "L4",
        "role": "Product integration (Smithay, apps, flake merge)",
        "when": "Machines UI, SwiftUI/Android, xcodegen, product packaging",
        "project": "wawona",
    },
    {
        "repo": "wawona.io",
        "layer": "docs",
        "role": "Public website / contributor docs",
        "when": "public docs, download, FAQ",
        "project": "wawona",
    },
    {
        "repo": "repo.wawona.io",
        "layer": "docs",
        "role": "Dual catalog host: store wasm (/wasm/v1) plus APT debs (Sileo iOS jailbreak and Termux Android sideload)",
        "when": "human /search/ catalogs, wasm index.json, Packages, jailbreak landing, termux landing",
        "project": "wawona",
    },
]

_WHERE: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"zsh|rootfs", re.I), "wwn-zsh", "zsh / RootFS patches live in wwn-zsh"),
    (re.compile(r"angle|swiftshader|moltenvk|kosmickrisp|iland|drm|kms|gbm|egl|iomfb", re.I),
     "wwn-iland", "Graphics stack ownership is L1 wwn-iland"),
    (re.compile(r"kmscube", re.I), "wwn-kmscube", "L2 acceptance client"),
    (re.compile(r"weston", re.I), "wwn-weston", "Weston ports and patches"),
    (re.compile(r"niri", re.I), "wwn-niri", "Niri compositor recipe"),
    (re.compile(r"waypipe", re.I), "wwn-waypipe", "waypipe-rs port"),
    (re.compile(r"anowaw|swinging.?bridge", re.I), "Wawona-Swinging-Bridge", "Swinging Bridge (not Desktop)"),
    (re.compile(r"iowatchdog|watchdogd|claim-ok|path.?b", re.I),
     "wwn-iowatchdog", "macOS IOWatchdog Path B (Desktop Mode B; never lldb watchdogd)"),
    (re.compile(r"igetty|igettyd|doorman", re.I),
     "wwn-igetty", "macOS Classic VTs or iOS TrollStore logical zsh PTYs"),
    (re.compile(r"desktop.?replacement|take.?over|keep.?ws|libwayland-mac|trollstore|mode.?b.?tipa", re.I),
     "Wawona", "Desktop Replacement (macOS helper or iOS TrollStore tipa)"),
    (re.compile(r"\bvm\b|virtual.?machine", re.I), "wwn-vms", "VM machine kinds"),
    (re.compile(r"container", re.I), "wwn-containers", "Container machine kinds"),
    (re.compile(r"ssh|libssh2|openssh", re.I), "wwn-ssh", "SSH backend split"),
    (re.compile(r"coreutils|uutils", re.I), "wwn-coreutils", "coreutils in-process"),
    (re.compile(r"\bfoot\b", re.I), "wwn-foot", "foot terminal"),
    (re.compile(r"fastfetch", re.I), "wwn-fastfetch", "fastfetch port"),
    (re.compile(r"neovim|nvim", re.I), "wwn-neovim", "neovim port"),
    (re.compile(r"phoon", re.I), "wwn-phoon-rs", "phoon-rs"),
    (re.compile(r"\bapt\b|storekit|odr", re.I), "wwn-apt", "App Store module catalog"),
    (re.compile(r"cairo|pango|pixman|fontconfig|harfbuzz|libwayland|toolchain|wawona-pty", re.I),
     "wwn-toolchain", "L0 substrate / toolchain"),
    (re.compile(r"machine|swiftui|xcodegen|android.?ui|smithay|compositor.?core", re.I),
     "Wawona", "L4 product integration"),
    (re.compile(r"mcp|rag|corpus|knowledge", re.I), "wwn-mcp", "This RAG server"),
    (re.compile(
        r"repo\.wawona\.io|sileo|termux|/wasm/v1|/search/\?channel|(wasm|deb) catalog",
        re.I,
    ), "repo.wawona.io", "Dual catalog host: wasm for stores; Sileo iOS jailbreak debs and Termux Android sideload debs. APT at repo root."),
    (re.compile(r"\bwpm\b", re.I), "wwn-wasm", "Wawona Runtime package client"),
    (re.compile(r"website|(?<!repo\.)wawona\.io|docs.?site", re.I), "wawona.io", "Public site"),
]

# platform → feature → state (available|planned|blocked|forbidden)
_CAPS: dict[str, dict[str, str]] = {
    "macos": {
        "native": "available", "remote": "available", "vm": "planned", "container": "planned",
        "multi_window": "available", "nested_compositors": "available", "gpu": "available",
        "desktop": "planned", "swinging_bridge": "planned",
    },
    "android": {
        "native": "available", "remote": "available", "vm": "planned", "container": "planned",
        "multi_window": "available", "nested_compositors": "available", "gpu": "available",
        "desktop": "planned", "swinging_bridge": "planned",
    },
    "ios": {
        "native": "available", "remote": "available", "vm": "planned", "container": "planned",
        "multi_window": "available", "nested_compositors": "available", "gpu": "available",
        "desktop": "forbidden", "swinging_bridge": "forbidden",
    },
    "ipados": {
        "native": "available", "remote": "available", "vm": "planned", "container": "planned",
        "multi_window": "available", "nested_compositors": "available", "gpu": "available",
        "desktop": "forbidden", "swinging_bridge": "forbidden",
    },
    "visionos": {
        "native": "available", "remote": "available", "vm": "planned", "container": "planned",
        "multi_window": "available", "nested_compositors": "available", "gpu": "available",
        "desktop": "forbidden", "swinging_bridge": "forbidden",
    },
    "tvos": {
        "native": "available", "remote": "available", "vm": "forbidden", "container": "forbidden",
        "multi_window": "forbidden", "nested_compositors": "available", "gpu": "planned",
        "desktop": "forbidden", "swinging_bridge": "forbidden",
    },
    "watchos": {
        "native": "available", "remote": "available", "vm": "forbidden", "container": "forbidden",
        "multi_window": "forbidden", "nested_compositors": "available", "gpu": "blocked",
        "desktop": "forbidden", "swinging_bridge": "forbidden",
    },
    "linux": {
        "native": "available", "remote": "available", "vm": "planned", "container": "planned",
        "multi_window": "available", "nested_compositors": "available", "gpu": "available",
        "desktop": "forbidden", "swinging_bridge": "forbidden",
    },
}

# Extra prose on a gate that agents otherwise treat as "not implemented".
_CAP_NOTES: dict[tuple[str, str], str] = {
    ("macos", "desktop"): (
        "Product gate stays planned until LockScreen/greeter. Classic Take Over "
        "is implemented on .#wawona-macos-desktop-host (SIP fully disabled; "
        "Enable arms Path B; Replace now takes over). See knowledge/wawona/"
        "desktop-replacement-macos.md."
    ),
    ("android", "desktop"): (
        "Still planned: Default Home + LockScreen APIs. No root. Not the macOS dylib."
    ),
    ("ios", "desktop"): (
        "Forbidden in the App Store IPA. Current Mode B product is the "
        "TrollStore tipa com.aspauldingcode.Wawona.ModeB (IOMFB Desktop, "
        "JIT QEMU, container-in-VM, Wawona zsh PTYs). Sileo/Doorman/ElleKit "
        "and Wasm JIT are deferred, not the current Desktop path."
    ),
    ("ipados", "desktop"): (
        "Forbidden in the App Store IPA. Current Mode B product is the "
        "TrollStore tipa com.aspauldingcode.Wawona.ModeB (IOMFB Desktop, "
        "JIT QEMU, container-in-VM, Wawona zsh PTYs). Sileo/Doorman/ElleKit "
        "and Wasm JIT are deferred, not the current Desktop path."
    ),
    ("ios", "swinging_bridge"): (
        "Forbidden in App Store IPA. Mode B only via repo.wawona.io / jailbreak."
    ),
    ("ipados", "swinging_bridge"): (
        "Forbidden in App Store IPA. Mode B only via repo.wawona.io / jailbreak."
    ),
}

_FEATURE_ALIASES = {
    "vms": "vm",
    "virtual_machine": "vm",
    "containers": "container",
    "multi-window": "multi_window",
    "nested": "nested_compositors",
    "vulkan": "gpu",
    "opengl": "gpu",
    "angle": "gpu",
    "lockscreen": "desktop",
    "desktop_replacement": "desktop",
    "anowaw": "swinging_bridge",
    "anowaW": "swinging_bridge",
    "swinging-bridge": "swinging_bridge",
}


def list_repos() -> list[dict[str, Any]]:
    return list(_REPOS)


def where_to_edit(change: str) -> dict[str, Any]:
    change = (change or "").strip()
    if not change:
        return {"error": "empty change description", "repos": [r["repo"] for r in _REPOS]}
    matches = []
    for pat, repo, note in _WHERE:
        if pat.search(change):
            matches.append({"repo": repo, "note": note})
    if not matches:
        return {
            "repo": "Wawona",
            "note": "No specific match; default to L4 integration. Refine the query.",
            "matches": [],
            "hint": "Try: zsh, ANGLE, niri, weston, Machines UI, waypipe, Swinging Bridge, igetty, iowatchdog",
        }
    primary = matches[0]
    return {"repo": primary["repo"], "note": primary["note"], "matches": matches}


def get_capability(platform: str, feature: str) -> dict[str, Any]:
    plat = (platform or "").strip().lower().replace(" ", "")
    feat = (feature or "").strip().lower().replace(" ", "_")
    feat = _FEATURE_ALIASES.get(feat, feat)
    if plat == "iphone":
        plat = "ios"
    if plat == "ipad":
        plat = "ipados"
    row = _CAPS.get(plat)
    if row is None:
        return {
            "error": f"unknown platform '{platform}'",
            "platforms": sorted(_CAPS.keys()),
        }
    if feat not in row:
        return {
            "error": f"unknown feature '{feature}'",
            "features": sorted(row.keys()),
            "platform": plat,
        }
    state = row[feat]
    legend = {
        "available": "Shipping. Keep green.",
        "planned": "Platform allows it; our work unfinished. Finish it.",
        "blocked": "No public platform API. Re-check on SDK bumps; no private API.",
        "forbidden": "Product/store policy. Never enable.",
    }
    out = {
        "platform": plat,
        "feature": feat,
        "state": state,
        "meaning": legend.get(state, state),
    }
    note = _CAP_NOTES.get((plat, feat))
    if note:
        out["note"] = note
    return out
