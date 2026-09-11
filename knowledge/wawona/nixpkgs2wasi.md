# nixpkgs2wasi

L3′ Rust toolchain at `github.com/Wawona/nixpkgs2wasi` (`development`). CLI:
`n2w`. Flake inputs: **nixpkgs only**. Never an input of L0-L3. L4 consumes
artifacts through `repo.wawona.io/wasm/v1`, not as a compositor flake edge.

Converts **curated** nixpkgs Wayland/userspace packages into WASI P1/P2
bytecode plus a WPM tree. Linux is not a runtime. Do not put a kernel, QEMU,
or UTM inside WASM.

```text
nixpkgs#foot → n2w → foot.wpm → /wasm/v1 → wpm → Relay Pulley → Wawona Compositor
```

Wayland stays Wayland. DRM/KMS/GBM ABI is **wwn-iland** userspace. Execute
engine is **Relay**. Catalog HTML/index is **repo.wawona.io**. Native ports
(`wwn-foot`) stay first-class.

`n2w verify` is the **Wawona App Store runtime profile** (WASM, Pulley, no
native payload). It is not App Review. Bundled vs downloadable catalog is a
separate WPM policy question.

North star: `n2w build nixpkgs#foot` then `wpm install foot` shows a Wayland
window on iPhone with no Linux VM. `hello-wasi-gui` already ships on `/wasm/v1`.

Hard rejects: auto-mirror nixpkgs; stub `.wasm`; UIKit translator; mix debs;
Mode B Runtime catalog; claim Apple approved the package.

Skill: `wawona-nixpkgs2wasi`. DAG: [`wwn-repo-dag.md`](wwn-repo-dag.md).
