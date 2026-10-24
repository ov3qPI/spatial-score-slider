SCRIPT_ID='spatial_score_slider_publish_v20261024T050817Z'
set -eu
root="${1:?Expected extracted repository root directory}"
cd "$root"
command -v git >/dev/null || { echo 'git is missing; run pkg install git'; exit 1; }
command -v gh >/dev/null || { echo 'gh is missing; run pkg install gh'; exit 1; }
gh auth status >/dev/null 2>&1 || gh auth login
login="$(gh api user --jq .login)"
[ "$login" = 'ov3qPI' ] || { echo "GitHub account mismatch: $login (expected ov3qPI)"; exit 1; }
if gh repo view ov3qPI/spatial-score-slider >/dev/null 2>&1; then echo 'Repository already exists: no files pushed; refusing to overwrite existing history'; exit 1; fi
git init -b main
git add -A
userid="$(gh api user --jq .id)"
git -c user.name="$login" -c user.email="${userid}+${login}@users.noreply.github.com" commit -m 'Initial CC0 source release'
gh repo create ov3qPI/spatial-score-slider --public --description 'Spatial Score Slider Android app: source-only, CC0 1.0 Universal, offline Termux build' --source=. --remote=origin --push
printf '%s\n' 'Published https://github.com/ov3qPI/spatial-score-slider'
