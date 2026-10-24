# Publishing Spatial Score Slider APK releases
The first release is **v1.0.0** (Android version name `1.0`, version code `1`). The Android package is `cc0.KPYQrT.spatialscoreslider` and source is under CC0 1.0 Universal.
## Publish from Termux
Run this in Termux with the Android SDK, Java, `aapt2`, `d8`, `apksigner`, `git`, `gh`, and Python available:
```sh
(
set -e
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
gh repo clone ov3qPI/spatial-score-slider "$tmp/repo"
bash "$tmp/repo/Documents/sh/spatial_score_slider_publish_release_v20261024T052630Z.sh" "$tmp/repo"
)
```
On the first release build, the build script automatically generates a cryptographically random password and a new RSA signing key. It privately stores them under `$HOME/.android/` as files readable only by the Termux user. All subsequent builds reuse them automatically. The release builder will never overwrite an existing signing key. If an older signing key already exists without a saved password, it prompts once for the existing password to adopt it without changing the key.
Release APK: `/storage/emulated/0/Documents/apk/SpatialScoreSlider_v1.0.0.apk`. The GitHub Release receives the APK as an asset; no generated APK or secret is committed into the Git repository. Temporary checkouts and build artifacts are deleted.
## Print a complete signing backup
Run the dedicated export command from any checkout of this repository:
```sh
python Documents/py/spatial_score_slider_export_signing_v20261024T052630Z.py
```
It prints the password, keystore alias, SHA-256 checksum and a Base64 representation of the entire PKCS#12 keystore **including the signing private key**. Treat this output as highly sensitive. Plaintext notes, clipboard contents, screenshots and terminal scrollback can expose the credentials to others. Store the backup securely offline, or in encrypted password storage. Losing either password or keystore can prevent installing updates over the released app. Never commit the exported output to GitHub.
To restore the keystore from the Base64 block, concatenate only its Base64 lines and decode them into the listed `.p12` file. Restore the password as one line in its `.pass` file with access mode `0600`.
**Important:** Any existing debug-signed installation of the same Android package must be uninstalled before the release-signed APK is installed. Future releases must keep using the same signing key.
