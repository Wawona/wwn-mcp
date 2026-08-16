# Patch-overlay model (all `wwn-*` repos)

Every Wawona patched-software repo follows the same **patch-overlay** pattern:

1. **Pristine upstream** is fetched at build time (pinned tarball/git rev in Nix).
2. **Patch scripts** (`patch-*.py`, `patch-*.sh`) or inline Nix `postPatch` /
   `substituteInPlace` rewrite the extracted source before compile.
3. **Nix recipes** (`ios.nix`, `android.nix`, `macos.nix`, …) cross-compile the
   patched tree for each platform.
4. **CI patch-anchor scripts** (`verify-*-patches.py`) assert the patch scripts
   still apply against the current upstream anchor. No silent drift.

There are **no long-lived source forks** of zsh, Weston, waypipe, etc. in git;
only recipes + patches + pins.

## Registry fragments

`wwn-toolchain` exports `lib.baseRegistry` (common libs + `wawona-pty`).

Each app repo exports `registryFragment`. An attrset of
`withPlatformVariants { ios = ./ios.nix; … }` entries with paths **relative to
that repo's tree**.

Wawona merges:

```nix
registry = wwn-toolchain.lib.baseRegistry
  // wwn-iland.registryFragment
  // wwn-weston.registryFragment
  // …;
```

`callPackageFiltered` resolves sibling `ios.nix` paths inside each input's store
path, so moving recipes out of the monorepo does not break the build graph.

## Finding patches with WWN-MCP

- **`list_patches()`**. Scans `dependencies/` in Wawona + all `wwn-*` corpus
  sources; returns repo-qualified paths.
- **`get_patch("zsh")`**. Resolves by software name (disambiguates if needed).
- **`get_patch("wwn-weston/weston")`**. Repo-qualified lookup.
- **`read_document("wwn-zsh/dependencies/libs/zsh/patches/patch-zsh-exec.py")`**
 . Read the live patch script from the indexed corpus.

## Per-repo patch highlights

| Software | Repo | Key patch artifacts |
|----------|------|---------------------|
| zsh | wwn-zsh | `patch-zsh-exec.py` (no fork/exec on Apple mobile) |
| Weston terminal | wwn-weston | `terminal-patches/patch-terminal.py`, `compositor-apple-mobile.nix` |
| waypipe | wwn-waypipe | `patch-waypipe-source.sh`, `waypipe-patched-src.nix` |
| coreutils | wwn-coreutils | `patch-coreutils-source.sh`, `multicall.nix` |
| iland shims | wwn-iland | upstream/shims/* (not a single patch file. Vendored compat layer) |
| foot | wwn-foot | platform `.nix` recipes + any `patch-*` scripts |
| fastfetch | wwn-fastfetch | `patch-fastfetch-apple-mobile.py`, `apply-wawona-wayland-macos.py` |
