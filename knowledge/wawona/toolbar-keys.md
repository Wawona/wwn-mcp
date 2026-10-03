# ToolbarKeys

L3′ crate at `github.com/Wawona/ToolbarKeys`.

Rootshell's keyboard toolbar (key catalog, drawer rows, custom sequences,
width overflow) lives here as Rust. UniFFI exports `ToolbarSession`.
`apple/Keyboard` is the UIKit drawing. Wawona compiles that directory
from this repo. The Wayland accessory bridge stays in Wawona. Do not
copy those Swift files back into the app.

iOS deployment target stays 13.0. Android uses the same JSON document.
`phone` and `pad` are the two default layouts (Rootshell version 14).

Wawona may depend on this crate. This crate does not depend on Wawona,
Ghostty, or iland.

Do not grow the Rootshell SwiftUI toolbar inside the Wawona app as the owner.
