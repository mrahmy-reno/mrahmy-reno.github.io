#!/usr/bin/env bash
# Copies the owner-approved likeness (DIRECTIVE #3 / owner Q6) and rasterises the locally
# generated favicon + Open Graph card with headless Chrome. No external service is contacted.
set -euo pipefail
# B1-05 / D-01 repair: operate on the checkout this script lives in, not on a hardcoded authoring
# path (asset regeneration must never mutate someone else's working copy).
cd "$(dirname "$0")/.."

SRC_PHOTO=/root/company/BENCHMARK_01/sources/linkedin_profile_photo_400.jpg
EXPECT_SHA=be1dc0c63f05f60564fa83c4f5abab3f8a8efe69de2211eda66cf814548c89be

echo "== profile photo =="
echo "source: ${SRC_PHOTO}"
sha256sum "${SRC_PHOTO}"
echo "${EXPECT_SHA}  ${SRC_PHOTO}" | sha256sum -c - || { echo "PHOTO HASH MISMATCH"; exit 1; }
cp -f "${SRC_PHOTO}" docs/assets/profile.jpg
sha256sum docs/assets/profile.jpg
ls -l docs/assets/profile.jpg

CHROME=/usr/bin/google-chrome
echo "== chrome version =="
"${CHROME}" --version

raster() { # svg out width height
  "${CHROME}" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --force-device-scale-factor=1 --default-background-color=00000000 \
    --window-size="$3,$4" --screenshot="$2" "$1" >/dev/null 2>&1 || true
  ls -l "$2" 2>/dev/null || { echo "FAILED to rasterise $1 -> $2"; return 1; }
}

echo "== og-image (1200x630) =="
raster "file://$(pwd)/tools/og-image.svg" "$(pwd)/docs/assets/og-image.png" 1200 630

echo "== favicon 32x32 =="
raster "file://$(pwd)/tools/favicon.svg" "$(pwd)/docs/assets/favicon-32.png" 32 32

echo "== apple-touch-icon 180x180 =="
raster "file://$(pwd)/tools/favicon.svg" "$(pwd)/docs/assets/apple-touch-icon.png" 180 180

echo "== file types =="
file docs/assets/og-image.png docs/assets/favicon-32.png docs/assets/apple-touch-icon.png
