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
  `ToolbarItem(placement: .bottomBar)` with a plain
  `Button { Image(systemName: "plus") }`. Default toolbar styling only.
  No custom circle fill, glassProminent, fixed frame, shadow, or
  `sharedBackgroundVisibility` hacks. System sizes the +.
- Top-trailing on phone: sort + Settings only. **Never** a second Add there.
  Exactly one `+` (bottom toolbar on phone).
- Top-trailing sort/Settings: `.buttonStyle(.automatic)` only
  (`glassToolbarButton`). Do not put `.buttonStyle(.glass)` on toolbar
  items (glass-on-glass Liquid Glass bug).
- Machine editor sheet toolbar: plain `ToolbarItem` leading `xmark` and
  trailing `checkmark`. Default system size/spacing. No custom circles,
  font weights, or shared-background overrides.
- Pre-iOS 26 fallback: 36pt capsule + 36pt circular + via
  `safeAreaInset` (sole phone Add on those OS versions). Not the iPad FAB.
  Not `GlassEffectContainer`.
- iPad and visionOS: top-trailing Add only (plus search overlay). Do not
  also put Add in a bottom bar on those hosts.
- Still dismiss sticky IME with `WWNHostKeyboard` on selection and
  column change.

## Hard rejects

- **Two Add Machine buttons** (top-trailing + bottom compose on phone)
- Custom opaque / glassProminent / fixed-frame FAB for iOS 26 toolbar Add
- Custom circle / padding / font weight on editor sheet xmark/checkmark
- `.buttonStyle(.glass)` on top-trailing toolbar items on iOS 26
- `DefaultToolbarItem(kind: .search)` **without** `ToolbarSpacer` before
  the compose + (search goes full-width and overlaps the button)
- Putting this chrome on iPad / visionOS
- Forcing `usesNativePhoneSearchToolbar = false` on iOS 26+
