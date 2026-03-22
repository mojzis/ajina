"""Assemble the final static site from templates and generated assets.

Copies templates to site/, verifies all referenced assets exist,
and reports any missing files.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def copy_templates(templates_dir: Path, site_dir: Path) -> None:
    """Copy template files (HTML, CSS, JS) to the site directory."""
    for filename in ["index.html", "style.css", "app.js"]:
        src = templates_dir / filename
        dst = site_dir / filename
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Copied {filename}")
        else:
            print(f"  WARNING: Template not found: {src}", file=sys.stderr)


def verify_assets(site_dir: Path) -> tuple[list[str], list[str]]:
    """Verify all referenced assets exist. Returns (complete, missing) word lists."""
    data_dir = site_dir / "data"
    index_path = data_dir / "index.json"

    if not index_path.exists():
        print("  WARNING: No index.json found", file=sys.stderr)
        return [], []

    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    complete: list[str] = []
    missing: list[str] = []

    for week_info in index_data.get("weeks", []):
        week_id = week_info["week_id"]
        week_path = data_dir / f"week-{week_id}.json"

        if not week_path.exists():
            missing.append(f"week-{week_id}.json")
            continue

        week_data = json.loads(week_path.read_text(encoding="utf-8"))
        week_dir = data_dir / week_id

        for word in week_data.get("words", []):
            word_label = f"{week_id}/{word['english']}"
            missing_assets: list[str] = []

            # Check image
            image_path = week_dir / word["image"]
            if not image_path.exists():
                missing_assets.append(word["image"])

            # Check audio files
            for audio_key in ["audio_cs", "audio_en"]:
                audio_path = week_dir / word[audio_key]
                if not audio_path.exists():
                    missing_assets.append(word[audio_key])

            if missing_assets:
                missing.append(f"{word_label} (missing: {', '.join(missing_assets)})")
            else:
                complete.append(word_label)

    return complete, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Open site in browser after build")
    args = parser.parse_args()

    templates_dir = PROJECT_ROOT / "templates"
    site_dir = PROJECT_ROOT / "site"
    site_dir.mkdir(parents=True, exist_ok=True)

    print("[build_site] Assembling site")
    print(f"  Templates: {templates_dir}")
    print(f"  Output: {site_dir}")

    # Copy templates
    copy_templates(templates_dir, site_dir)

    # Verify assets
    complete, missing = verify_assets(site_dir)

    print("\n  Asset report:")
    print(f"    Complete: {len(complete)} words")
    if complete:
        for item in complete:
            print(f"      {item}")

    if missing:
        print(f"    Missing: {len(missing)} items")
        for item in missing:
            print(f"      {item}")
    else:
        print("    Missing: 0 items")

    print(f"\n  Site assembled at: {site_dir}")

    if args.preview:
        try:
            subprocess.Popen(  # noqa: S603
                [sys.executable, "-m", "http.server", "8000", "--directory", str(site_dir)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("  Preview server started at http://localhost:8000")
        except Exception as e:
            print(f"  Could not start preview server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
