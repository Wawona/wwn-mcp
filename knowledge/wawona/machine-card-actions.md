# Machines: select then act (detail-first)

Indexed summary. Machines grid cards are select-only. Start, Stop, Focus,
Edit, Delete, Tags, and Pin live on the machine detail screen.

Also covers the older incident 2026-10-13 (action chips clipped on the card
when they still lived on the grid): `MachineActionFlow` must not measure at
infinite width. That layout rule still applies **inside detail**.

## Contract

1. Tap / click a card → open machine detail.
2. No action chips on the card face.
3. tvOS (no context menu): Tags and Pin on detail.

| Host | Detail |
|---|---|
| Apple | `WWNMachineDetailView` via `detailMachineId` |
| watchOS | `QuickConnectView` |
| Android | `MachineDetailScreen` |
| Linux | Adw dialog from card click |

A11y: `wwn.machines.detail`, `wwn.machines.detail.back`.

## Detail action wrap (keep)

1. Always use `MachineActionFlow` for `.flow` (no `ViewThatFits` HStack).
2. `resolvedMaxWidth`: when proposal width is unknown, assume ~2 chips per
   line for 3-4 actions so measurement height includes wrap.
3. tvOS / watchOS: `.stack`.

## Appearance

Each machine card keeps a visible one-point outline in both appearances.
macOS uses the system separator, iOS/iPadOS use `Color.primary` at 16%/28%,
Android uses `outlineVariant`.

## Hard rejects

- Action chips on grid cards
- Tags/Pin only via context menu on tvOS
- Nested `NavigationStack` on macOS split for detail
- Restoring `ViewThatFits(HStack)` for detail action wrap without finite width
- Truncating or omitting Delete/Edit to keep one row

Rule: `wawona-machine-card-actions`. Skill: `wawona-machine-card-actions`.
Related: `wawona-machine-types`, `wawona-apple-swift`.
