# Mission-critical assurance

All Wawona organization repositories use a shared quality baseline plus
repository-specific gates. GitHub organization security enables dependency
graph, Dependabot alerts, CodeQL default setup, secret scanning, push
protection, validity checks, non-provider patterns, extended metadata, and
private vulnerability reporting for current and future repositories.

The shared workflow validates changed files, parses changed data and scripts,
checks root Rust workspace formatting when Rust changes, inventories dependency
locks with OSV, reviews new pull-request dependencies, and rejects high-severity
zizmor findings in changed GitHub Actions workflows. Existing security debt is
visible; new high-severity dependency additions are blocked.

Assurance is risk-tiered. Tier 3 covers VM memory, MMU, CPU, virtio, privilege,
watchdog, and display ownership. Each obligation names production Rust,
preconditions, postconditions, a Kani harness, a Verus model when tractable,
negative tests, and remaining unproved behavior. Never claim whole-product or
flaw-free proof.

Wawona adopts the LAWs concept as named Rust contracts and proof obligations.
It does not add Bend-2-generated C product code. Generated C would violate
Rust-first and create a second implementation outside the shared Kani, Verus,
and Miri semantics. Miri cannot execute linked C, and Kani does not prove C via
a Rust extern declaration.

Canonical: `Wawona/docs/mission-critical-assurance.md`. Skill:
`wawona-mission-critical`.
