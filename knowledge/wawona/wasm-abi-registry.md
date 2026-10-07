# Wasm ABI registry and GHA builds

Canonical registry prose:
[`repo.wawona.io/docs/wasm-abi.md`](https://github.com/Wawona/repo.wawona.io/blob/development/docs/wasm-abi.md).

Builder repo: [`Wawona/wasm-packages`](https://github.com/Wawona/wasm-packages).

## Today vs later

| | Today | Later (planned) |
|---|---|---|
| Machine API | `/wasm/v1/index.json` + `.wasm` | Wasmer/WebC via wasinix; keep store `wpm` clients working |
| Producer | **GHA** in `Wawona/wasm-packages` (`ubuntu-24.04`) | wasinix + `wawona` publish profile |
| Unit | `.wasm` (`component.wasm`) | `.webc` (`wasmer publish`) |
| Converter | None. `nixpkgs2wasi` retired | Do not revive `n2w` |

## GHA path (proven)

```text
recipes.json + packages/<name>/
  → build-wasm.yml (matrix, wasmtime smoke, artifacts)
  → publish-to-repo.yml (WAWONA_REPO_TOKEN) or staged PR
  → repo.wawona.io/wasm/v1
```

Proven packages: `hello-wasi` 0.1.2, `wasi-true` 0.1.0.
Local `cargo` is recipe debug only. Never publish laptop blobs as production.

```bash
gh workflow run build-wasm.yml --repo Wawona/wasm-packages
```

## ABI labels

| Label | Target | Runtimes |
|-------|--------|----------|
| WASI P1 | `wasm32-wasip1` | Wasmtime, Wasmer, WAMR, WasmEdge |
| WASI P2 | `wasm32-wasip2` | Component Model (+ Preview 1 adapter when needed) |
| WASIX | `wasm32-wasix` | **Wasmer only** |

Names: `wawona/wasi-p1-grep`, `wawona/wasix-ripgrep`.

## Phase order (expand on GHA)

1. Grow P1 CLI matrix in `wasm-packages` (grep, sed, awk, …)
2. Fork wasinix when public; WASIX lane on same runners (Wasmer-only labels)
3. Wayland proof (Weston terminal client), then small GTK client

## Same-commit product gate

Before WASIX is “runnable everywhere”:

- Store iOS/iPadOS ≤ 26: Pulley only. WASIX does not run there.
- macOS/Linux: Wasmtime Cranelift today; WASIX-as-Wasmer-only changes
  `wawona-relay-wasm`. Do not link Wasmer early.
- `wpm` stays Wasm package data. Never `docker pull`.

Hard rejects: claim WASIX on store Pulley; revive `nixpkgs2wasi`; treat
laptop builds as the publish source of truth.