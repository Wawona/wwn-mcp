# wwn-apt. Removed

**Retired.** Do not answer as if StoreKit / ODR `apt install` of Mach-O modules
is a Wawona product path.

## Replacement

- **Wawona Runtime** (`wwn-wasm`): WASI P1/P2 `.wasm` via Files.app or a bundled
  Wasm package client (OCI artifacts preferred).
- Canonical product doc: `Wawona/docs/wasm-wasi.md`.
- **Containers** (`wwn-containers` + Machines kind `container`): OCI Linux images
  (e.g. Docker Hub), macOS Apple Container / iOS UTM-SE jitless container-in-VM -
  **not** Wasm packages.

If a user asks about `apt` on iPhone in Wawona: explain it was removed; point at
Wasm Runtime + shell.
