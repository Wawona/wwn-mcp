# Wawona Ports (catalog + how to build)

Almost every package on `repo.wawona.io` is a **port** of existing software.
Build law: rule/skill `wawona-wasm-cli-ports`. Catalog host rule:
`repo-wawona-io-ports`.

## Two build lanes

| Lane | When | Repo | CI smoke |
|------|------|------|----------|
| WASI P1/P2 (store / Pulley) | Fits Preview 1/2 | `Wawona/wasm-packages` GHA | **Wasmtime** |
| WASIX | Needs POSIX process/socket/TTY | `Wawona/wasinix` (nixpkgs override + wasixcc) | **Wasmer** |

Never auto-mirror nixpkgs. Never revive `nixpkgs2wasi` / `n2w` (GitHub
#172-#177 closed wontfix). A live `Wawona/nixpkgs2wasi` repo is not the
producer. Never publish a stub under `sed` / `jq` / `grep` at invented `0.1.0`.

## Catalog laws

- Package `name`: upstream name for ports; distinct unbranded name for scratch.
  Never `wawona-` / `wwn-` prefix or `-wawona` / `-wwn` suffix.
- Port `version`: upstream release/tag. Require `upstream_version`.
  `upstream_is_bootstrap` only when upstream itself is that bootstrap.
- Field **`homepage`**: upstream project URL (nixpkgs `meta.homepage`). Not
  `website`. Never blanket `wawona.io/docs/wasm/`.
- Field **`source`**: port / packaging tree (wasm-packages or wasinix).

## Where

| Piece | Path |
|-------|------|
| Build decision rule | `wawona-wasm-cli-ports` |
| Catalog gate | `repo.wawona.io/scripts/check-packages.py` |
| P1 allowlist | `wasm-packages/allowlist.toml` |
| WASIX recipes | `wasinix/pkgs/programs/<name>/` |
| ABI prose | `repo.wawona.io/docs/wasm-abi.md`, this file’s sibling `wasm-abi-registry.md` |

Exception: reverse-DNS first-party Mode B app ids
(`com.aspauldingcode.wawona.modeb.demo`).
