"""Generate illustrations for each word in a week.

Supports two modes:
- placeholder (default): generates simple SVG placeholders
- api: uses Replicate API with SDXL-lineart model (same as ../esl)
"""

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STYLE_PREFIX = """A lovely hand-drawn illustration in the style of a vintage natural history atlas.
Black ink contours with soft, warm watercolor fills. Clean white background.
Simple, charming, suitable for educational materials for children.
Single subject, centered, no text in the image."""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--force", action="store_true", help="Regenerate existing images")
    parser.add_argument(
        "--mode",
        choices=["placeholder", "api"],
        default="placeholder",
        help="Generation mode (default: placeholder)",
    )
    parser.add_argument("--regenerate", help="Regenerate specific words only (comma-separated)")
    args = parser.parse_args()

    # TODO: Implement in Phase 3 (placeholder) and Phase 4 (api)
    print(f"[generate_images] Would generate images for week {args.week}")
    print(f"  Mode: {args.mode}")
    print(f"  Force: {args.force}")
    if args.regenerate:
        print(f"  Regenerate only: {args.regenerate}")

    output_dir = PROJECT_ROOT / "site" / "assets" / "images" / f"week-{args.week}"
    print(f"  Output: {output_dir}")


if __name__ == "__main__":
    main()
