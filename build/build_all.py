"""Orchestrator: runs the full build pipeline for a week.

Steps:
1. Parse word list
2. Generate images (placeholder by default)
3. Generate audio
4. Assemble site
"""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_step(name: str, cmd: list[str]) -> None:
    """Run a build step, exit on failure."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}\n")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\nERROR: {name} failed (exit code {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--title", required=True, help="Czech title for the week")
    parser.add_argument("--title-en", required=True, help="English title for the week")
    parser.add_argument("--input", required=True, type=Path, help="Path to word list file")
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation")
    parser.add_argument("--skip-audio", action="store_true", help="Skip audio generation")
    args = parser.parse_args()

    python = sys.executable

    # 1. Parse words
    run_step(
        "Parse words",
        [
            python,
            "build/parse_words.py",
            "--input",
            str(args.input),
            "--week",
            args.week,
            "--title",
            args.title,
            "--title-en",
            args.title_en,
        ],
    )

    # 2. Generate images
    if not args.skip_images:
        run_step(
            "Generate images",
            [python, "build/generate_images.py", "--week", args.week],
        )
    else:
        print("\n  Skipping image generation")

    # 3. Generate audio
    if not args.skip_audio:
        run_step(
            "Generate audio",
            [python, "build/generate_audio.py", "--week", args.week],
        )
    else:
        print("\n  Skipping audio generation")

    # 4. Build site
    run_step("Build site", [python, "build/build_site.py"])

    print(f"\n{'=' * 60}")
    print("  Done! Open site/index.html to preview.")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
