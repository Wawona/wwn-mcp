# Android Gradle JVM is JBR 21

Wawona Android Studio and local `./gradlew` use JetBrains Runtime 21
(Studio embedded JBR, IDE JDK name `21`). CI installs JBR 21 with
`actions/setup-java` (distribution `jetbrains`) in `setup-xtask`. Nix builds
only the `.#deps-android` slice and runs no Gradle.

Do not export Nix OpenJDK as `JAVA_HOME` into Android Studio. That
breaks sync (`Invalid Gradle JDK configuration`, `#GRADLE_LOCAL_JAVA_HOME`).

Resolver: `cargo xtask build android` (`xtask/src/product.rs`).
Rule: `wawona-android-jbr`.
Prose: `Wawona/docs/agent-rules/wawona-android-jbr.md`.
