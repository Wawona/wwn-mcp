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
read `swiftui-pro` + `swiftui-expert-skill`. iOS 13 + `WawonaBackport` and
`wawona-apple-swift-glue` override upstream modernization advice.
