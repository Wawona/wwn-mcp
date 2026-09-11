# Host keymap bridge

Indexed summary. Full copy: `Wawona/docs/agent-rules/wawona-host-keymap-bridge.md`.
Cursor rule: `wawona-host-keymap-bridge` (`alwaysApply`).
Skill: `wawona-host-keymap`.

## Split

Wawona does not catalog layouts. Host TIS / `UCKeyTranslate` /
`NSTextInputClient` / HID / `KeyCharacterMap` / Android IME map onto
`wl_keyboard.keymap` (XkbV1) and `zwp_text_input_v3`.

Smithay keyboard is the seat. `HostKeymapBridge.keymap_xkb_v1()` then
`set_keymap_from_string`. Last phase: macOS `UCKeyTranslate` and Android
`KeyCharacterMap` push UTF-32 via `WWNApplyHostKeyLevels`. iOS family
stays US fallback. No locale-to-RMLVO table.

## Smell

Agents recreated QWERTY matrices (`charToLinuxKeycode`, Watch 2000-line
blobs, Settings layout picker). That is the #60 mismatch. Delete those
paths. Do not add AZERTY in ObjC.

Touch Input Type / Touchpad Mode / Swap CMD/ALT are not layout.

## Hard rejects

- Settings Keyboard layout picker
- `zwp_wawona_keymap`
- IBus/Fcitx as Apple/Android IME
- Second xkb machine beside Smithay
