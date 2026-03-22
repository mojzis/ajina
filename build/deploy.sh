#!/usr/bin/env bash
# Deploy site/ to the gh-pages branch.
# TODO: Implement in Phase 5

set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)/site"

if [ ! -d "$SITE_DIR" ] || [ -z "$(ls -A "$SITE_DIR")" ]; then
    echo "ERROR: site/ directory is empty or missing. Run the build first."
    exit 1
fi

echo "[deploy] Would deploy $SITE_DIR to gh-pages"
echo "  TODO: Implement deployment (gh-pages push or GitHub Action)"
