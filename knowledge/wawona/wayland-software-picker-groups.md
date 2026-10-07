# Native Wayland software picker grouping

Machine editor (Native Shell → Wayland) lists bundled software as:

1. **Compositors** (weston, niri)
2. Client types: **Terminals**, **Graphics**, **Demos**
3. **Other** (e.g. weston-simple-shm)

Custom commands belong under **Native Shell → Terminal** (Custom Command
beside Use SSH), not in this Wayland picker. Legacy client id `custom`
migrates to Terminal on edit/save.

Shared classifiers:

- Swift: `BundledWaylandSoftwareKind` in `Sources/WawonaModel`
- Linux: `SoftwareKind` / `wayland_picker_groups()` in `src/linux/bundled_clients.rs`
- Android: `BundledWaylandSoftwareKind` in `BundledClients.kt`

Never list `wawona-shell` / `wawona-wasm` in this Wayland picker (those are
other Native Shell sessions).
