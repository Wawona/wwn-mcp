# repo.wawona.io catalog grid

Two channels. Three kinds. The APT index file at the repo root is named
`Packages`, so the recipe tree is `catalog/` (a `packages/` directory cannot
exist beside that file on a case-insensitive disk).

```text
catalog/wasm/cli/<name>/
catalog/wasm/gui/<name>/
catalog/wasm/lib/<name>/
catalog/deb/cli/<name>/
catalog/deb/gui/<name>/
catalog/deb/lib/<name>/
```

`builtins.readDir` is the index (`catalog/load.nix`). One directory is one
card. Wasm `abi` is `wasi-p1`, `wasi-p2`, or `wasix`. It is not a directory.
P1 and P2 smoke with Wasmtime. WASIX smokes with Wasmer.

P1 sources: `catalog/wasm/src/p1`. WASIX sources: `catalog/wasm/src/wasinix`.
Flake output `legacyWasix` is that tree's package function. Publish path for
store bytecode stays `/wasm/v1`.

Process debs (weston, niri, foot, weston-simple-shm) are
`catalog/deb/gui/<name>/default.nix`. Android libraries stay
`pkgs/wayland/ndkLibs.nix`. Debs do not import `apple-mobile.nix` and do not
rename `main` to `*_main`.

In-app archives live in `in-app/` next to the deb card. One
`registryFragment` covers weston, niri, foot, kmscube, fastfetch, phoon, and
neovim. Wawona inputs `github:Wawona/repo.wawona.io/development` only.
`wwn-toolchain` does not input the catalog.

Add a package by creating `catalog/<channel>/<kind>/<name>/default.nix`.
Copy `pkgs/wayland/TEMPLATE.nix` for a deb.
