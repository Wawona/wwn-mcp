# Machine card action chips (Focus / Stop / Edit / Delete)

Indexed summary. Incident 2026-10-13: iPhone Machines grid clipped Delete
(and sometimes Edit) off the bottom of the running-machine card.

## Root cause

`MachineActionBar` used `ViewThatFits` with a single-line `HStack` first and
`MachineActionFlow` second. Under `LazyVGrid`, the Flow often measured with
**nil / infinite width**, so `sizeThatFits` reported **one-row height**. At
place time the same chips **wrapped** onto a second row. The card frame was
locked to the one-row height and **clipped** the overflow.

## Fix (keep)

1. Always use `MachineActionFlow` for `.flow` (no `ViewThatFits` HStack).
2. `resolvedMaxWidth`: when proposal width is unknown, assume ~2 chips per
   line for 3-4 actions so measurement height includes wrap.
3. `WWNMachineCardView`: `.fixedSize(horizontal: false, vertical: true)`
   before `.frame(maxHeight: .infinity)` so the grid row grows with content.

## Code

- `Wawona/Sources/WawonaUI/Machines/MachineActionBar.swift`
- `Wawona/Sources/WawonaUI/Machines/WWNMachineCardView.swift`

## Hard rejects

- Restoring `ViewThatFits(HStack)` for card actions without finite-width
  measure that matches place height
- Treating nil proposal width as infinity in wrap `Layout.sizeThatFits`
- Truncating or omitting Delete/Edit to keep one row

Rule: `wawona-machine-card-actions`. Skill: `wawona-machine-card-actions`.
Related: `wawona-machine-types`, `wawona-apple-swift`,
`ios-iphone-machines-messages-chrome.md`.
