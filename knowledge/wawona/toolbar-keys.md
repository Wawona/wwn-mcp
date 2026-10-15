# ToolbarKeys

L3′ crate at `github.com/Wawona/ToolbarKeys`.

Rootshell's keyboard toolbar is the starting point.
Copyright (c) 2026 Rootshell LLC, Kit Knox. MIT.

Ellipsis / drawer: UIKit stacks drawer rows *above* the main toolbar and
grows intrinsic height. Android `ToolbarKeysBar` must `Column`-stack the
same (never `Box` siblings that overlay the main row).

The key catalog, drawer rows, custom sequences, and width overflow live
here as Rust. UniFFI exports `ToolbarSession`. Host UI also lives here:

- `apple/Keyboard` UIKit (iOS family)
- `android/com/wawona/toolbarkeys` Compose (`ToolbarKeysBar`, chrome,
  layout store, settings sheet)

Wawona overlays / compiles those trees. The Wayland accessory bridge
stays in Wawona. Do not copy Swift or Compose back into the app.

iOS deployment target stays 13.0. Android uses the same JSON document.
`phone` and `pad` are the two default layouts (Rootshell version 14).

## Product hosts (must ship)

- **Compositor soft keyboard:** iOS `WWNCompositorView_ios` attaches
  `WWNKeyboardAccessoryView` as `inputAccessoryView`. Android
  `ToolbarKeysBar` + `ToolbarKeyChrome` clones the UIKit plate
  (glass tint, clear keys, equal-fill main row, lock bar, drawer
  separators). Android key faces stay symbols like ToolbarKeys (⎋⌃⌥⇧◆
  Meta for `cmd`), never Win ⊞, never Ctrl/Alt abbreviations, never Mac
  ⌘. Do not ship Material `TextButton` chips as the Toolbar Keys look.
- **Settings:** iOS `KeyboardToolbarSettingsView` as `.pageSheet` (Done +
  EditButton). Android `ToolbarKeysSettingsSheet` ModalBottomSheet (Done
  + Edit). Edit rearranges key order like Rootshell. Global Settings →
  Input also exposes Customize + docking/appearance
  (`persistentToolbar`, `showToolbarWithHardwareKeyboard`,
  `toolbarThemeAware`, `toolbarChromeStyle`, `arrowJoystickMode`).
- **Wawona Terminal (Start):** iOS `WWNTerminalToolbarHost` first-responder
  + same accessory; shell bytes go to PTY. Android draws the bar **above**
  `GuestConsoleOverlay` (not buried); printable routes into the Terminal
  buffer until Done/Focus, then compositor inject resumes.
- Hardware keyboard: dock only when `showToolbarWithHardwareKeyboard` (or
  persistent). Else hide accessory / `HIDDEN_EXTERNAL`. When docked,
  accessory-only (hide OSK), Android `ACCESSORY_ONLY`.
- Chrome styles tint glass via `ToolbarChromePalette` / `ToolbarHostOptions`.
- tvOS / visionOS may omit some UIKit materials. Watch unchanged.

Wawona may depend on this crate. This crate does not depend on Wawona,
Ghostty, or iland.

Do not grow the Rootshell SwiftUI toolbar inside the Wawona app as the owner.
Prose: `Wawona/docs/toolbar-keys.md`.
