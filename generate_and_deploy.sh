#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Generating images via API ==="
uv run python build/generate_images.py \
  --week 2026-W14 \
  --mode api \
  --force \
  --review

echo "=== Rebuilding site ==="
uv run python build/build_all.py \
  --week 2026-W14 \
  --title "Zvířata" \
  --title-en "Animals" \
  --input input/week-2026-W14.txt

echo "=== Committing and pushing ==="
git add -A
git commit -m "Generate real images for week 2026-W14 with image prompts"
git push

echo "=== Done ==="
