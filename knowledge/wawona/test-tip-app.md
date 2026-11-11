# Tip Wawona app freshness (all platforms)

Never dogfood a morning `/tmp/wawona-*-tip` after afternoon `Sources/` edits.
Binary mtime is not a freshness check.

## Contract

Tip roots store:

- `git-HEAD` — commit when the tip was last built
- `product-FP` — sha256 of product-path index + dirty diffs

Product paths: `Sources/`, `src/`, `Darwin/`, `Cargo.toml`, `Cargo.lock`,
`Package.swift`, `dependencies/`, `deps.nix`, `flake.nix`, `flake.lock`,
`VERSION`.

Check: `cargo xtask tip <platform> --check` (`xtask/src/tip.rs` writes and reads the stamps).

## Tip commands

| Host | Command |
|------|---------|
| macOS | `eval "$(cargo xtask tip macos)"` |
| Apple sims | `eval "$(cargo xtask tip tvos)"` (or visionOS / iOS / watchOS) then `simctl install` |

Force: `WAWONA_TEST_REBUILD=1`. Forbidden for UI proof:
`WAWONA_TIP_SKIP_BUILD=1` after editing Sources; `WAWONA_ALLOW_STALE_TEST_APP=1`.

## Agent loop

```text
edit Sources/…
→ cargo xtask tip <platform> (rebuilds if git-HEAD / product-FP is stale)
→ clean launch / simctl install tip
→ agent-device / Appium / screenshot
```

Rule: `docs/agent-rules/wawona-test-tip-app.md`. Skill: `wawona-test-tip-app`.
Related: `wawona-fresh-build`, `wawona-appium-ui-gh`, `wawona-test-control`.
