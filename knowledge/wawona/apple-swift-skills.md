# Apple Swift / SwiftUI skills (mandatory)

Wawona Apple compositor host UI requires installed Swift/SwiftUI agent skills.

## Personal skills (operator machine)

| Skill | Upstream |
|-------|----------|
| `swiftui-pro` | twostraws/swiftui-agent-skill |
| `swiftui-expert-skill` | AvdLee/SwiftUI-Agent-Skill |
| `swift-concurrency-pro` | twostraws/Swift-Concurrency-Agent-Skill |
| `swift-concurrency` | AvdLee/Swift-Concurrency-Agent-Skill |
| `swift-testing-pro` | twostraws/Swift-Testing-Agent-Skill |
| `swift-testing-expert` | AvdLee/Swift-Testing-Agent-Skill |

Install with `npx skills@latest add … -g -a cursor -y`. Paths:
`~/.agents/skills/<name>` and optionally `~/.cursor/skills/<name>` symlinks.

## Wawona gate

Skill `wawona-apple-swift`. Rule `wawona-apple-swift-skills` (alwaysApply).
Before editing `Sources/WawonaApple`, `WawonaUI`, `WawonaWatch`, or `Darwin/`,
read `swiftui-pro` + `swiftui-expert-skill`. iOS 15 + `WawonaBackport` and
`wawona-apple-swift-glue` override upstream modernization advice.

## tvOS focus findings (2026-11-05)

- `.buttonStyle(.plain)` drops the tvOS focus platter. A focused control then
  looks identical to an unfocused one. Use a custom `ButtonStyle` whose body
  reads `@Environment(\.isFocused)` (`WWNTvCapsuleButtonStyle`,
  `WWNTvRowButtonStyle`, `WWNTvSwatchButtonStyle`, `WWNTvChipButtonStyle`).
- `Color.secondary` / `foregroundColor(.secondary)` stays light gray on the
  white focus platter (illegible). Use hierarchical `.foregroundStyle(.secondary)`.
- `ViewThatFits` / `WawonaFittingRow` re-measures under the focus scale and
  rows jump between layouts. Use a fixed `HStack` on tvOS.
- Grids and horizontal strips clip the focus lift. Add padding and
  `.scrollClipDisabled()`.
- Up from the first row cannot reach toolbar Save / Done unless content is a
  `.focusSection()`. Do not use overscan margins on tvOS forms.
- Toolbar `.searchable` toggled on a split detail stacks a second search bar
  and filters the grid behind it. tvOS Machines search is a dedicated cover
  with a local query; Done clears it.
- Settings Done sits `.topBarTrailing` on the detail column only.
