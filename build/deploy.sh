#!/usr/bin/env bash
# Deploy site/ to the gh-pages branch.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SITE_DIR="$PROJECT_DIR/site"

if [ ! -d "$SITE_DIR" ] || [ -z "$(ls -A "$SITE_DIR")" ]; then
    echo "ERROR: site/ directory is empty or missing. Run the build first."
    exit 1
fi

echo "[deploy] Deploying $SITE_DIR to gh-pages..."

cd "$PROJECT_DIR"

# Get the remote URL to construct the Pages URL
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

# Deploy using git subtree push
git subtree push --prefix site origin gh-pages

# Print the URL
if echo "$REMOTE_URL" | grep -q "github.com"; then
    # Extract owner/repo from URL
    REPO_PATH=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/](.*)\.git$|\1|; s|.*github\.com[:/](.*)$|\1|')
    OWNER=$(echo "$REPO_PATH" | cut -d'/' -f1)
    REPO=$(echo "$REPO_PATH" | cut -d'/' -f2)
    echo ""
    echo "Site deployed! URL: https://${OWNER}.github.io/${REPO}/"
else
    echo ""
    echo "Site deployed to gh-pages branch."
fi
