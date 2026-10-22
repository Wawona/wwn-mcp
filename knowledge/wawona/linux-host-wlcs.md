# Wawona Linux Host, Relay Backends, and WLCS Conformance

Overview of Linux host support, Relay backend infrastructure, and Wayland protocol conformance testing via WLCS.

## 1. Wawona Linux Host UI (GTK4 + Libadwaita)

Binary: `wawona-linux-ui` (`src/bin/wawona-linux-ui.rs`).
Module: `src/linux/ui/` (`mod.rs`, `tab_overview.rs`, `editor.rs`, `settings.rs`, `navigation.rs`, `views/`).

Key characteristics:
- Native GNOME Human Interface Guidelines (HIG) compliance via Libadwaita 1.
- Tab Overview (`AdwTabOverview` / `AdwTabView`) for fluid machine session switching.
- Integrated Settings dialog (`AdwPreferencesWindow`) for Display, Input, Machines, and Network configuration.
- Built-in lightweight Editor view with line numbers and syntax styling.
- Core compositor integration via `wawona-core` / Smithay polling loop.
- Supports both nested Wayland (`WAYLAND_DISPLAY`) and X11 (`DISPLAY`) presentation.

## 2. Wawona Relay Linux Backends

Repository: `Wawona/Relay` (`github.com/Wawona/Relay`).
Takes over VM, container, and Wasm runtime responsibilities across all platforms.

On Linux:
- **Virtual Machines**: backed by host `cloud-hypervisor` using direct `/dev/kvm` hardware virtualization. Communicates with guests via vsock and waypipe.
- **Containers**: backed by host OCI runtime (`runc` / cgroups v2) with Linux namespace isolation.
- **Wasm**: backed by Wasm runtime for Store/WASI-P1/WASIX apps.
- Single unified daemon and CLI interface replacing legacy `wwn-runtime`, `wwn-vms`, and `wwn-containers`.

## 3. Headless Compositor Mode (Wawona Core)

Files: `src/ffi/c_api.rs`, `src/core/mod.rs`, `src/linux/headless.rs`.

New C ABI endpoints for headless test environments:
- `WWNCoreSetHeadlessHost(bool)`: switches compositor pipeline to headless mode without requiring physical displays, EGL, or Vulkan surfaces.
- `WWNCoreHeadlessHostTick()`: manual pump function driving the Smithay event loop, protocol dispatches, timers, and client sockets.
- `WWNCorePresentRenderScene(...)`: software SHM pixel capture allowing headless verification of rendered frame buffers.

## 4. WLCS Wayland Conformance Testing

Repository integration: `Wawona` (`tests/wlcs/`, `src/bin/wawona-wlcs.rs`).
Workflow: `.github/workflows/wlcs.yml` (`ci-l2-wlcs`).

Architecture:
- Implements the WLCS (Wayland Live Compositor Suite) server interface (`wlcs_server_integration`).
- Spawns in-process headless Wawona compositor using `WWNCoreSetHeadlessHost`.
- Provides mock input devices (pointer, keyboard, touch) and virtual output displays directly to WLCS test cases.
- Validates core Wayland protocol specifications (`wl_compositor`, `wl_subcompositor`, `wl_surface`, `wl_seat`, `xdg_shell`, `wl_shm`).
- Executes automatically on pull requests and commits to `development` as a mandatory quality gate.
