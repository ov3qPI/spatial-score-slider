# Publishing Spatial Score Slider APK releases

Current release: **v1.0.0** (Android version name `1.0`, code `1`).

The release is built on the developer's Termux device using the existing source-only build layout and a dedicated persistent signing key. No APKs or keystores are committed.

## Release command

Run from an interactive Termux session with `git`, `gh`, `python`, `aapt2`, `javac`, `d8`, `apksigner`, `keytool`, `zipalign`, and Android SDK API 34+ installed:

```sh
(
set -e
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
gh repo clone ov3qPI/spatial-score-slider "$tmp/repo"
bash "$tmp/repo/Documents/sh/spatial_score_slider_publish_release_v20261024T051252Z.sh" "$tmp/repo"
)
```

On first use, choose and confirm a strong signing-key password. On subsequent releases, enter the same password. The private keystore is kept at `$HOME/.android/SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.p12`; back it up securely with the password. Losing either prevents ordinary signature-compatible Android updates.

The script compiles, zipaligns, release-signs, and verifies the APK, retaining `/storage/emulated/0/Documents/apk/SpatialScoreSlider_v1.0.0.apk`. It creates GitHub Release `v1.0.0` with that APK attached, after checking that the tag and release are unused. The temporary checkout and build intermediates are removed.

**Important:** An installed test APK signed with the earlier Android debug key cannot be updated in place with this release-signed APK. Uninstall the test version first, preserving any data you require. Future public releases must use this same release signing keystore.
