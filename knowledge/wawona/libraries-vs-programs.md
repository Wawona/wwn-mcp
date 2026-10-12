# wasinix: libraries vs programs

wasinix splits two trees. Do not mix them.

| Tree | Path | Flake | What |
|------|------|-------|------|
| Libraries / toolkits | `pkgs/libraries/` | `.#wasix.libraries.<profile>.<name>` | Linkable `.a` / headers: zlib, cairo, **GTK4** |
| Programs | `pkgs/programs/` | `.#wasix.<name>` / `.#wasmer.<name>` | Runnable CLIs/apps: grep, nano |

**GTK4 is a library/toolkit**, not a program. Recipe: `pkgs/libraries/gtk.nix`
(closure + Wawona Wayland fd bridge). A GTK demo app would be a separate
`pkgs/programs/` consumer that links `libraries.gtk4`. Never `programs/gtk4`.

Standing split example: `libraries.ncurses` (`--without-progs`) vs
`programs.ncurses` (`--with-progs`).

Programs on tip: `wayland-bridge-smoke`, `gtk4-hello` (link toolkit; Relay
host `wawona_wayland_*`). Smoke: `wasinix/scripts/smoke-wayland-relay.sh`.
Library CI: `gtk-wasix-libs.yml` on `development`/`main`.

Docs: `wasinix/docs/libraries-vs-programs.md`, `wasinix/docs/gtk4-wayland.md`.
Rules: `wawona-wasm-cli-ports`, `wawona-optional-software`.
