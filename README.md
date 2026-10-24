# Spatial Score Slider
**App name:** Spatial Score Slider (launcher and in-app title). Android package ID: `cc0.KPYQrT.spatialscoreslider`. This is a distinct application ID from both `com.example.spatialscore` and `cc0.spatialscoreslider`, so it installs separately from either.
An Android spatial scoring app reconstructed from the original APK and adapted for offline Termux builds.
## License
The original source code, build scripts, and authored resources in this repository are dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/). See [LICENSE](LICENSE) for the complete legal code. This dedication applies only to rights the affirmer is authorized to waive and does not override third-party rights.
## Behavior
A 0–100 slider keeps the score hidden until released. Tap the revealed number to copy it to the clipboard; use Reset to clear the score. The slider is aligned to the measured app-window vertical centerline, with a compact score display centered above it. The status bar uses the app's dark background (`#23201D`). Score 0 is orange (`#D68A3A`), and 100 is blue (`#4C7EA8`). The launcher icon is a native Android vector gradient.
## Source organization
The source files are stored under `Documents/java/`, `Documents/xml/`, `Documents/json/`, `Documents/py/`, and `Documents/md/`, matching the extension-based shared-storage layout used by this project. `Documents/json/SpatialScoreSlider_project_v20261024T050357Z.json` maps these original source filenames into a disposable Android build tree. Source identifiers retain their release timestamps.
## Build and install on Termux
Requirements: `python`, `aapt2`, `javac`, `d8`, `apksigner`, `keytool`, `zipalign`, `termux-open`, and Android SDK API 34+ `android.jar` (the existing setup uses API 35). With `gh` authenticated as `ov3qPI`, use:
```sh
(
set -e
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
gh repo clone ov3qPI/spatial-score-slider "$tmp/repo"
python "$tmp/repo/Documents/py/spatial_score_slider_build_v20261024T050357Z.py" --storage-root "$tmp/repo" --output-root /storage/emulated/0 --install
)
```
The builder temporarily stages Java and Android resources in Termux's private temporary directory. Compilation intermediates and the temporary checkout are deleted after the command completes, including on failure. The signed APK is retained at `/storage/emulated/0/Documents/apk/SpatialScoreSlider_rebuilt_v20261024T050357Z.apk`; the Android debug signing keystore remains in `$HOME/.android/debug.keystore` to support updates. No APK, signing key, or compiled artifact is tracked in Git.
## Implementation
The application targets minimum API 24 and target API 34, uses native Android widgets, and has no external runtime dependencies. Because it was reconstructed from a compiled APK, it does not preserve the original Java formatting or comments and may differ from the original Material Components appearance.
## Validation
Earlier versions built and installed successfully through Termux. This package-ID update has passed static source and staging checks but has not been compiled or installed on a device.

## Build directly from the downloaded source ZIP
Place the ZIP in `/storage/emulated/0/Documents/zip/` and execute:
```sh
(
set -e
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
unzip -q /storage/emulated/0/Documents/zip/SpatialScoreSlider_CC0_GitHub_source_v20261024T050817Z.zip -d "$tmp"
python "$tmp/Documents/py/spatial_score_slider_build_v20261024T050357Z.py" --storage-root "$tmp" --output-root /storage/emulated/0 --install
)
```
The extracted source and intermediate build directories are deleted even if compilation fails. The final signed APK and the original ZIP remain.

## Publish to GitHub as a new public repository
With `git`, `gh`, and `unzip` installed in Termux, authenticate `gh` as `ov3qPI`, then run this command using the source-only ZIP:
```sh
(
set -e
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
unzip -q /storage/emulated/0/Documents/zip/SpatialScoreSlider_CC0_GitHub_source_v20261024T050817Z.zip -d "$tmp"
bash "$tmp/Documents/sh/spatial_score_slider_publish_v20261024T050817Z.sh" "$tmp"
)
```
The publishing script requires a repository that does not yet exist, creates `ov3qPI/spatial-score-slider` as **public**, commits the source and CC0 license, and pushes `main`. It refuses to overwrite an existing repository. The temporary unpacked files are deleted afterward, including if publishing fails.

## GitHub Releases

See [RELEASING.md](RELEASING.md) for automated signing and release publication, including how to print and back up the keystore and password.
