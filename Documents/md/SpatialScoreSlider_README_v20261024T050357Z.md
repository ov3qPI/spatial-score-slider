# Spatial Score Slider — centered layout, vector gradient icon, source-only Termux project
Version: `20261024T050357Z`
Application name: `Spatial Score Slider`
Application ID: `cc0.KPYQrT.spatialscoreslider` (new identity; distinct from `com.example.spatialscore` and `cc0.spatialscoreslider`)
Source recovered from original `spatial-score-slider.apk`, with UI adjustments.
## UI changes
The status bar and optional navigation bar are dark `#23201D` with light system icons. A layout-change listener recomputes the centerline as one-half of the measured app window height, places the slider's vertical midpoint at that line, and centers a compact CURRENT VALUE display above it. The heading remains top-aligned and Reset remains at the bottom. Color mapping: 0 is orange `#D68A3A`, 100 is blue `#4C7EA8`. The hidden-until-release behavior, score copying, reset, and 0–100 scale are unchanged.
## Launcher icon
The launcher icon is an Android VectorDrawable consisting of one full-square horizontal gradient, from orange `#D68A3A` at 0 on the left to blue `#4C7EA8` at 100 on the right. `AndroidManifest.xml` references it as both `android:icon` and `android:roundIcon`. No PNG, SVG, or prebuilt APK is needed.
## Build and install
Save this ZIP to `/storage/emulated/0/Documents/zip/SpatialScoreSlider_CC0_GitHub_source_v20261024T050817Z.zip` then run in Termux:
```sh
(
set -e
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
unzip -q /storage/emulated/0/Documents/zip/SpatialScoreSlider_CC0_GitHub_source_v20261024T050817Z.zip -d "$tmp"
python "$tmp/Documents/py/spatial_score_slider_build_v20261024T050357Z.py" --storage-root "$tmp" --output-root /storage/emulated/0 --install
)
```
The signed output is `/storage/emulated/0/Documents/apk/SpatialScoreSlider_rebuilt_v20261024T050357Z.apk`. The ZIP includes only the Java application source, XML resources (including the vector icon), the JSON source-path manifest, Python Termux builder, and README. There is no prebuilt APK, DEX, JAR, or other build artifact. Unpacked files and intermediate artifacts are removed whether building succeeds or fails; the signed APK, source ZIP, and persistent debug keystore are retained.
## Requirements
Termux packages for `python`, `unzip`, `aapt2`, `javac`, `d8`, `apksigner`, `keytool`, `termux-open`; Android SDK API 34+ `android.jar`. The installer requires on-device confirmation.
The reconstruction uses native Android widgets with no external network dependencies; some UI details differ from the original AndroidX app. Matching signing credentials are required when upgrading an already-installed app with the same application ID.
## Verification
XML parsing, icon references, source manifest coverage, Python syntax, staging, and ZIP integrity were checked. Android build and installation must be verified on-device.

## CC0 1.0 Universal
This project is dedicated to the public domain under CC0 1.0 Universal, to the extent the affirmer owns the relevant rights. The complete legal code is in the repository-root `LICENSE` file.
