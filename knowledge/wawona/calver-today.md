# CalVer today (fail closed)

Product builds require `VERSION` / `Cargo.toml` = today's CalVer `YY.M.D`
(America/Los_Angeles). Script: `Wawona/.github/scripts/verify-calver-today.sh`.
Wired in `xcode-prebuild.sh` and Mode B tipa packaging. Escape:
`WAWONA_ALLOW_STALE_CALVER=1`. Rule: `wawona-calver-today`.
