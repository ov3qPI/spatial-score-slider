SCRIPT_ID='spatial_score_slider_publish_release_v20261024T051252Z'
set -eu
repo="${1:?Expected cloned source repository path}"
release='v1.0.0'
remote='ov3qPI/spatial-score-slider'
command -v gh >/dev/null || { printf '%s\n' 'Install GitHub CLI first: pkg install gh'; exit 1; }
command -v python >/dev/null || { printf '%s\n' 'Install Python first: pkg install python'; exit 1; }
gh auth status >/dev/null 2>&1 || gh auth login
login="$(gh api user --jq .login)"
[ "$login" = 'ov3qPI' ] || { printf '%s\n' "GitHub account mismatch: $login"; exit 1; }
if gh release view "$release" --repo "$remote" >/dev/null 2>&1; then printf '%s\n' "Release $release already exists; refusing to replace it"; exit 1; fi
if gh api "repos/$remote/git/ref/tags/$release" >/dev/null 2>&1; then printf '%s\n' "Tag $release already exists; refusing to reuse it"; exit 1; fi
commit="$(git -C "$repo" rev-parse HEAD)"
python "$repo/Documents/py/spatial_score_slider_release_v20261024T051252Z.py" --repo-root "$repo" --output-root /storage/emulated/0
apk="/storage/emulated/0/Documents/apk/SpatialScoreSlider_${release}.apk"
[ -s "$apk" ] || { printf '%s\n' 'Signed APK missing or empty'; exit 1; }
notes="$(printf '%s\n' 'First public APK release of Spatial Score Slider.' '' 'Android package: cc0.KPYQrT.spatialscoreslider' 'Version: 1.0 (code 1), minimum Android 7.0 / API 24' 'Source license: CC0 1.0 Universal' 'Features: 0–100 scoring slider, centered score output, dark status bar, orange-to-blue gradient launcher icon, tap-to-copy, Reset.' '' 'Signed with the project’s dedicated release key. Test/debug-signed builds with the same package ID must be uninstalled before installing this release.')"
gh release create "$release" "$apk" --repo "$remote" --target "$commit" --title "Spatial Score Slider $release" --notes "$notes" --latest
sha256sum "$apk"
printf '%s\n' "Published https://github.com/$remote/releases/tag/$release" "Retained $apk and the release keystore in Termux private storage"
