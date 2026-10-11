# Apple-mobile Mode A backends (least maintenance)

iOS family (not macOS): iOS / iPadOS / tvOS / watchOS / visionOS.
Deployment **13.0**, latest SDK. No per-OS backend forks (18→26 is marketing).

## Owners

| Need | Backend | Repo |
|------|---------|------|
| coreutils | uutils → `wawona_coreutils_main` | **wwn-coreutils** (`safe-subset.txt`, pin, patch) |
| SSH | libssh2 CLI | **wwn-ssh** |
| zsh | `wawona_zsh_main` in-process | **wwn-zsh** |
| `system()` | `wawona_dispatch_inprocess` | **wwn-toolchain** `wawona-pty` |

Wawona L4 links + SwiftUI only. Must use `wwn-coreutils.lib.coreutilsSrc` /
`mkPatchedSrc`; must not re-`fetchFromGitHub` uutils.

## Hard rejects

- NIOSSH / ios_system / Swift `Process` as product shell backends
- OpenSSH fork-exec on Apple-mobile store builds
- Real POSIX `system()` of unsigned Mach-O
- Mega App Store SDK owning every tool
- Raising min OS above 13.0 for convenience

## Patch budget

Pin hard. Prefer configure over patches. Anchor CI per `wwn-*`. See
`wwn-coreutils/docs/PATCH-BUDGET.md`.

## Verify

`Wawona/.github/scripts/verify-ios-shell-tools.py` (safe-subset sync + no
Swift shell imports).

Canonical rule: `Wawona/docs/agent-rules/wawona-apple-mobile-mode-a-backends.md`.
