# ToolbarKeys

L3′ crate at `github.com/Wawona/ToolbarKeys`.

Rootshell's keyboard toolbar is the starting point.
Copyright (c) 2026 Rootshell LLC, Kit Knox. MIT.

The key catalog, drawer rows, custom sequences, and width overflow live
here as Rust. UniFFI exports `ToolbarSession`. `apple/Keyboard` is the
UIKit drawing, also from that Rootshell implementation. Wawona compiles
that directory from this repo. The Wayland accessory bridge stays in
Wawona. Do not copy those Swift files back into the app.

iOS deployment target stays 13.0. Android uses the same JSON document.
`phone` and `pad` are the two default layouts (Rootshell version 14).

## Product hosts (must ship)

- **Compositor soft keyboard:** iOS `WWNCompositorView_ios` attaches
  `WWNKeyboardAccessoryView` as `inputAccessoryView`. Android keeps
  `ModifierAccessoryBar` for the session.
- **Wawona Terminal (Start):** iOS `WWNTerminalToolbarHost` first-responder
  + same accessory; shell bytes go to PTY. Android draws the bar **above**
  `GuestConsoleOverlay` (not buried); printable routes into the Terminal
  buffer until Done/Focus, then compositor inject resumes.
- Hardware keyboard: accessory-only (hide OSK), Android `ACCESSORY_ONLY`
  parity.
- tvOS / visionOS omit ToolbarKeys UIKit. Watch unchanged.

Wawona may depend on this crate. This crate does not depend on Wawona,
Ghostty, or iland.

Do not grow the Rootshell SwiftUI toolbar inside the Wawona app as the owner.
Prose: `Wawona/docs/toolbar-keys.md`.
