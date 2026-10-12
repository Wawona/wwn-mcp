# WASIX libraries vs programs

Implementation lives in `repo.wawona.io` `catalog/wasm/src/wasinix`.
The card kind is the public split. Do not mix them.

| Kind | Card | Implementation | What |
|------|------|----------------|------|
| lib | `catalog/wasm/lib/<name>/` | `pkgs/libraries/` | Linkable `.a` / headers: zlib, cairo, **GTK4** |
| cli | `catalog/wasm/cli/<name>/` | `pkgs/programs/` | Runnable tools: grep, nano |
| gui | `catalog/wasm/gui/<name>/` | `pkgs/programs/` when it draws | gtk4-hello, wayland-bridge-smoke |

**GTK4 is a library**, card `catalog/wasm/lib/gtk4`, recipe `pkgs/libraries/gtk.nix`.
A GTK demo is `gui`. Never a program named gtk4.

`Wawona/wasinix` is deleted. Upstream `xtyxtyx/wasinix` stays.
Flake output `legacyWasix` is `{ system, nixpkgs }: ...`.
Smoke: `catalog/wasm/src/wasinix/scripts/smoke-wayland-relay.sh` and `smokes.toml`.

Rules: `wawona-wasm-cli-ports`, `wawona-optional-software`.
Grid: `catalog-grid.md`.
