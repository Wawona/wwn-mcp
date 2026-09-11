# Host edit menu and clipboard

Indexed so agents do not overlay OS selection handles on Wayland clients.

## Protocol

Wayland has no interface that reports glyph boxes or "this pixel range is
selected text" for an arbitrary client (weston-terminal, GTK, Qt).

- `wl_data_device`: clipboard **transport** only
- `zwp_text_input_v3` surrounding text: IME, not visual selection
- Primary selection: Smithay `primary_selection` on desktop profiles.
  Mobile UX is explicit Copy/Paste, not middle-click.

So iOS `UITextInteraction` knobs, Android selection handles, and a
compositor-drawn highlight on client pixels are **forbidden**. That would
need OCR or a Wawona-only protocol. Port fidelity (waypipe equivalence)
rejects both.

## What ships

Long-press on Multi-Touch is `wl_touch`. The client toolkit draws handles
and the Copy/Cut/Paste menu. Do **not** cancel that contact to show a
host overlay.

Host **chrome** Copy/Paste (not over the Wayland surface) stays, gated by
Universal Clipboard:

| Host | Stock UI | Action |
|------|----------|--------|
| iOS / iPadOS / visionOS | Hardware keyboard `copy:` / `paste:` | Terminal focused: Ctrl+C is VINTR (`0x03`), not Copy. Cmd+C still injects Ctrl+Shift+C. Non-terminal: Copy injects Ctrl+Shift+C. Paste is TI `commit_string` or PTY inject or Ctrl+Shift+V |
| macOS | Edit menu Cmd+C / Cmd+V | Same chords / TI |
| Android | none on the compositor surface | Long-press is `wl_touch` for the client |
| tvOS | none | No `UIPasteboard` |
| watchOS | none | No stock text edit menu |
| Linux | client toolkit | Host Machines window is not the compositor surface |

Existing tick sync (`WWNCorePollClipboardText` / `SetClipboardText`) still
mirrors client Copy onto `UIPasteboard` / `NSPasteboard` / `ClipboardManager`.

## Hard rejects

- UIKit / Android selection handles on Wayland surfaces
- Returning a fake `characterRangeAtPoint:` so iOS draws handles
- `UIEditMenuInteraction` / `ActionMode` on long-press over a Wayland
  surface (that `wl_touch.cancel`s the client selection)
- Treating host Paste as proof the client highlighted those glyphs
- Inventing `zwp_wawona_selection`
- Custom `wl_touch` broadcast as the protocol owner while Smithay
  `TouchHandle` exists
- Global Multi-Touch one-finger or two-finger drag as `wl_pointer.axis`
- Holding `BTN_LEFT` over GTK/Qt/browser content. Pointer + button is
  only for nested weston/niri chrome, or the off-by-default
  `TouchPointerEmulation` pref.

Code: `WWNCompositorBridge` `hostEdit*` (macOS Edit menu / hardware
keyboard), `WWNCompositorView_ios` `copy:`/`paste:`, `WWNView` `copy:`/`paste:`.
