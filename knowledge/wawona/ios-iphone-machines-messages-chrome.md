# iPhone Machines: Messages bottom chrome

Indexed summary. iPhone Machine Configuration matches iMessage / Mail
Liquid Glass: system search at the bottom, new-machine + to the right.

## What shipped

- Phone idiom only (`UIDevice` phone, not size class). The split forces
  regular width, so size class cannot detect phone.
- iOS 26 native row (required, `usesNativePhoneSearchToolbar`):
  `.searchable(text:)` (default placement) plus toolbar
  `DefaultToolbarItem(kind: .search, placement: .bottomBar)`,
  `ToolbarSpacer(.flexible, placement: .bottomBar)`, then
  `ToolbarItem(placement: .bottomBar)` with a plain `Label(..., "plus")`,
  `.tint(accent)`, `.sharedBackgroundVisibility(.hidden)`.
  No custom capsule. No fixed 44/56pt frame on the +. The system sizes
  search and + to the same bottom chrome.
- Top-trailing sort/Settings: `.buttonStyle(.automatic)` only. Do not put
  `.buttonStyle(.glass)` on toolbar items (glass-on-glass Liquid Glass bug).
- Pre-iOS 26 fallback: 36pt capsule + 36pt circular + via
  `safeAreaInset`. Not the iPad FAB. Not `GlassEffectContainer`.
- iPad and visionOS keep the top magnifying glass overlay and the
  trailing FAB. Do not move those.
- Still dismiss sticky IME with `WWNHostKeyboard` on selection and
  column change.

## Hard rejects

- Custom glass capsule + oversized circular + (44/56pt) next to search on
  iOS 26 (or forcing `usesNativePhoneSearchToolbar = false` on 26+)
- `.buttonStyle(.glass)` on top-trailing toolbar items on iOS 26
- `DefaultToolbarItem(kind: .search)` **without** `ToolbarSpacer` before
  the compose + (search goes full-width and overlaps the button)
- Putting this chrome on iPad / visionOS
- Gray / secondary tint on the new-machine +
