#!/usr/bin/env bash
# Deploy site/ to the gh-pages branch.
#
# Usage:
#   bash build/deploy.sh
#
# This script:
# 1. Verifies site/ exists and is non-empty
# 2. Copies latest templates into site/
# 3. Creates/updates the gh-pages branch with site/ contents
# 4. Pushes to origin
# 5. Prints the live GitHub Pages URL

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SITE_DIR="$PROJECT_DIR/site"
TEMPLATES_DIR="$PROJECT_DIR/templates"

# --- Step 1: Verify site directory ---
if [ ! -d "$SITE_DIR" ] || [ -z "$(ls -A "$SITE_DIR")" ]; then
    echo "ERROR: site/ directory is empty or missing. Run the build first."
    exit 1
fi

# --- Step 2: Copy latest templates into site/ ---
echo "[deploy] Copying templates to site/..."
cp "$TEMPLATES_DIR/index.html" "$SITE_DIR/index.html"
cp "$TEMPLATES_DIR/style.css" "$SITE_DIR/style.css"
cp "$TEMPLATES_DIR/app.js" "$SITE_DIR/app.js"

echo "[deploy] Deploying $SITE_DIR to gh-pages..."

cd "$PROJECT_DIR"

# Get the remote URL to construct the Pages URL
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

# --- Step 3: Create a temporary worktree for gh-pages ---
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Check if gh-pages branch exists on remote
if git ls-remote --heads origin gh-pages | grep -q gh-pages; then
    git fetch origin gh-pages
    git worktree add "$TMPDIR" origin/gh-pages --detach 2>/dev/null || true
    cd "$TMPDIR"
    git checkout -B gh-pages
else
    git worktree add --orphan "$TMPDIR" gh-pages 2>/dev/null || {
        # Fallback for older git: create orphan manually
        git worktree add "$TMPDIR" --detach 2>/dev/null || true
        cd "$TMPDIR"
        git checkout --orphan gh-pages
    }
    cd "$TMPDIR"
fi

# --- Step 4: Replace contents with site/ ---
# Remove all existing files
git rm -rf . 2>/dev/null || true
find . -not -path './.git*' -not -path '.' -delete 2>/dev/null || true

# Copy site contents
cp -r "$SITE_DIR"/. .

# Add and commit
git add -A
if git diff --cached --quiet; then
    echo "[deploy] No changes to deploy."
else
    git commit -m "deploy: update site $(date +%Y-%m-%d_%H:%M:%S)"
fi

# --- Step 5: Push ---
git push origin gh-pages --force

cd "$PROJECT_DIR"
git worktree remove "$TMPDIR" 2>/dev/null || true

# --- Step 6: Print URL ---
if echo "$REMOTE_URL" | grep -q "github.com"; then
    # Extract owner/repo from URL
    REPO_PATH=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/](.*)\.git$|\1|; s|.*github\.com[:/](.*)$|\1|')
    OWNER=$(echo "$REPO_PATH" | cut -d'/' -f1)
    REPO=$(echo "$REPO_PATH" | cut -d'/' -f2)
    echo ""
    echo "Site deployed!"
    echo "URL: https://${OWNER}.github.io/${REPO}/"
else
    echo ""
    echo "Site deployed to gh-pages branch."
fi
