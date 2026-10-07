# Physical-iPhone CarPlay developer lab

Canonical docs: Wawona/docs/carplay-lab.md.
Implementation: Wawona/scripts/carplay/main.rs and carplay.nix.

macOS `nix run .#carplay` builds a pinned Playport receiver and browser,
privately imports the upstream-documented experimental DiPlay identity, then
prompts for Wi-Fi details and launches. Subcommands: setup, doctor, scan,
pair ADDRESS, run [FLAGS]. Bluetooth pairing confirmation is manual.

All credentials/runtime state live outside Git at ~/.playport/wawona-lab.
Never index, print, attach, or redistribute that directory or identity APK.
Nix contains only helper source and tools. Wi-Fi password uses hidden input
and a private Java argument file, unlinked before JVM launch and read through
an inherited descriptor, not process argv. Never share runtime files. Viewer URL is
also a credential. No automatic credential uploads or Git mutations.

Wawona's existing WWNCarPlaySceneDelegate is dormant without Apple-granted
CarPlay entitlement and matching signing profile. Playport does not provide
that entitlement. Physical phone session remains unproved until connected.
Wireless only; upstream Bluetooth bridge requires macOS. Separate from vphone.

Bluetooth scan completion may stall during macOS name resolution. Rust launcher
bounds scan to 15 seconds and proceeds to address prompt with printed results.
Pairing has a 75-second failure timeout. Restart older stalled launcher, or
pair ADDRESS directly. Verify iPhone address in General > About > Bluetooth.

Default command now opens a Rust terminal UI with arrow-key menu, live selectable
scan results, pairing code, masked Wi-Fi input, start/stop receiver, and O to
open viewer. Q/Ctrl+C restore terminal and stop JVM via graceful termination.
Viewer token stays in memory and is not displayed. Selected phone address is
private and explicitly passed to receiver. CLI subcommands remain available.

Pairing regression: never swallow helper stderr or treat cancellation as success.
Capture final stdout/stderr after fast exit. Keep success/failure visible until
acknowledged; save phone only on success. Main menu: Pair iPhone, Start/Stop
CarPlay, Open viewer, Help, Quit. Manual address/rescan live inside Pair iPhone.
