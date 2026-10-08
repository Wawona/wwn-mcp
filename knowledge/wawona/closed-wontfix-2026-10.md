# Closed wontfix (2026-10-07)

These GitHub issues on `Wawona/Wawona` are closed as **not planned**. Do not
reopen them. Do not implement the old plan under a new title.

## nixpkgs2wasi (#172-#177)

Milestone **Support nixpkgs2wasi** is closed. `n2w` is not the producer.

- Store WASI P1: `Wawona/wasm-packages` (GHA, Wasmtime smoke) to `/wasm/v1`.
- Nixpkgs to WASIX: `Wawona/wasinix` (Wasmer smoke). Not store Pulley.
- `Wawona/Wawona` `flake.nix` / `flake.lock` do not input `nixpkgs2wasi`.
- `github.com/Wawona/nixpkgs2wasi` may still exist. That is not permission to
  revive it. Do not add it back as a flake input.
- A wasm `foot` window, if still wanted, stays on epic #143. Not `n2w build`.

## UTM-SE downloadable (#33)

Do not bundle UTM or UTM-SE. Linux VM and container-in-VM engine is Wawona
Relay. Guest GUI is Wayland into Wawona (iland). Third-party UTM over SSH +
waypipe is a remote machine, not the product engine.

## watchOS wasm size gate (#156)

Do not keep Pulley off watchOS for size. Relay wasm is required on watchOS,
tvOS, visionOS, and every other product target. `hello-wasi-gui` must run
from Machines Start. GPU wasm on watchOS stays blocked (no Metal).
