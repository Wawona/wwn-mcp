# Wasm ABI registry and GHA auto-publish

Canonical registry prose:
[`repo.wawona.io/docs/wasm-abi.md`](https://github.com/Wawona/repo.wawona.io/blob/development/docs/wasm-abi.md).

Two build lanes (hard law): rule `wawona-wasm-cli-ports`, skill
`wawona-wasm-cli-ports`. Catalog identity: `repo-wawona-io-ports`.

| Lane | Where | ABI | Catalog |
|------|------|-----|---------|
| Store P1 | `repo.wawona.io` `catalog/wasm` `abi = wasi-p1` | `wasm32-wasip1` | `/wasm/v1` for `wpm` / Pulley |
| WASIX | same tree, `abi = wasix` (`catalog/wasm/src/wasinix`) | `wasm32-wasix` | Wasmer/WebC (not store Pulley) |

`nixpkgs2wasi` / `n2w` are **retired**. GitHub #172-#177 closed wontfix.
Do not revive. Do not auto-mirror nixpkgs. A live `Wawona/nixpkgs2wasi`
checkout is not a Wawona flake input and not the `/wasm/v1` producer.
Do not ship stub CLIs under upstream names.

## Today vs later

| | Today | Later (planned) |
|---|---|---|
| Machine API | `/wasm/v1/index.json` + `.wasm` | Wasmer/WebC from `catalog/wasm` `abi = wasix`; keep store `wpm` clients working |
| Store P1 producer | `catalog/wasm/src/p1` allowlist | same; real upstream recipes only |
| WASIX producer | `catalog/wasm/src/wasinix` via flake `legacyWasix` | `wawona` publish profile to registry |
| Unit | `.wasm` (`component.wasm`) for P1 | `.webc` (`wasmer publish`) for WASIX |
| Converter | None | Do not revive `n2w` |

## How to port a CLI

1. Native-all-targets? Stop (`wawona-native-over-wasm`).
2. Needs POSIX process/socket/TTY? → `catalog/wasm` `abi = wasix`: override nixpkgs
   pkg with wasixcc, patches beside recipe, `makeWasmerPackage`, upstream `homepage` + version.
3. Fits P1 and must run on Pulley? → `catalog/wasm/src/p1/allowlist.toml` + real upstream
   recipe. Not a 30-line toy. Do not recreate `Wawona/wasm-packages`.
4. Catalog: `homepage` = upstream project URL; `source` = packaging tree;
   `version` = upstream release.

## Upstream freshness (P1 allowlist)

Each allowlist row has `version_policy`: `local` | `cargo-deps` | `crates-io` |
`git-tag`. Nightly: `check-upstream-versions.py`, `bump-outdated.py`, rebuild,
bot-commit `[skip ci]`. Still allowlist-only.

## Auto-growth loop (store P1 only)

```text
allowlist.toml (curated P1; blocked rows skip)
  → sync-recipes-from-allowlist.py → recipes.json
  → build-wasm.yml (push / dispatch / cron)
       nightly: select stale vs https://repo.wawona.io/wasm/v1/index.json
       cap: meta.max_new_per_nightly
  → Wasmtime smoke (P1/P2) → smoke-result.json per package
  → summarize-smoke-results.py → artifact wasm-out
  → publish-to-repo.yml → stage-for-repo.py → check-packages.py
       push repo.wawona.io development (wawona-wasm-bot)
  → Pages on development → live /wasm/v1
```

### Runtime test matrix (required)

| ABI | CI runtime | Harness |
|-----|------------|---------|
| WASI P1 / P2 | **Wasmtime** | `wasm-packages/scripts/smoke-package.sh` |
| WASIX | **Wasmer** | `wasinix/smokes.toml` + `scripts/smoke-wasix-package.sh` |

Every active package must emit pass/fail JSON. Empty pass set is red. Do not
smoke WASIX with Wasmtime. Do not use Wasmer as the store P1/P2 gate.

### Hydra-style UI

`stage-for-repo.py` merges each `smoke-result.json` into
`repo.wawona.io/wasm/v1/index.json` as `ci.status` (`pass`|`fail`|`unknown`)
plus `ci.suites` (`smoke`, later `terminal` / `socket` / `wayland`). Summary
file: `/wasm/v1/ci.json`. Search UI shows a green/red/gray dot beside the
package version on `/search/?channel=wasm`.

WASIX smoke: `catalog/wasm/src/wasinix/smokes.toml` and
`scripts/smoke-wasix-package.sh`. `Wawona/wasinix` is deleted.

Secret: `WAWONA_REPO_TOKEN` on `Wawona/repo.wawona.io` when a publish workflow
runs from that repo. Do not set it on the deleted `wasm-packages` repo.

Active P1 today: Wawona Runtime smokes (`hello-wasi`, `wasi-true`,
`wasi-false`, …) plus real ports when they land (e.g. `chess` with upstream
version). Stub `jq`/`gzip`/`grep`/`sed`/`awk` stay **blocked** until a real
upstream tree is packaged. WASIX queue (curl, git, tar, …) stays
`build = wasinix` blocked in the allowlist until published via wasinix.

```bash
# from repo.wawona.io
python3 catalog/wasm/src/p1/scripts/sync-recipes-from-allowlist.py
nix eval .#catalogIndex.hello-wasi.abi
nix eval .#legacyWasix --apply 'f: builtins.isFunction f'
```

Local `cargo` is recipe debug only. Never publish laptop blobs as production.

## ABI labels

| Label | Target | CI smoke runtime |
|-------|--------|------------------|
| WASI P1 | `wasm32-wasip1` | Wasmtime (`wasm-packages`) |
| WASI P2 | `wasm32-wasip2` | Wasmtime (`wasm-packages`) |
| WASIX | `wasm32-wasix` | Wasmer (`wasinix`) |

Later Wasmer-style names: `wawona/wasi-p1-grep`, `wawona/wasix-ripgrep`.

## Phase order

1. Store P1 allowlist on GHA: real upstream recipes only (no stubs).
2. Grow wasinix WASIX / WebC recipes from nixpkgs overrides (grep, sed, tar, …).
3. Same-commit product gate before WASIX is “runnable everywhere”.
4. Wayland proof (Weston terminal client), then a small GTK client.

## Same-commit product gate

Before WASIX is “runnable everywhere”:

- Store iOS/iPadOS ≤ 26: Pulley only. WASIX does not run there.
- macOS/Linux: Wasmtime Cranelift today; WASIX-as-Wasmer-only changes
  `wawona-relay-wasm`. Do not link Wasmer early.
- `wpm` stays Wasm package data. Never `docker pull`.

Hard rejects: claim WASIX on store Pulley; revive `nixpkgs2wasi`; auto-mirror
nixpkgs; treat laptop builds as the publish source of truth; forge upstream
names with invented `0.1.0`.

## Native over wasm

Do not package `/wasm/v1` twins of CLIs in
`wasm-packages/scripts/native-all-targets.txt`. Rule: `wawona-native-over-wasm`.

## Package version vs ABI

Catalog `version` = upstream (or Wawona scratch) **package** version. ABI is
separate (`wasi-p1`/`wasix`). Ports use the upstream release and upstream
`homepage`. See `wasm-packages/docs/package-versioning.md` and
`repo-wawona-io-ports`.
