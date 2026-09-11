# Android Gradle JVM is JBR 21

Wawona Android Studio and local `./gradlew` use JetBrains Runtime 21
(Studio embedded JBR, IDE JDK name `21`). Linux Nix assemble uses
`jetbrains.jdk-no-jcef-21`. Darwin Nix sandbox cannot use nixpkgs JBR
(Linux-only platforms) and stays on OpenJDK; local Darwin still uses
Studio JBR via `gradlegen`.

Do not export Nix OpenJDK as `JAVA_HOME` into Android Studio. That
breaks sync (`Invalid Gradle JDK configuration`, `#GRADLE_LOCAL_JAVA_HOME`).

Helper: `Wawona/scripts/lib/android-jbr.sh`.
Rule: `wawona-android-jbr`.
Prose: `Wawona/docs/agent-rules/wawona-android-jbr.md`.
