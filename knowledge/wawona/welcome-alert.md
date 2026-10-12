# Welcome alert (all products)

First-launch welcome is one native alert over Machines on Apple, Android, and
Linux. Never a full-screen Welcome page.

Exact copy (Rust `Wawona/src/domain/welcome_copy.rs`):

- Title: `Welcome to Wawona`
- Message: `A Universal Wayland Compositor. Tap '+' to add a Machine.`
- Dismiss: `Continue`

Exports: C `wawona_welcome_*`, UniFFI `welcome_*`, Apple `WelcomeCopy`,
Android `WelcomeCopy.kt`, Linux `maybe_show_welcome`. Gate: unseen and empty
Machines list. Apple syncs `HasSeenWelcome` / `hasSeenWelcome` aliases on save.

Rule: `wawona-welcome-alert`. Docs: `Wawona/docs/agent-rules/wawona-welcome-alert.md`.
