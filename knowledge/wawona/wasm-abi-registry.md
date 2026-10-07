# Wasm ABI registry and GHA auto-publish

Canonical registry prose:
[`repo.wawona.io/docs/wasm-abi.md`](https://github.com/Wawona/repo.wawona.io/blob/development/docs/wasm-abi.md).

Builder repo: [`Wawona/wasm-packages`](https://github.com/Wawona/wasm-packages).

## Today vs later

| | Today | Later (planned) |
|---|---|---|
| Machine API | `/wasm/v1/index.json` + `.wasm` | Wasmer/WebC via wasinix; keep store `wpm` clients working |
| Producer | **GHA allowlist** in `Wawona/wasm-packages` (`ubuntu-24.04`) | wasinix + `wawona` publish profile |
| Unit | `.wasm` (`component.wasm`) | `.webc` (`wasmer publish`) |
| Converter | None. `nixpkgs2wasi` retired | Do not revive `n2w` |

## Upstream freshness (updatable)

Each allowlist row has `version_policy`: `local` | `cargo-deps` | `crates-io` | `git-tag`. Nightly runners run `check-upstream-versions.py` (catalog + crates.io / git tags / Cargo.lock deps), `bump-outdated.py` when ahead, rebuild, bot-commit `[skip ci]`. Artifact: `upstream-report`. Still allowlist-only.

## Auto-growth loop

```text
allowlist.toml (curated P1; blocked rows skip)
  → sync-recipes-from-allowlist.py → recipes.json
  → build-wasm.yml (push / dispatch / cron 0 6 * * *)
       nightly: select stale vs https://repo.wawona.io/wasm/v1/index.json
       cap: meta.max_new_per_nightly (default 3)
  → wasmtime smoke → artifact wasm-out
  → publish-to-repo.yml (workflow_run on green development)
       WAWONA_REPO_TOKEN → stage-for-repo.py → check-packages.py
       direct push to repo.wawona.io development (wawona-wasm-bot)
       optional open_pr=true dry-run
  → Pages on development → live /wasm/v1
```

Secret: `WAWONA_REPO_TOKEN` on `Wawona/wasm-packages` (prefer GitHub App /
machine user `wawona-wasm-bot`; `contents:write` on `repo.wawona.io`).

Wasinix fork: `github.com/Wawona/wasinix` (Nix→WASIX/WebC). Store P1 CLI kit in wasm-packages.

First-wave active: `hello-wasi`, `wasi-true`, `jq`, `gzip`, `grep`, `sed`,
`awk`. Blocked: `curl` (no store-safe WASI P1 HTTP recipe yet).

```bash
gh secret set WAWONA_REPO_TOKEN --repo Wawona/wasm-packages
python3 scripts/sync-recipes-from-allowlist.py
gh workflow run build-wasm.yml --repo Wawona/wasm-packages
```

Local `cargo` is recipe debug only. Never publish laptop blobs as production.

## ABI labels

| Label | Target | Runtimes |
|-------|--------|----------|
| WASI P1 | `wasm32-wasip1` | Wasmtime, Wasmer, WAMR, WasmEdge |
| WASI P2 | `wasm32-wasip2` | Component Model (+ Preview 1 adapter when needed) |
| WASIX | `wasm32-wasix` | **Wasmer only** |

Names: `wawona/wasi-p1-grep`, `wawona/wasix-ripgrep`.

## Phase order

1. Grow P1 CLI allowlist on GHA (grep/sed/awk/gzip/jq first wave)
2. Fork wasinix when public; WASIX lane on same runners (Wasmer-only labels)
3. Wayland proof (Weston terminal client), then small GTK client

## Same-commit product gate

Before WASIX is “runnable everywhere”:

- Store iOS/iPadOS ≤ 26: Pulley only. WASIX does not run there.
- macOS/Linux: Wasmtime Cranelift today; WASIX-as-Wasmer-only changes
  `wawona-relay-wasm`. Do not link Wasmer early.
- `wpm` stays Wasm package data. Never `docker pull`.

Hard rejects: claim WASIX on store Pulley; revive `nixpkgs2wasi`; auto-mirror
nixpkgs; treat laptop builds as the publish source of truth.

## Native over wasm

Do not package `/wasm/v1` twins of CLIs in `wasm-packages/scripts/native-all-targets.txt` (uutils safe subset on every target). Rule: `wawona-native-over-wasm`.
