# iOS app entry and Simulator runtime (2026-10-08)

Hard gate: `Wawona/docs/agent-rules/wawona-ios-app-entry.md` (Cursor
`wawona-ios-app-entry`). Skill: `wawona-ios-sim-runtime`.

## What broke

1. `libgbm_es2_demo.a` exported C `_main`. Linked into the iOS app, that
   symbol became LC_MAIN. Process ran the ES2 cube and exited. Machines UI
   never appeared.
2. Renaming archive `main` to `gbm_es2_demo_cli_main` fixed the steal, then
   the iOS target had **no** `_main` because `Darwin/Sources/Main.swift` was
   only on the macOS xcodegen target.
3. Putting SwiftUI `App` / `Scene` on iOS failed the **13.0** floor
   (`scenePhase`, `UIApplicationDelegateAdaptor` need iOS 14). Mobile entry
   is `UIApplicationMain` + `WWNSceneDelegate` hosting `WawonaRootView`.
4. `-Dmain=gbm_es2_demo_main` **redefines** the existing
   `extern "C" gbm_es2_demo_main` in upstream `main.cpp`. Keep
   `-Dmain=gbm_es2_demo_cli_main`.
5. Host compositor bind used `/tmp/wawona-<uid>` and failed on Simulator.
   Set `XDG_RUNTIME_DIR` to `preferredSharedRuntimeDir()`
   (`/tmp/wawona_sim_<uid>`) before `WWNCoreStart`.
6. `Label { } icon:` in Settings hub is iOS 14+. Use `HStack` + iconTile.
7. Nesting a `UIView` under `UIHostingController.view` triggers a SwiftUI
   runtime warning. Host chrome only.

## Sim dogfood

- `defaults import` for profiles. Raw plist file edits lose to cfprefsd.
- `wawona.machineProfiles.v1` is JSON **NSData**.
- Env into guest: `SIMCTL_CHILD_WWN_AUTO_START_MACHINE=<id>`. Plain
  `simctl launch -e VAR=val` is **argv**, not environment.
- Lab Start: SceneDelegate auto-start when agent-device
  `build-for-testing` is red (Xcode 26). Connected badge may stay 0;
  trust stderr `WWN_AUTO_START_MACHINE: started …` and
  `/tmp/wawona_sim_$UID/wayland-0`.

## Machines Start (host + sim)

1. **Unlinked Wayland socket.** `wayland-0` path can vanish while the
   listen fd stays open. Clients get `ENOENT`. `isRunning` must require a
   connectable path; `ensureRunning` stops and rebinds. Heal: kill Wawona,
   `rm` `/tmp/wawona-$UID/wayland-*` locks, relaunch, prove connect.
2. **Wasm no-op.** `launchBundledClient("wawona-wasm")` must call
   `launchWasmModule` (bundled `hello-wasi-gui.wasm` or `wasmModulePath`).
   A bare `break` marks Connected without running the module.

## Verify snippets

```bash
nm -gU "$GBM_A" | rg 'T _' | rg -i 'main|gbm'
# expect: _gbm_es2_demo_main, mangled cli_main; no T _main
SIMCTL_CHILD_WWN_AUTO_START_MACHINE=e2e-wasm-hello \
  xcrun simctl launch --stderr=/tmp/w.err booted com.aspauldingcode.Wawona
rg 'AUTO_START|Compositor started' /tmp/w.err
```
