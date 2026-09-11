# Relay iOS Hypervisor (Mode B)

Canonical: `Wawona/docs/relay-ios-hypervisor.md`.
Rule: `wawona-relay-ios-hypervisor`. Repo: `github.com/Wawona/Relay`.

Native Hypervisor.framework for Mode B iOS/iPadOS **VM and container-in-VM**
only. Window: kernel HV on iOS/iPadOS **14.0–16.3.1**, public SoCs **M1 / M2 /
A16**. A12Z capable, not public. 16.4+ removed. Store IPA forbidden.

Resolve: Mode A → StaticCpu. Mode B + probe → IosHv. Wasm → Pulley. macOS
product VM → Virtualization.framework (macOS HV lab-only).

Not QEMU. Not HVF-via-qemu. Not UTM-as-product. No Settings HV toggle.
`vphone` / iOS 26 are not HV proof devices.
