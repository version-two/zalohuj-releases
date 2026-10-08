# Zálohuj.sk – desktop client releases

Installers for the Zálohuj.sk backup client. Every release carries the same version on all platforms, `1.0.0+N`, where `N` is the build number; the release tag is `v1.0.0+N` and file names use `1.0.0.N`. Source lives in a private repository; this repository holds binaries, checksums and the signed update manifest.

| Platform | File | Notes |
|---|---|---|
| Windows 10/11 x64 | `Zalohuj-1.0.0.N-windows-x86_64-setup.exe` | NSIS installer, also served at https://zalohuj.sk/storage/release/latest/ |
| macOS 12+ Apple Silicon | `Zalohuj-1.0.0.N-darwin-aarch64.dmg` | `.app.tar.gz` is the updater asset |
| macOS 12+ Intel | `Zalohuj-1.0.0.N-darwin-x86_64.dmg` | |
| Linux x86_64 | `Zalohuj-1.0.0.N-linux-x86_64.AppImage`, `.deb` | AppImage self-updates; `.deb` installs are notified only |
| Linux aarch64 | `Zalohuj-1.0.0.N-linux-aarch64.AppImage`, `.deb` | |

`SHA256SUMS` lists every asset. `latest.json` is the update manifest: the client verifies each entry against an Ed25519 public key compiled into the binary, so a tampered asset or manifest is rejected before installation.

Releases are produced by Version Two's CI: Windows by TeamCity, macOS and Linux by the workflow in `.github/workflows/release.yml`, which is dispatched by that TeamCity build with the version it minted.

Version Two s.r.o., https://www.versiontwo.sk
