# Mode A guest AOT (design target, not shipped)

Canonical: `Relay/docs/ios13-aot-assessment.md`.
Rule: `wawona-linux-vms-relay-runtime`. Skill: `wawona-relay`.
Proof: `wawona-formal-verification`.

Today's Mode A VM CPU is one StaticCpu thread. The design target is the
fastest App Store-safe ARM64 Linux VM in the smallest proved codebase.

Required shape, still store-safe: offline multi-threaded AOT of the bundled
guest, one host thread per guest vCPU, software TLB, signed indirect-branch
tables. The translator does not ship in the app. Translated code calls
StaticCpu's helpers. Kani and Verus refine that relation. StaticCpu remains
the oracle and the fallback for bytes outside the signed image.

No second CPU. No JIT. No `MAP_JIT`. No Hypervisor.framework in the store IPA.
No "world's fastest" or "cleanest" claim until that doc's measurements exist.
Hardware virtualization is a separate comparison class, not a reason to put
JIT in Mode A.
