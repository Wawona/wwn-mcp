# Machines: three kinds + Native Shell sessions

Updated 2026-10-07. Product UX collapse. Not a schema deletion of legacy
`MachineType` enum cases.

## User-facing kinds

1. **Native Shell**
2. **Virtual Machine**
3. **Container**

Add/Edit pickers use only these three (`MachineType.selectableCases`,
`MachineType::selectable_for_ui`, `kWWNSelectableMachineTypes`).

## Native Shell sessions

| Session | Notes |
|---|---|
| Terminal | Wawona Terminal (`wawona-shell`). Local or SSH. Optional Custom Command (`NativeCustomCommand` / `remoteCommand`). Not foot / weston-terminal. |
| Wayland | Bundled Wayland client only. No SSH. No Custom Command row. |
| Wasm | Relay WASI / `wpm` / `repo.wawona.io/wasm/v1`. |
| Waypipe | waypipe local or SSH+waypipe. |

WWN overrides: `NativeShellKind`, `NativeShellUseSSH`, `NativeCustomCommand`
(Terminal). Legacy load: `type=wasm|ssh_terminal|ssh_waypipe` folds into
Native Shell in the editor. Connect still understands those storage types.
Legacy Wayland client id `custom` migrates to Terminal.

## Do not

- Re-add SSH / Wasm / Waypipe as top-level Machines kinds in UI
- Infer Use SSH from leftover `sshHost` alone
- Offer `wawona-shell` / `wawona-wasm` in the Wayland client picker
- Offer Custom Command as a Wayland client (use Terminal session)

## Code

- `Sources/WawonaModel/MachineProfile.swift` (`NativeShellSession`)
- `Sources/WawonaApple/Machines/MachineConstants.swift`
- `Sources/WawonaApple/Runners/WWNMachineSessionBridge.swift`
- `Sources/WawonaUI/Machines/Editor/*`, `MachineEditorView.swift`
- `src/domain/machine_profile.rs`, `src/linux/ui/editor.rs`

Skill: `wawona-machine-types`. Rule: `wawona-machine-types`.
