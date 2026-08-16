# Wawona multi-repo development model

Wawona development is split across the **Wawona GitHub organization**
(`github.com/Wawona/*`). The monolithic era — all patched software living under
`Wawona/dependencies/` — is over. Today:

- **`Wawona/Wawona`** is the **integration layer**: Smithay compositor, SwiftUI
  apps, Android packaging, `flake.nix` that wires everything together.
- **`wwn-toolchain`** owns the cross-compile framework, substrate libraries, and
  `wawona-pty`.
- **`wwn-*` repos** own headline patched upstreams and compositors (iland,
  weston, **niri**, kmscube, waypipe, zsh, ssh, wasm, containers, …).

## Local checkout layout

```
~/Wawona/
├── Wawona/           # integration (compositor, apps, flake inputs)
├── wwn-mcp/          # this retrieval server (stdio)
├── wwn-toolchain/
├── wwn-iland/
├── wwn-kmscube/
├── wwn-weston/
├── wwn-niri/
├── wwn-waypipe/
├── Wawona-Swinging-Bridge/
├── wwn-vms/
├── wwn-containers/
├── wwn-ssh/
├── wwn-zsh/
├── wwn-coreutils/
├── wwn-foot/
├── wwn-fastfetch/
├── wwn-neovim/
├── wwn-phoon-rs/
├── wwn-wasm/         # Wawona Runtime (WASI); optional package path
└── wawona.io/
```

`wwn-apt` is **retired** (tombstone only if the GitHub repo remains).

## Documentation firewall (App Store vs jailbreak)

| Surface | Rule |
|---------|------|
| **Wawona / wwn-wasm** | App Store Runtime + Wasm packages. **Zero** jailbreak / `repo.wawona.io`. |
| **`repo.wawona.io`** | Jailbreak `.deb` only. Not in default wwn-mcp corpus. |
| **Wawona App Store docs** | Native ports + Wasm documents/packages; no StoreKit ODR `apt`. |

## Where to edit what

| Change | Repo |
|--------|------|
| zsh exec patch, RootFS | `wwn-zsh` |
| Weston patches | `wwn-weston` |
| Niri recipe | `wwn-niri` |
| iland / ANGLE / ICDs | `wwn-iland` |
| kmscube | `wwn-kmscube` |
| waypipe-rs | `wwn-waypipe` |
| Wawona Swinging Bridge | `Wawona-Swinging-Bridge` |
| SSH / libssh2 | `wwn-ssh` |
| VMs / containers | `wwn-vms` / `wwn-containers` |
| WASI Runtime / Wasm packages | `wwn-wasm` (+ Wawona docs) |
| XcodeGen, Android APK, Rust backend, Machines | `Wawona` |
| Public website | `wawona.io` |
| Agent RAG / corpus | `wwn-mcp` |

Canonical DAG: [`wwn-repo-dag.md`](wwn-repo-dag.md).
Contribute checklist: [`contribute.md`](contribute.md).
