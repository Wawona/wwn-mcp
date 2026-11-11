# CalVer today (fail closed)

Product builds require `VERSION` / `Cargo.toml` = today's CalVer `YY.M.D`
(America/Los_Angeles). Gate: `cargo xtask verify calver`.
Wired in `cargo xtask xcode prebuild` (every Xcode build, so `cargo xtask package` too). Escape:
`WAWONA_ALLOW_STALE_CALVER=1`. Rule: `wawona-calver-today`.
