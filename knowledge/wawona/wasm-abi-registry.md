# Wasm ABI registry (later Wasmer / WebC)

Canonical registry prose:
[`repo.wawona.io/docs/wasm-abi.md`](https://github.com/Wawona/repo.wawona.io/blob/development/docs/wasm-abi.md).

## Today vs later

| | Today | Later (planned) |
|---|---|---|
| Machine API | `/wasm/v1/index.json` + `.wasm` | Wasmer/WebC via wasinix; keep store `wpm` clients working |
| Producer | Curated blobs | Upstream wasinix + `wawona` publish profile at `repo.wawona.io` |
| Unit | `.wasm` | `.webc` (`wasmer publish`) |
| Converter | None. `nixpkgs2wasi` retired | Do not revive `n2w` |

## ABI labels

| Label | Target | Runtimes |
|-------|--------|----------|
| WASI P1 | `wasm32-wasip1` | Wasmtime, Wasmer, WAMR, WasmEdge |
| WASI P2 | `wasm32-wasip2` | Component Model (+ Preview 1 adapter when needed) |
| WASIX | `wasm32-wasix` | **Wasmer only** |

Names: `wawona/wasi-p1-grep`, `wawona/wasix-ripgrep`. Metadata in
`wasmer.toml` `[package.metadata]`: `abi`, `abi-target`, `runtime`, `posix`,
`wayland`, plus source revision and rebuild command.

## Phase order (not started)

1. Fork wasinix; point publication at `repo.wawona.io/wasm`
2. P1 CLI set (coreutils, busybox, grep, sed, awk, gzip, curl, wget, jq, git,
   make, cmake, CPython core, lua, sqlite3, openssl CLI)
3. Five WASIX tools including bash and nix
4. Wayland proof (Weston terminal client), then small GTK client (Mesa +
   WASIX socket → Wawona still open)

## Same-commit product gate

Before WASIX is “runnable everywhere”:

- Store iOS/iPadOS ≤ 26: Pulley only. WASIX does not run there.
- macOS/Linux: Wasmtime Cranelift today; WASIX-as-Wasmer-only changes
  `wawona-relay-wasm`. Do not link Wasmer early.
- `wpm` stays Wasm package data. Never `docker pull`.

Hard reject: claim WASIX/WebC/wasinix shipping on store Pulley.