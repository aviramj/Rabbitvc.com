#!/usr/bin/env bash
# Downloads every image referenced in index.html from the live
# rabbitvc.com WordPress and zips them, mirroring the wp-content
# directory layout. Run from anywhere with internet + curl + zip.
#
# Usage:  bash tools/download-assets.sh
# Output: ./rabbitvc-assets/  and  ./rabbitvc-assets.zip

set -euo pipefail

OUT="rabbitvc-assets"
ZIP="rabbitvc-assets.zip"
HOST="https://rabbitvc.com"

PATHS=(
  # logos / favicons
  "wp-content/uploads/2023/07/rabbit.png"
  "wp-content/uploads/2023/08/cropped-rabbit-32x32.png"
  "wp-content/uploads/2023/08/cropped-rabbit-192x192.png"
  "wp-content/uploads/2023/08/cropped-rabbit-180x180.png"
  "wp-content/uploads/2024/08/rabbit-only-transparent-white-300x207.png"
  "wp-content/uploads/2024/08/rabbit-only-transparent-white-1024x707.png"

  # hero background (responsive sizes)
  "wp-content/uploads/2023/03/rabbit-website-background-image5-1-768x573.jpg"
  "wp-content/uploads/2023/03/rabbit-website-background-image5-1-1024x765.jpg"
  "wp-content/uploads/2023/03/rabbit-website-background-image5-1-1536x1147.jpg"
  "wp-content/uploads/2023/03/rabbit-website-background-image5-1-2048x1529.jpg"

  # Aviram Jenik
  "wp-content/uploads/2023/04/Aviram-Jenik-01_1-294x300.jpg"
  "wp-content/uploads/2023/04/Aviram-Jenik-01_1-768x784.jpg"
  "wp-content/uploads/2023/04/Aviram-Jenik-01_1-1002x1024.jpg"

  # MJ Kang
  "wp-content/uploads/2023/03/MJ-Kang-300x300.jpeg"
  "wp-content/uploads/2023/03/MJ-Kang-600x600.jpeg"
  "wp-content/uploads/2023/03/MJ-Kang-768x768.jpeg"

  # SK (Soo Keun) Lee
  "wp-content/uploads/2023/04/station_2957_1-266x300.jpg"
  "wp-content/uploads/2023/04/station_2957_1-768x866.jpg"
  "wp-content/uploads/2023/04/station_2957_1-908x1024.jpg"

  # Sun Cho
  "wp-content/uploads/2023/03/sun-cho-profile-225x300.jpg"
  "wp-content/uploads/2023/03/sun-cho-profile-600x800.jpg"
  "wp-content/uploads/2023/03/sun-cho-profile-768x1024.jpg"
)

rm -rf "$OUT" "$ZIP" "${ZIP%.zip}.tar.gz"
mkdir -p "$OUT"

ok=0; fail=0
for p in "${PATHS[@]}"; do
  mkdir -p "$OUT/$(dirname "$p")"
  printf "  %-70s " "$p"
  if curl -fsSL --retry 3 --max-time 60 \
       -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
       -o "$OUT/$p" "$HOST/$p"; then
    size=$(wc -c < "$OUT/$p" | tr -d ' ')
    printf "ok  (%s bytes)\n" "$size"
    ok=$((ok+1))
  else
    printf "FAIL\n"
    fail=$((fail+1))
  fi
done

echo
echo "Downloaded: $ok / ${#PATHS[@]}  (failed: $fail)"

if [ "$fail" -gt 0 ]; then
  echo "Some files failed; check the output above. Aborting." >&2
  exit 1
fi

if command -v zip >/dev/null 2>&1; then
  zip -qr "$ZIP" "$OUT"
  echo "Created $ZIP  ($(wc -c < "$ZIP" | tr -d ' ') bytes)"
else
  tar -czf "${ZIP%.zip}.tar.gz" "$OUT"
  echo "zip not found — created ${ZIP%.zip}.tar.gz instead"
fi
