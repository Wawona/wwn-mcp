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
  `ToolbarItem(placement: .bottomBar)` with `Image(systemName: "plus")`,
  `.backport.composeCircleButton()` (`.labelStyle(.iconOnly)` +
  `.glassProminent` + `.circle` + accent tint),
  `.sharedBackgroundVisibility(.hidden)`.
  Blue filled compose bubble (not a bare + glyph). Toolbar `Label` often
  drops the circle. No custom capsule. No fixed 44/56pt frame on the +.
  System sizes search and + to the same bottom chrome.
- Top-trailing on phone: sort + Settings only. **Never** a second Add there.
  Exactly one `+` (bottom compose on phone).
- Top-trailing sort/Settings: `.buttonStyle(.automatic)` only. Do not put
  `.buttonStyle(.glass)` on toolbar items (glass-on-glass Liquid Glass bug).
- Pre-iOS 26 fallback: 36pt capsule + 36pt circular + via
  `safeAreaInset` (sole phone Add on those OS versions). Not the iPad FAB.
  Not `GlassEffectContainer`.
- iPad and visionOS: top-trailing Add only (plus search overlay). Do not
  also put Add in a bottom bar on those hosts.
- Still dismiss sticky IME with `WWNHostKeyboard` on selection and
  column change.

## Hard rejects

- **Two Add Machine buttons** (top-trailing + bottom compose on phone)
- Custom glass capsule + oversized circular + (44/56pt) next to search on
  iOS 26 (or forcing `usesNativePhoneSearchToolbar = false` on 26+)
- `.buttonStyle(.glass)` on top-trailing toolbar items on iOS 26
- `DefaultToolbarItem(kind: .search)` **without** `ToolbarSpacer` before
  the compose + (search goes full-width and overlaps the button)
- Putting this chrome on iPad / visionOS
- Gray / secondary tint on the new-machine +
- Accent tint alone on Add (blue foreground / no filled background)
