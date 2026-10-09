# Android Kotlin / Jetpack Compose skills (mandatory)

Wawona Android host UI requires installed Compose/Android agent skills.

## Personal skills (operator machine)

| Skill | Upstream |
|-------|----------|
| `compose-agent`, `jetpack-compose-audit` | hamen/compose_skill |
| `modern-jetpack-compose` | anhvt52/jetpack-compose-skills |
| `edge-to-edge`, `styles`, `navigation-3`, `migrate-xml-views-to-jetpack-compose`, `testing-setup` | android/skills |
| `compose-ui-testing-patterns`, `compose-focus-navigation`, `compose-animations`, `kotlin-concurrency-and-flow`, `using-chrisbanes-skills` | chrisbanes/skills |
| `mobile-android-design` | wshobson/agents |
| `android-kotlin` | alinaqi/maggy |

Install with `npx skills@latest add … -g -a cursor -y`. Paths:
`~/.agents/skills/<name>` and optionally `~/.cursor/skills/<name>` symlinks.

## Wawona gate

Skill `wawona-android-compose`. Rule `wawona-android-compose-skills`
(alwaysApply). Before editing `android/app` Compose, read `compose-agent` +
`modern-jetpack-compose`. Material 3 Expressive is Android 16+ only. In-app
`SettingsDialog` only. Rust owns product policy.
