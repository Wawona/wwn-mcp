# Machine Start placement (Prompt / Tab / Window)

Indexed summary. Machines Start respects Display → Default Start Type
(`prompt` | `newTab` | `newWindow`) only when the host can open another
window. Otherwise always New Tab.

## Gates

- macOS / visionOS / iPad (multi-scene) / Android API 24+: windowed Start OK
- iPhone / tvOS / watchOS / Linux / Android pre-N: tab only, setting hidden
- iPadOS 26 is **not** the multi-window floor (scenes older; 26 = window chrome)

## UX

- Prompt: macOS `NSAlert`; iOS/iPad/visionOS action sheet; Android dialog
- New Window: dedicated session `NSWindow` / `UIWindowScene` / `SessionActivity`
- In-window session return: sidebar Machines (no floating Machines button)

## Code

`MachineStartPlacement`, `WWNMachinesViewModel.beginStart`,
`WWNSessionWindowPresenter`, `MainActivity.beginMachineStart`.
Rule: `docs/agent-rules/wawona-machine-start-placement.md`.
